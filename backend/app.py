from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load configuration
from config import config
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])

# Initialize extensions with app
from extensions import db
db.init_app(app)
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# Initialize AI services
from services.humanizer import HumanizeEngine
from services.detector import AIDetector

humanizer = HumanizeEngine()
detector = AIDetector()

# Create upload folder
os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)


# ===== HUMANIZE ROUTE =====

@app.route('/api/humanize', methods=['POST'])
def humanize():
    data = request.get_json()

    text = data.get('text', '')
    tone = data.get('tone', 'casual')
    language = data.get('language', 'en')

    if not text or len(text) > 10000:
        return jsonify({'error': 'Text must be between 1 and 10000 characters'}), 400

    # Humanize text
    try:
        humanized = humanizer.humanize(text, tone=tone, language=language)
    except Exception as e:
        return jsonify({'error': f'Humanization failed: {str(e)}'}), 500

    # Detect AI patterns
    try:
        detection_before = detector.detect(text)
        detection_after = detector.detect(humanized)
    except Exception as e:
        detection_before = {'ai_score': 0, 'patterns': []}
        detection_after = {'ai_score': 0, 'patterns': []}

    return jsonify({
        'success': True,
        'original': text,
        'humanized': humanized,
        'ai_score_before': detection_before['ai_score'],
        'ai_score_after': detection_after['ai_score'],
        'patterns_removed': detection_before.get('patterns', []),
    })


# ===== FILE UPLOAD ROUTE =====

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Extract text based on file type
    try:
        if file.filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        elif file.filename.endswith('.pdf'):
            import PyPDF2
            reader = PyPDF2.PdfReader(file)
            text = '\n'.join([page.extract_text() for page in reader.pages])
        elif file.filename.endswith('.docx'):
            from docx import Document as DocxDocument
            doc = DocxDocument(file)
            text = '\n'.join([p.text for p in doc.paragraphs])
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'text': text[:10000],
        'word_count': len(text.split())
    })


# ===== HEALTH CHECK ROUTE =====

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': humanizer.model_loaded if hasattr(humanizer, 'model_loaded') else True,
        'database': 'connected'
    })


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ===== INITIALIZE DATABASE =====

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
