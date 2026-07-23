# RecruitSafe - Installation & Setup Guide

This guide details the step-by-step setup procedure for local installation and running the backend and frontend modules of RecruitSafe.

---

## 📋 1. Prerequisites

Make sure the following runtimes are installed on your machine:
* **Python**: Version `3.10` or above (`3.13` recommended)
* **Node.js**: Version `18` or above (`20` recommended)
* **MongoDB**: A running local MongoDB community edition server or an active MongoDB Atlas cluster URI.

---

## 🛠️ 2. Step-by-Step Installation

### Clone the Codebase
Clone or copy the code repository:
```bash
cd RecruitSafe
```

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install backend packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Download the required spaCy NLP model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install frontend packages:
   ```bash
   npm install
   ```

---

## ⚙️ 3. Environment Variables Configuration

Create a `.env` file in the `backend/` root directory:
```env
# MongoDB configuration
MONGODB_URL=mongodb://localhost:27017/recruitsafe

# JWT Security
SECRET_KEY=yoursecretjwtkeyhere
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Groq Cloud API Key (Semantic AI analysis)
GROQ_API_KEY=gsk_your_groq_api_key_value
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 🚀 4. Running the Application

### Start the Backend Server
Navigate to the `backend/` directory, activate the virtual environment, and run:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The REST API will be available at `http://127.0.0.1:8000`. Swagger documentation can be viewed at `http://127.0.0.1:8000/docs`.

### Start the Frontend Server
Navigate to the `frontend/` directory and run:
```bash
npm run dev
```
The React development server will be available at `http://localhost:5173`.

---

## 🔍 5. Running Tests

Run all automated unit tests using pytest from the `backend/` folder:
```bash
python -m pytest
```
Run the context-aware validation framework:
```bash
python -m tests.run_validation_framework
```
