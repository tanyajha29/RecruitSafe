# RecruitSafe - API Documentation

This document describes all REST API endpoints exposed by the RecruitSafe FastAPI backend application.

---

## 🔐 1. Authentication Endpoints

### Register User
* **Method**: `POST`
* **Route**: `/api/auth/register`
* **Authentication**: None
* **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123"
  }
  ```
* **Response Body (201 Created)**:
  ```json
  {
    "message": "User registered successfully",
    "user_id": "6a62583831250d7c5cbc5af5"
  }
  ```
* **Possible Errors**:
  * `400 Bad Request`: Email already registered.

### Login User
* **Method**: `POST`
* **Route**: `/api/auth/login`
* **Authentication**: None
* **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword123"
  }
  ```
* **Response Body (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer"
  }
  ```
* **Possible Errors**:
  * `401 Unauthorized`: Invalid credentials.

---

## 🔍 2. Analysis Endpoints

### Submit Job Text for Analysis
* **Method**: `POST`
* **Route**: `/api/analyze`
* **Authentication**: JWT Token (Bearer)
* **Request Body**:
  ```json
  {
    "text": "Job description text goes here..."
  }
  ```
* **Response Body (201 Created)**:
  ```json
  {
    "analysis_id": "6a62607f0ad8e7a359361332",
    "status": "pending",
    "message": "Job analysis task submitted successfully"
  }
  ```

### Get Analysis Results
* **Method**: `GET`
* **Route**: `/api/analyze/{id}`
* **Authentication**: JWT Token (Bearer)
* **Response Body (200 OK)**:
  ```json
  {
    "id": "6a62607f0ad8e7a359361332",
    "status": "completed",
    "verdict": "SAFE",
    "trust_score": 91,
    "confidence": 95.0,
    "evidence": [
      {
        "id": "official_corporate_email",
        "factor_name": "Official corporate email",
        "points_deducted": 0,
        "score": 20,
        "severity": "NONE"
      }
    ],
    "verifications": {
      "website_reachable": "Verified",
      "ssl_valid": "Verified",
      "domain_age": "Verified",
      "careers_page": "Verified"
    },
    "recommendations": [
      "Mitigate danger by verifying contacts"
    ]
  }
  ```
* **Possible Errors**:
  * `404 Not Found`: Analysis ID does not exist.

---

## 📄 3. Report Endpoints

### Download Analysis PDF Report
* **Method**: `GET`
* **Route**: `/api/report/{id}`
* **Authentication**: JWT Token (Bearer)
* **Response**: Binary PDF file (`application/pdf`)
* **Possible Errors**:
  * `404 Not Found`: Analysis report does not exist.

---

## 🩺 4. Health & System status

### ML Service Health check
* **Method**: `GET`
* **Route**: `/api/ml/health`
* **Authentication**: None
* **Response Body (200 OK)**:
  ```json
  {
    "loaded": true,
    "model_name": "recruitsafe_xgb",
    "model_version": "1.0.0",
    "vectorizer_loaded": true,
    "model_loaded": true
  }
  ```
