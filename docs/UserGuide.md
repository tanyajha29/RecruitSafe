# RecruitSafe - End-User Guide

This guide walks you through registering, logging in, submitting analyses, and interpreting results inside RecruitSafe.

---

## 🔐 1. Register & Login

When you launch the application:
1. Navigate to the **Register** tab.
2. Enter your email and a secure password. Click **Sign Up**.
3. Upon registration, you will be redirected to the **Login** page.
4. Enter your credentials to access the main **Analysis Dashboard**.

---

## 🔍 2. Scanning a Job Posting

1. Paste the full text of the job description or email into the main input textarea.
2. Click **Scan Posting**.
3. The system processes the analysis in the background. You will see a progress spinner as the canonical extractor, rules engine, and ML pipeline are executed.

---

## 📊 3. Understanding the Analysis Dashboard

Once analysis completes, you will see a detailed safety dashboard:

* **Verdict Panel**: Shows the final safety assessment of the job posting:
  * 🟢 **SAFE**: The posting has low indicators of fraud and presents standard corporate hiring patterns.
  * 🟡 **SUSPICIOUS**: Some footprint signals or communication links raised alarms.
  * 🟠 **HIGH RISK**: Severe keyword detections or payment requests were found.
  * 🔴 **SCAM**: Immediate threat confirmed. Point deductions exceeding -60.
* **Trust Score & Confidence**: Displays the calculated trust percentage (0-100%) and the confidence factor representing data alignment.
* **Verification Footprints Grid**: Displays the status of crucial safety signals:
  * `✓ Verified`: Footprint resolved successfully (e.g. valid SSL certificate, old domain).
  * `⚠ Missing`: Footprint was inspected but found absent (e.g. missing privacy policy page).
  * `? Unknown`: Site was unreachable, preventing verification.
* **Triggered Flags & Explanations**: Lists all triggered threat vectors (e.g. training fees, Telegram contact requirements) along with context-aware semantic explanations.
* **Dynamic Action Recommendations**: Suggests specific validation checks matching the final verdict category.

---

## 📄 4. Exporting PDF Reports

1. Click the **Download PDF Report** button on the results page.
2. A formal PDF report containing the **Orchestration Flow Summary**, **Extraction Stats**, **Confidence Contributors**, and **Safety Indicators Breakdown** will be generated and downloaded.
