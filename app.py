from dotenv import load_dotenv
load_dotenv('api.env')
import os
import traceback
import docx                # python-docx
import PyPDF2
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import openai

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

# OpenAI API key - set in .env 
openai.api_key = os.environ.get('OPENAI_API_KEY', '')


# ---- Helpers --------------------------------------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file_obj):
    """Save uploaded FileStorage and return secure filename (or None)."""
    filename = secure_filename(file_obj.filename)
    if not filename:
        return None
    out_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_obj.save(out_path)
    return filename

def extract_text(filepath):
    """Extract text from txt / pdf / docx / doc (doc -> ask user to convert)."""
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif ext == '.pdf':
            text = ""
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text
        elif ext == '.docx':
            doc = docx.Document(filepath)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip() != ""]
            return "\n".join(paragraphs)
        elif ext == '.doc':
            # .doc support is flaky without third-party converters; ask user to save as .docx
            return ""
        else:
            return ""
    except Exception:
        traceback.print_exc()
        return ""

def truncate_text(text, max_chars=15000):
    if not text:
        return text
    return text if len(text) <= max_chars else text[:max_chars] + "\n\n[...truncated]"

def call_openai_chat(messages, max_tokens=500, temperature=0.3):
    """Wrapper for the OpenAI chat call used previously."""
    if not openai.api_key:
        return "OpenAI API key not set. Please set OPENAI_API_KEY environment variable."
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Return error string for display (useful for debugging)
        return f"OpenAI API error: {str(e)}"

# AI helpers (same prompts as before)
def get_summary(text):
    text = truncate_text(text)
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes study notes clearly and concisely."},
        {"role": "user", "content": f"Please summarize the following text for study purposes. Keep it concise (3-6 sentences), highlight main ideas and important terms:\n\n{text}"}
    ]
    return call_openai_chat(messages, max_tokens=500, temperature=0.2)

def get_notes(text):
    text = truncate_text(text)
    messages = [
        {"role": "system", "content": "You are an assistant that converts raw text into structured study notes with headings and bullet points."},
        {"role": "user", "content": f"Convert the following text into well-structured study notes. Use short headings, then 3-6 concise bullet points under each heading. Keep it suitable for quick review:\n\n{text}"}
    ]
    return call_openai_chat(messages, max_tokens=700, temperature=0.25)

def get_evaluation(text):
    text = truncate_text(text)
    messages = [
        {"role": "system", "content": "You are an assistant that evaluates study material and gives a numeric score and actionable feedback."},
        {"role": "user", "content": f"Evaluate the following text on clarity, completeness, accuracy, and usefulness for a student. Provide:\n1) A numeric score out of 10 (one number).\n2) A short justification (2-4 sentences).\n3) Two concrete suggestions to improve the material.\n\n{text}"}
    ]
    return call_openai_chat(messages, max_tokens=500, temperature=0.3)

# ---- Routes ---------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')

# POST endpoints (accept either uploaded file or 'file' hidden filename)
@app.route('/summarize', methods=['POST'])
def summarize_post():
    filename = None
    if 'file' in request.files and request.files['file'].filename != '':
        uploaded = request.files['file']
        if not allowed_file(uploaded.filename):
            return "File type not allowed.", 400
        filename = save_uploaded_file(uploaded)
    else:
        filename = request.form.get('file') or request.form.get('filename')

    if not filename:
        return redirect(url_for('upload_page'))

    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    text = extract_text(filepath)
    if not text.strip():
        result = "No text could be extracted from the file. Please upload a plain .txt, .pdf, or .docx file (or convert .doc to .docx)."
    else:
        result = get_summary(text)

    return render_template('result_summary.html', result=result, file_path=filename)

# alias /create_notes -> /notes POST
@app.route('/create_notes', methods=['POST'])
def create_notes_alias():
    return notes_post()

@app.route('/notes', methods=['POST'])
def notes_post():
    filename = None
    if 'file' in request.files and request.files['file'].filename != '':
        uploaded = request.files['file']
        if not allowed_file(uploaded.filename):
            return "File type not allowed.", 400
        filename = save_uploaded_file(uploaded)
    else:
        filename = request.form.get('file') or request.form.get('filename')

    if not filename:
        return redirect(url_for('upload_page'))

    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    text = extract_text(filepath)
    if not text.strip():
        result = "No text could be extracted from the file. Please upload a plain .txt, .pdf, or .docx file (or convert .doc to .docx)."
    else:
        result = get_notes(text)

    return render_template('result_notes.html', result=result, file_path=filename)

@app.route('/evaluate', methods=['POST'])
def evaluate_post():
    filename = None
    if 'file' in request.files and request.files['file'].filename != '':
        uploaded = request.files['file']
        if not allowed_file(uploaded.filename):
            return "File type not allowed.", 400
        filename = save_uploaded_file(uploaded)
    else:
        filename = request.form.get('file') or request.form.get('filename')

    if not filename:
        return redirect(url_for('upload_page'))

    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    text = extract_text(filepath)
    if not text.strip():
        result = "No text could be extracted from the file. Please upload a plain .txt, .pdf, or .docx file (or convert .doc to .docx)."
    else:
        result = get_evaluation(text)

    return render_template('result_eval.html', result=result, file_path=filename)

# Convenience GET routes (optional)
@app.route('/summarize/<filename>', methods=['GET'])
def summarize_get(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    text = extract_text(filepath)
    if not text.strip():
        result = "No text could be extracted from the file."
    else:
        result = get_summary(text)
    return render_template('result_summary.html', result=result, file_path=filename)

@app.route('/notes/<filename>', methods=['GET'])
def notes_get(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    text = extract_text(filepath)
    if not text.strip():
        result = "No text could be extracted from the file."
    else:
        result = get_notes(text)
    return render_template('result_notes.html', result=result, file_path=filename)

@app.route('/evaluate/<filename>', methods=['GET'])
def evaluate_get(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    text = extract_text(filepath)
    if not text.strip():
        result = "No text could be extracted from the file."
    else:
        result = get_evaluation(text)
    return render_template('result_eval.html', result=result, file_path=filename)

# ---- Run server -----------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
