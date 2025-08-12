**SummAI - The AI Study Assistant**

**Overview**
AI Study Assistant is a Python-based application designed to help students, researchers, and professionals summarize lengthy texts, create concise study notes, and evaluate the quality or meaning of written content. It uses OpenAI’s API as the backend intelligence, enabling high-quality natural language processing and generation.
Features

•	Text Summarization – Condense long paragraphs or documents into key points.
•	Note Creation – Automatically generate clear, concise notes from any given text.
•	Text Evaluation – Assess writing for clarity, tone, and structure.
•	Interactive Assistant – A simple, user-friendly interface for queries and responses.

**Tech Stack**
Programming Language: Python 3.x
Backend AI: OpenAI API (GPT-based models)
Environment Management: .env for API key security

**Additional Libraries:**
  - openai – to communicate with the OpenAI API
  - flask – for web-based interaction
  - dotenv – to load environment variables
    
**Installation**

1. Clone the repository:
git clone httpshttps://github.com/bareknuckles-99/SummAI.git
cd SummAI

3. Create and activate a virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate      # For Linux/Mac
venv\Scripts\activate         # For Windows

5. Install dependencies:
pip install -r requirements.txt

7. Set up environment variables:
Create a .env file in the project root with:
OPENAI_API_KEY=your_api_key_here
(Never commit .env to version control)

**Usage**
Run the application:
python app.py

Depending on your implementation, interact through Terminal/CLI or Web Interface (if Flask or another framework is used).

**Example**
Input Text:
Artificial intelligence refers to the simulation of human intelligence in machines that are programmed to think and learn.
AI Assistant Output:
- Summary: AI is the simulation of human intelligence in machines.
- Notes:
  - AI mimics human thinking and learning
  - Used in various fields such as automation, robotics, and data analysis
- Evaluation: Clear, concise, and well-structured definition.

  
**Project Structure**

AI-Study-Assistant/
│
├── app.py              # Main application script
├── .env                # Environment variables (ignored in Git)
├── .gitignore          # Git ignore file
├── requirements.txt    # Dependencies
├── static/             # Static assets (if web-based)
├── templates/          # HTML templates (if web-based)
└── README.md           # Project documentation

**Security Notes**
Your OpenAI API Key must be stored in .env and never committed to GitHub.
.gitignore already includes .env and __pycache__/ for protection.

**Future Improvements**
•	Add support for PDF and DOCX file uploads.
•	Implement multi-language summarization.
•	Provide export options (PDF, Markdown).
•	Add interactive chat mode with memory for ongoing sessions.

