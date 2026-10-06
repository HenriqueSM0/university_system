# 🎓 University System Agents & Core Database

First and foremost, **thank you** so much for visiting this repository! We are incredibly grateful for the open-source community, the amazing developers behind the libraries we use, and to you for taking the time to explore this project. This system is built with care to simulate and automate the complex operations of a university environment. 

---

## ✨ Features

Our system integrates a robust relational database with AI-powered agents to manage university operations seamlessly:

*   **Comprehensive Academic Modeling:** Fully models Institutes, Courses, Subjects (Matérias), Professors, Students, and Classes (Turmas).
*   **Intelligent Scheduling:** Calculates time conflicts, validates course hours, and maps class times accurately using a custom `Horario` class.
*   **AI-Powered Verification:**
    *   *Time & Location Agent:* Correlates and verifies if the user-provided room/location matches the complex scheduling strings.
    *   *Cancellation Agent:* Analyzes student justifications for dropping courses and approves valid administrative calls.
*   **Enrollment & Priority System:** Handles student enrollment requests, manages class vacancies (including course-specific reservations), and processes priority-based waitlists.
*   **Academic Metrics:** Automatically calculates a student's General GPA (Média Geral) and Approval Rates based on their course history.

---

## 🛠️ Libraries Used

We are thankful for the following tools that make this system tick:

*   **`sqlite3`**: The built-in backbone of our relational database structure.
*   **`json`**: Used for storing dynamic grade data within the database.
*   **`datetime`**: Essential for calculating current semesters and student periods.
*   **`langchain_groq`**: Connects our system to lightning-fast LLMs for our AI verification agents.
*   **`python-dotenv`**: Securely loads environment variables for API integrations.

---

## 🚀 Working Info

To get the system up and running, you simply need to execute our test script. This script will automatically spin up the database, create the necessary tables in dependency order, and populate it with sample data (like our test student, Maria!).

1. Ensure you have Python installed.
2. Run the test population script:
   ```bash
   python test.py
   ```
3. A `university.db` file will be generated in your root folder. If it already exists, the script will kindly refresh it for you!

---

## 🔑 Environment Setup (Groq API)

To enable the AI Agents (handled in `ai_funcs.py`), you need to provide access to the Groq LLM API. 

1. Create a file named `.env` in the root directory of the project.
2. Add your Groq API key to the file like this:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```
*(Note: The system gracefully falls back to returning `-1` (error/bypass state) if the API key or agents are not available, so your database will still work perfectly without it!)*

---
*Thank you again for exploring this project! We hope it serves as a wonderful example of combining traditional database management with modern AI integrations.*