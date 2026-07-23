# RecruitSafe - Hybrid Decision Intelligence Platform

RecruitSafe is a production-grade, multi-layered job posting audit and scam detection platform. By combining deterministic regular expression scanners, deep-crawling infrastructure footprints verifiers, spaCy-based natural language processing context models, and XGBoost machine learning text classifiers, RecruitSafe provides clear threat verdicts and mitigation directions for job seekers.

---

## 🌟 Key Features

* **3-Layer Canonical Extraction**: Decouples extraction, normalization, and validation rules to map 31 distinct metadata points.
* **Context-Aware Rule Engine**: Integrates regular expression keyword matchers with a spaCy NLP pipeline to distinguish genuine offers from phishing patterns (e.g. voluntary training vs. mandatory registration fees).
* **Deep footprints Verification**: Audits DNS reachability, resolves HTTPS/SSL certificate issues, parses WHOIS records to check domain age, and validates external company crawling footprints.
* **Machine Learning Analysis**: Employs a thread-safe, lazy-loaded XGBoost model and TF-IDF text vectorization.
* **Calibrated Decision Fusion Scorer**: Merges engine results using weights from configuration maps to issue verdicts (`SAFE`, `SUSPICIOUS`, `HIGH_RISK`, `SCAM`).
* **Visual PDF Reporting**: Generates automated, ReportLab-based PDF audits summarizing confidence levels and safety metrics.

---

## 💻 Technology Stack

* **FastAPI**: Backend web framework.
* **Beanie ODM & Motor**: MongoDB ODM mapping.
* **spaCy**: NLP syntactic token and dependency parsing.
* **scikit-learn & XGBoost**: ML vectorization and predictions.
* **ReportLab**: PDF report canvas rendering.
* **React, Vite, & Tailwind CSS**: Frontend dashboard UI.

---

## 📂 System Architecture Overview

```
                          [ Job Posting Text ]
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
        [ Canonical Extractor ]         [ XGBoost ML Content Classifier ]
                     │                           │
                     ▼                           ▼
        [ Context-Aware Rules ]           [ Content Score ]
                     │                           │
                     ▼                           │
        [ Verification footprints ]              │
                     │                           │
                     └─────────────┬─────────────┘
                                   ▼
                       [ Decision Fusion Engine ]
                                   │
                                   ▼
                     [ Final Verdict & PDF Report ]
```

Detailed architectural breakdowns can be found in [docs/Architecture.md](file:///c:/Users/jhata/WEB-Projects/RecruitSafe/docs/Architecture.md).

---

## 🚀 Getting Started

### Local Setup
1. Clone the repository and navigate to backend directory. Create virtual env and install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
2. Set up your local environment file (`.env`):
   ```env
   MONGODB_URL=mongodb://localhost:27017/recruitsafe
   SECRET_KEY=yoursecretkey
   GROQ_API_KEY=yourkey
   ```
3. Boot the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
4. Navigate to the frontend directory, install npm modules, and run the developer server:
   ```bash
   npm install
   npm run dev
   ```

Detailed installation steps are available in [docs/Setup.md](file:///c:/Users/jhata/WEB-Projects/RecruitSafe/docs/Setup.md).

---

## 📄 Project Guides

* **System Design & Sequence Flow**: [docs/Architecture.md](file:///c:/Users/jhata/WEB-Projects/RecruitSafe/docs/Architecture.md)
* **REST API Endpoint Specifications**: [docs/API.md](file:///c:/Users/jhata/WEB-Projects/RecruitSafe/docs/API.md)
* **Local Prerequisites & Setup**: [docs/Setup.md](file:///c:/Users/jhata/WEB-Projects/RecruitSafe/docs/Setup.md)
* **End-User Application Manual**: [docs/UserGuide.md](file:///c:/Users/jhata/WEB-Projects/RecruitSafe/docs/UserGuide.md)
* **Developer Customizations**: [docs/DeveloperGuide.md](file:///c:/Users/jhata/WEB-Projects/RecruitSafe/docs/DeveloperGuide.md)

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for details.