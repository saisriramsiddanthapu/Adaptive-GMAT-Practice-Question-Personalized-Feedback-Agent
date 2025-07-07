import os
import logging
import traceback

from flask import Flask, request, jsonify
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field # Pydantic v2 is now used internally by LangChain 0.3.0+
from dotenv import load_dotenv

# --- Import specific LLM client you are using (now OpenAI for OpenRouter) ---
# Ensure you have 'langchain-openai' installed (pip install langchain-openai)
from langchain_openai import ChatOpenAI

# --- Configure logging to capture more details ---
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# --- Load your secret API key from the .env file ---
load_dotenv()
logging.debug(".env file loaded.")

app = Flask(__name__) # This sets up the web connection part

# --- Updated LLM Initialization for OpenRouter (DeepSeek) ---
# Initialize the LLM outside the route functions to avoid re-initializing on each request
try:
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    # Using your specific DeepSeek model name from .env
    openrouter_model_name = os.getenv("OPENROUTER_MODEL_NAME", "deepseek/deepseek-r1-0528-qwen3-8b:free")

    if openrouter_api_key:
        logging.debug(f"OPENROUTER_API_KEY loaded successfully. Starts with: {openrouter_api_key[:5]}...")
        # ChatOpenAI is used because OpenRouter provides an OpenAI-compatible API
        llm = ChatOpenAI(
            model=openrouter_model_name,
            openai_api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1" # This is OpenRouter's API endpoint
        )
        logging.debug(f"LLM initialized: {openrouter_model_name} via OpenRouter.")
    else:
        logging.error("OPENROUTER_API_KEY is NOT loaded. Check .env file and environment.")
        raise ValueError("OPENROUTER_API_KEY not found in environment. Please check .env file.")

except Exception as e:
    logging.critical(f"CRITICAL ERROR: Failed to initialize LLM model: {e}")
    traceback.print_exc()
    exit(1)


# --- These are like "blueprints" for the AI's answers ---
class QuestionOutput(BaseModel):
    question: str = Field(description="The GMAT-style math question text.")
    options: list[str] = Field(description="List of multiple-choice options (A, B, C, D, E).")
    answer: str = Field(description="The correct answer option (e.g., 'A', 'B', 'C', 'D', 'E' or the numeric value).")
    explanation: str = Field(description="Detailed step-by-step explanation of the solution.")

class FeedbackOutput(BaseModel):
    is_correct: bool = Field(description="True if the student's answer is correct, False otherwise.")
    feedback: str = Field(description="Personalized feedback for the student.")
    remediation_topic: str = Field(description="A specific topic for the student to review if incorrect (e.g., 'Algebra: Linear Equations').")


# --- 1. Question Generation Code (When Make.com asks for a question) ---
@app.route('/generate_question', methods=['POST'])
def generate_question():
    data = request.json
    topic = data.get('topic', 'Algebra')
    difficulty = data.get('difficulty', 'Medium')

    logging.debug(f"Received request for topic='{topic}', difficulty='{difficulty}'")
    try:
        with open('gmat_style_guide.txt', 'r') as f:
            gmat_style_guide = f.read()
        logging.debug(f"Successfully read gmat_style_guide.txt (length: {len(gmat_style_guide)} chars)")
    except FileNotFoundError:
        logging.error("gmat_style_guide.txt not found. Make sure it's in the same folder.")
        return jsonify({"error": "gmat_style_guide.txt not found. Make sure it's in the same folder."}), 500

    # This is the "brain's instructions" for generating a question
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert GMAT quantitative question designer.
         {gmat_style_guide}
         Generate a GMAT-style Multiple Choice question with 5 options (A, B, C, D, E).
         Focus on concise, clear language typical of GMAT.
         Ensure the question has one clear correct answer.
         For 'Hard' difficulty, include a subtle trap or require multiple steps.
         Your output MUST be a JSON object conforming to the QuestionOutput schema.
         """),
        ("human", f"Generate a {difficulty} difficulty GMAT Quant question on the topic of {topic}. Provide 5 options (A, B, C, D, E).")
    ])

    try:
        logging.debug("Attempting to invoke LLM chain for question generation...")
        chain = prompt | llm | JsonOutputParser(pydantic_object=QuestionOutput)
        response = chain.invoke({"topic": topic, "difficulty": difficulty}) # Pass relevant data to invoke
        logging.debug(f"LLM chain invoked successfully. Response data: {response}") # Added to log the actual response
        return jsonify(response)
    except Exception as e:
        logging.error(f"ERROR during question generation: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# --- 2. Answer Evaluation & Feedback Code (When Make.com sends an answer) ---
@app.route('/evaluate_answer', methods=['POST'])
def evaluate_answer():
    # --- START NEW DEBUGGING AND ROBUST PARSING LINES ---
    data = None # Initialize data to None
    try:
        raw_data = request.get_data(as_text=True)
        logging.debug(f"Received raw data for /evaluate_answer: {raw_data}")
        logging.debug(f"Request Content-Type header: {request.headers.get('Content-Type')}")

        # Attempt to parse JSON. Flask's request.json returns None if parsing fails
        # or if Content-Type is not application/json
        data = request.json
        if data is None:
            logging.error("request.json returned None. Raw data might be malformed JSON or Content-Type mismatch.")
            return jsonify({
                "error": "Could not parse JSON body. Ensure Content-Type is 'application/json' and body is valid JSON.",
                "received_raw_data": raw_data
            }), 400
    except Exception as e:
        # Catch any other unexpected errors during data reading
        logging.error(f"Error reading request data for /evaluate_answer: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to read request data: {e}", "traceback": traceback.format_exc()}), 400
    # --- END NEW DEBUGGING AND ROBUST PARSING LINES ---

    question_data = data.get('question_data')
    student_answer = data.get('student_answer')

    if not question_data or not student_answer:
        logging.warning("Missing 'question_data' or 'student_answer' in request body for evaluation.")
        return jsonify({"error": "Missing 'question_data' or 'student_answer' in request body."}), 400

    # Ensure question_data has the expected keys and is a dictionary
    if not isinstance(question_data, dict) or not all(k in question_data for k in ['answer', 'question', 'explanation']):
        logging.warning("Invalid 'question_data' format. Expected a dictionary with 'answer', 'question', 'explanation'.")
        return jsonify({"error": "Invalid 'question_data' format. Required keys: 'answer', 'question', 'explanation'."}), 400

    correct_answer = str(question_data['answer']).strip().lower()
    question_text = question_data['question']
    explanation = question_data['explanation']

    is_correct = str(student_answer).strip().lower() == correct_answer

    feedback_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a supportive and insightful GMAT tutor.
         Provide personalized feedback to the student based on their answer.
         If correct, offer positive reinforcement and explain why it's right.
         If incorrect, first clearly state the correct answer. Then, explain why the student's answer is wrong, why the correct answer is right (referencing the detailed explanation provided). Suggest a specific remediation topic (e.g., 'Algebra: Word Problems', 'Geometry: Triangles') if incorrect.
         Keep feedback concise and encouraging.
         Your output MUST be a JSON object conforming to the FeedbackOutput schema.
         """),
        ("human", f"""Student's question: {question_text}
         Student's answer: {student_answer}
         Correct answer: {correct_answer}
         Is correct: {is_correct}
         Detailed explanation: {explanation}
         """)
    ])

    try:
        logging.debug("Attempting to invoke LLM chain for feedback generation...")
        chain = feedback_prompt | llm | JsonOutputParser(pydantic_object=FeedbackOutput)
        response = chain.invoke({
            "question_text": question_text,
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": explanation
        })
        logging.debug("LLM chain for feedback invoked successfully.")
        return jsonify(response)
    except Exception as e:
        logging.error(f"ERROR during feedback generation: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# --- TEST ROUTE FOR LLM CALL ---
@app.route('/test_llm', methods=['POST'])
def test_llm():
    # --- START NEW DEBUGGING AND ROBUST PARSING LINES FOR TEST_LLM ---
    data = None
    try:
        raw_data = request.get_data(as_text=True)
        logging.debug(f"Received raw data for /test_llm: {raw_data}")
        logging.debug(f"Request Content-Type header: {request.headers.get('Content-Type')}")

        data = request.json
        if data is None:
            logging.error("request.json returned None for /test_llm. Raw data might be malformed JSON or content-type mismatch.")
            return jsonify({
                "status": "error",
                "message": "Could not parse JSON body for /test_llm. Ensure Content-Type is 'application/json' and body is valid JSON.",
                "received_raw_data": raw_data
            }), 400
    except Exception as e:
        logging.error(f"Error reading request data for /test_llm: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Failed to read request data for /test_llm: {e}", "traceback": traceback.format_exc()}), 400
    # --- END NEW DEBUGGING AND ROBUST PARSING LINES FOR TEST_LLM ---

    try:
        user_prompt = data.get('prompt', "Say 'Hello, AI is working!'")
        logging.info(f"Test LLM route called with prompt: '{user_prompt}'")

        test_prompt_template = ChatPromptTemplate.from_messages([
            ("human", "{user_prompt}")
        ])

        test_chain = test_prompt_template | llm
        test_response = test_chain.invoke({"user_prompt": user_prompt})
        logging.info(f"Test LLM invoke successful. Response: {test_response.content}")
        return jsonify({"status": "success", "response": test_response.content})
    except Exception as e:
        logging.error(f"ERROR: Test LLM call failed: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500
# --- END TEST ROUTE ---


# --- This starts the web connection (like turning on a listening phone) ---
if __name__ == '__main__':
    logging.info("Starting Flask server on http://127.0.0.1:5000/")
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, app, use_reloader=False, use_debugger=False)