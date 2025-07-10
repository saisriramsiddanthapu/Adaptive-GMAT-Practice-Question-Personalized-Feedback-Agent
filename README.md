# Adaptive GMAT Practice Question Personalized Feedback Agent 🚀

This project presents an intelligent, AI-powered system designed to revolutionize GMAT quantitative preparation. It dynamically generates practice questions tailored to a user's performance and provides in-depth, personalized feedback to help them pinpoint and overcome specific weaknesses.

## ✨ Features

*   **Dynamic Question Generation:** Creates GMAT-style quantitative questions based on specified topics (e.g., Algebra, Geometry) and difficulty levels (Easy, Medium, Hard).
*   **Personalized Feedback:** Delivers detailed, actionable feedback for each attempted question, explaining why an answer is correct or incorrect, going beyond generic explanations.
*   **Targeted Remediation:** Identifies specific sub-topics where a student needs improvement and suggests areas for further study.
*   **Structured AI Output:** Leverages Pydantic models with LangChain's structured output capabilities to ensure consistent and reliable JSON responses from Large Language Models (LLMs).
*   **API-Driven:** Exposes a robust Flask API for question generation and answer evaluation, allowing for seamless integration with external systems.
*   **Workflow Orchestration:** Demonstrates integration with Make.com (formerly Integromat) for end-to-end automation of the adaptive learning flow.

## 💡 Problem Solved

Traditional standardized test preparation often relies on static question banks and generalized feedback, making it challenging for students to efficiently identify and address their unique learning gaps. This agent provides a highly personalized learning experience, adapting to the student's needs in real-time and offering specific guidance to maximize study efficiency.

## 🛠️ Technologies Used

*   **Backend & API:**
    *   **Python:** Core programming language.
    *   **Flask:** Lightweight web framework for building the RESTful API.
    *   **`python-dotenv`:** For managing environment variables securely.
    *   **`werkzeug`:** WSGI utility library used by Flask's development server.
*   **AI / Machine Learning:**
    *   **LangChain:** Framework for developing applications powered by LLMs, used for prompt orchestration and structured output.
    *   **`langchain-openai`:** Connector for OpenAI-compatible APIs.
    *   **OpenRouter.ai:** LLM API provider, utilizing the **DeepSeek** model for intelligent text generation and understanding.
    *   **Pydantic:** Data validation and parsing library, used to define strict schemas for LLM outputs, ensuring reliability.
*   **Integration & Development Tools:**
    *   **Make.com (formerly Integromat):** Cloud-based automation platform used to orchestrate the workflow, making HTTP requests to the local API.
    *   **`venv` (Python Virtual Environments):** For isolated dependency management.
    *   **`ngrok`:** Secure tunneling service to expose the local Flask API to the internet, enabling Make.com to access it.
    *   **Postman:** For API testing and debugging.

## 🚀 Getting Started

Follow these steps to get a copy of the project up and running on your local machine.

### Prerequisites

*   Python 3.9+ installed
*   `pip` (Python package installer)
*   `git` (for cloning the repository)
*   An [OpenRouter.ai](https://openrouter.ai/) account and an API Key (Free tier is usually sufficient for testing).
*   `ngrok` executable installed and authenticated (download from [ngrok.com](https://ngrok.com/) and run `ngrok authtoken YOUR_AUTH_TOKEN`).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/[YourGitHubUsername]/gmat_ai_project.git
    cd gmat_ai_project
    ```

2.  **Create and activate a virtual environment:**
    ```powershell
    python -m venv venv
    . .\venv\Scripts\Activate.ps1
    ```
    *   **Note for PowerShell users:** If you encounter an error related to script execution, run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then try activating again.

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
    *   If `requirements.txt` is missing, you can generate a basic one with `pip freeze > requirements.txt` (after installing necessary packages like Flask, langchain-openai, pydantic) or create it manually with:
        ```
        flask
        langchain-openai
        pydantic
        python-dotenv
        ```

### Environment Variables (`.env`)

Create a file named `.env` in the root of your project directory (where `app.py` is located) and add your OpenRouter API key and desired model:

*   **Important:** Replace `YOUR_OPENROUTER_API_KEY_HERE` with your actual key from OpenRouter.ai.
*   The `deepseek/deepseek-r1-0528-qwen3-8b:free` model is used by default as it's often available on the free tier. You can change this to another model supported by OpenRouter if needed.

## 🏃 Running the Application

You'll need two separate terminal windows for this:

### Terminal Window 1: Flask Application

1.  **Navigate to your project directory (if not already there):**
    ```powershell
    cd "C:\Users\YourUsername\OneDrive\Desktop\gmat_ai_project"
    ```
    *(Adjust the path to your actual project location)*

2.  **Activate your virtual environment:**
    ```powershell
    . .\venv\Scripts\Activate.ps1
    ```

3.  **Run the Flask application:**
    ```powershell
    python app.py
    ```
    You should see output similar to `* Running on http://127.0.0.1:5000/`. **Keep this window open and running.**

### Terminal Window 2: ngrok Tunnel

1.  **Open a *new*, separate PowerShell window.**

2.  **Navigate to your project directory (where `ngrok.exe` is located):**
    ```powershell
    cd "C:\Users\YourUsername\OneDrive\Desktop\gmat_ai_project"
    ```
    *(Adjust the path to your actual project location, or to wherever your ngrok.exe is)*

3.  **Start ngrok to expose your Flask app to the internet:**
    ```powershell
    .\ngrok.exe http 5000
    ```
    ngrok will start and display a `Forwarding` URL (e.g., `https://xxxx-xx-xx-xx-xx.ngrok-free.app`). **Copy this URL.**

## 🌐 Integrating with Make.com

1.  Go to your Make.com (formerly Integromat) scenario where you've set up your workflow.
2.  In your HTTP module, **update the URL** to the `Forwarding` URL you copied from your `ngrok` terminal.
3.  Ensure your HTTP module is configured to send a `POST` request with a `Content-Type: application/json` header and a JSON request body (e.g., `{"topic": "Algebra", "difficulty": "Medium"}` for `/generate_question`).
4.  Run your Make.com scenario to see the full flow in action!

## 🧪 API Endpoints

The Flask application exposes the following RESTful API endpoints:

### 1. `POST /generate_question`

*   **Description:** Generates a GMAT-style quantitative question with multiple-choice options, a detailed explanation, and the correct answer.
*   **Request Body (JSON):**
    ```json
    {
        "topic": "Algebra",   # Optional, default is "Algebra"
        "difficulty": "Medium" # Optional, default is "Medium". Options: "Easy", "Medium", "Hard"
    }
    ```
*   **Example Response (JSON):**
    ```json
    {
        "question": "If 2x + 3 = 4x - 5, then x = ?",
        "options": ["A) 1", "B) -1", "C) 0", "D) 2", "E) 4"],
        "explanation": "To solve the equation 2x + 3 = 4x - 5:\n1. Subtract 2x from both sides: 3 = 2x - 5\n2. Add 5 to both sides: 8 = 2x\n3. Divide by 2: x = 4. Therefore, the correct answer is E.",
        "answer": "E"
    }
    ```

### 2. `POST /evaluate_answer`

*   **Description:** Provides personalized feedback on a student's answer to a generated question.
*   **Request Body (JSON):**
    ```json
    {
        "question_data": {
            "question": "Your question text here...",
            "options": ["A) ...", "B) ..."],
            "explanation": "The detailed explanation from generate_question...",
            "answer": "B" # The correct answer letter
        },
        "student_answer": "C" # The student's submitted answer
    }
    ```
*   **Example Response (JSON):**
    ```json
    {
        "is_correct": false,
        "feedback": "Your answer 'C' is incorrect. The correct answer is 'B'. Review the explanation carefully, specifically focusing on isolating the variable and performing operations on both sides of the equation. Try similar problems involving linear equations.",
        "remediation_topic": "Algebra: Linear Equations"
    }
    ```

### 3. `POST /test_llm`

*   **Description:** A simple endpoint to test the LLM connection and basic response.
*   **Request Body (JSON):**
    ```json
    {
        "prompt": "Tell me a fun fact about Python."
    }
    ```
*   **Example Response (JSON):**
    ```json
    {
        "status": "success",
        "response": "Did you know the name 'Python' comes from the British comedy group Monty Python, not the snake?"
    }
    ```


## 🔮 Future Enhancements

*   **User Interface (UI):** Develop a simple web-based frontend for a more intuitive user experience.
*   **Database Integration:** Implement a database (e.g., SQLite, PostgreSQL) to store user progress, past questions, and feedback for persistent adaptive learning.
*   **More Sophisticated Adaptation:** Incorporate an Item Response Theory (IRT) model or similar for more nuanced difficulty adjustment and skill tracking.
*   **Support for Other GMAT Sections:** Expand to Verbal (Critical Reasoning, Sentence Correction, Reading Comprehension) and Analytical Writing Assessment (AWA).
*   **Dockerization:** Containerize the Flask application using Docker for easier deployment and portability.
*   **Cloud Deployment:** Deploy the application to cloud platforms (AWS, Azure, GCP) for scalability and reliability.
*   **Advanced MLOps:** Integrate tools for model versioning, monitoring, and automated retraining pipelines.

## 🤝 Contributing

Contributions are welcome! If you have suggestions or want to improve the project, feel free to:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a Pull Request.

## 📄 License

This project is licensed under the **MIT License**.

The MIT License is a permissive free software license, meaning it allows you to reuse, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software. This is ideal for open-source projects where you want to encourage widespread adoption and contribution.

For the full text of the license, see the [LICENSE](LICENSE) file in this repository.

## 📧 Contact

[Sai Sri Ram Siddanthapu] - [[Your LinkedIn Profile URL](https://www.linkedin.com/in/sai-sri-ram-siddanthapu-0962a1255)] - [sriramsiddanthapu@gmail.com]

---
