# ReportHumanizer: AI Text Humanizer

ReportHumanizer is a sophisticated AI-powered application designed to transform AI-generated text into high-quality, human-like prose. By leveraging advanced NLP models and a multi-stage refinement pipeline, it helps bypass AI detection while preserving factual integrity and enhancing readability.

---

## 🌟 Features

- **Multi-Stage Humanization**: Iterative refinement process to ensure natural flow and human-like variation.
- **AI Detection Bypass**: Specifically tuned to reduce AI detection scores (Turnitin, GPTZero, etc.).
- **Tone Selection**: Customize output for Casual, Academic, Formal, or Creative contexts.
- **Multi-Language Support**: Supports English, Spanish, French, German, Portuguese, Chinese, and Japanese.
- **File Upload Support**: Directly process `.txt`, `.pdf`, and `.docx` files.
- **Visual Diff**: Real-time comparison between original and humanized text.
- **AI Pattern Analysis**: Detailed feedback on removed AI patterns and improvements made.

---

## 🛠 Tech Stack

### Frontend
- **Framework**: React.js (Vite)
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy (SQLite for development)
- **NLP Libraries**: HuggingFace Transformers, NLTK, SpaCy
- **Authentication**: JWT (JSON Web Tokens)
- **LLM Integration**: Google Gemini (primary), with support for OpenAI/Anthropic.

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v18.0 or higher
- **Python**: v3.8 or higher
- **npm**: v9.0 or higher

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/ReportHumanizer.git
   cd ReportHumanizer
   ```

2. **Backend Setup**
   ```bash
   cd backend
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Download NLTK and SpaCy data
   python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
   python -m spacy download en_core_web_sm
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

---

## ⚙️ Configuration

### Backend Environment Variables
Create a `.env` file in the `backend/` directory:
```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=sqlite:///database.db
JWT_SECRET=your_super_secret_key
CORS_ORIGINS=http://localhost:5173
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
```

### Frontend Environment Variables
Create a `.env` file in the `frontend/` directory:
```env
VITE_API_URL=http://localhost:5001
```

---

## 🏃 Running the Application

### 1. Start the Backend
```bash
cd backend
source venv/bin/activate
python app.py
```
The backend will be running on `http://localhost:5001`.

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:5173`.

---

## 📂 Project Structure

```text
ReportHumanizer/
├── backend/            # Flask API, ML models, and services
│   ├── models/         # Database schemas
│   ├── routes/         # API endpoints
│   ├── services/       # Core humanization logic
│   ├── config.py       # App configuration
│   └── app.py          # Entry point
├── frontend/           # React application
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── hooks/      # Custom React hooks
│   │   └── App.jsx     # Main entry
│   └── vite.config.js  # Build configuration
├── deployment/         # Docker and CI/CD configurations
├── docs/               # Technical documentation
└── training/           # ML model training scripts and datasets
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
