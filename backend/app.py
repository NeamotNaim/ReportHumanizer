from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import difflib
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

def _generate_word_diff(original, humanized):
    # Splits by word for diffing
    orig_words = original.split()
    hum_words = humanized.split()
    matcher = difflib.SequenceMatcher(None, orig_words, hum_words)
    diff_data = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            diff_data.append({'type': 'equal', 'value': ' '.join(orig_words[i1:i2])})
        elif tag == 'replace':
            diff_data.append({'type': 'removed', 'value': ' '.join(orig_words[i1:i2])})
            diff_data.append({'type': 'added', 'value': ' '.join(hum_words[j1:j2])})
        elif tag == 'delete':
            diff_data.append({'type': 'removed', 'value': ' '.join(orig_words[i1:i2])})
        elif tag == 'insert':
            diff_data.append({'type': 'added', 'value': ' '.join(hum_words[j1:j2])})
            
    return diff_data


# ===== HUMANIZE ROUTE =====

@app.route('/api/humanize', methods=['POST'])
def humanize():
    data = request.get_json()

    text = data.get('text', '')
    tone = data.get('tone', 'casual')
    language = data.get('language', 'en')

    if not text or len(text) > 10000:
        return jsonify({'error': 'Text must be between 1 and 10000 characters'}), 400

    # Analyze text before humanization
    try:
        analysis_before = humanizer.analyze_text(text, tone=tone)
    except Exception as e:
        analysis_before = {"issues": [], "strengths": []}

    # Humanize text (now returns dict with humanized text + metadata)
    try:
        result = humanizer.humanize(text, tone=tone, language=language)
        humanized = result["humanized"]
        iterations = result.get("iterations", 0)
        stage_log = result.get("stage_log", [])
    except Exception as e:
        return jsonify({'error': f'Humanization failed: {str(e)}'}), 500

    # Analyze text after humanization
    try:
        analysis_after = humanizer.analyze_text(humanized, tone=tone)
    except Exception as e:
        analysis_after = {"issues": [], "strengths": []}

    # Detect AI patterns before and after
    try:
        detection_before = detector.detect(text)
        detection_after = detector.detect(humanized)
    except Exception as e:
        detection_before = {'ai_score': 0, 'patterns': []}
        detection_after = {'ai_score': 0, 'patterns': []}

    # Generate Diff
    diff_result = _generate_word_diff(text, humanized)

    # Word count comparison
    original_words = len(text.split())
    humanized_words = len(humanized.split())

    return jsonify({
        'success': True,
        'original': text,
        'humanized': humanized,
        'diff': diff_result,
        'ai_score_before': detection_before.get('ai_score', 0),
        'ai_score_after': detection_after.get('ai_score', 0),
        'patterns_removed': detection_before.get('patterns', []),
        'analysis_before': analysis_before,
        'analysis_after': analysis_after,
        'word_count_original': original_words,
        'word_count_humanized': humanized_words,
        'iterations': iterations,
        'stage_log': stage_log,
        'provider': os.getenv('LLM_PROVIDER', 'gemini'),
        'assessment_note': (
            'These scores are local heuristics for structure and phrasing. '
            'They are not equivalent to Turnitin, GPTZero, or any external AI detector. '
            'However, the multi-stage pipeline significantly improves humanization quality.'
        ),
    })


# ===== PROVIDER INFO ROUTE =====

@app.route('/api/provider', methods=['GET'])
def get_provider_info():
    """Return current LLM provider status."""
    return jsonify({
        'provider': os.getenv('LLM_PROVIDER', 'gemini'),
        'model_loaded': humanizer.model_loaded,
        'llm_available': humanizer.llm.is_available if humanizer.llm else False,
        'model_name': humanizer.llm.model_name if humanizer.llm else None,
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
        'model_loaded': humanizer.model_loaded,
        'provider': os.getenv('LLM_PROVIDER', 'gemini'),
        'llm_available': humanizer.llm.is_available if humanizer.llm else False,
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
