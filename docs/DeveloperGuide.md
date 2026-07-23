# RecruitSafe - Developer Customization Guide

This guide describes how to extend and customize the RecruitSafe rule engine, verifications, machine learning services, and fusion scoring settings.

---

## 🛠️ 1. Project Directory Structure

* `/backend/app/services/`:
  - `nlp/`: Singleton spaCy initialization, intent classification heuristics, and models.
  - `rules/`: Registry setups, execution pipeline, and builtin regex rules.
  - `ai/`: ML vectorizer, XGBoost model pickle configurations, and health checks.
  - `fusion/`: Calibrator classes evaluating risk scores.
  - `website_verifier.py`: Core verifiers for DNS, SSL, and Careers URL footprints.
* `/backend/app/config/`:
  - `rules_config.json`: Core regex keyword databases.
  - `severity_config.json`: Dynamic intent-to-severity maps.
  - `score_config.json`: Dynamic severity-to-points deductions maps.
  - `fusion_config.json`: Centralized weights configurations.

---

## 🔌 2. Adding a New Context-Aware Detection Rule

To add a new rule:
1. Open `backend/app/config/rules_config.json` and append your rule descriptor:
   ```json
   {
     "id": "new_rule_id",
     "name": "New Rule Name",
     "description": "Rule trigger description.",
     "category": "financial_fraud",
     "severity": "medium",
     "weight_key": "payment_request",
     "default_weight": -20,
     "keywords": [
       "\\btrigger\\s*phrase\\b"
     ]
   }
   ```
2. Open `backend/app/services/rules/builtin_rules.py`. Locate the `context_aware_rules` set in `RegexPatternRule.evaluate()` and add your new rule ID:
   ```python
   context_aware_rules = {
       "payment", "registration_fee", "training_fee", "paid_certification",
       "telegram_only", "whatsapp_only", "telegram", "whatsapp",
       "no_interview", "guaranteed_placement", "urgency_urg", "new_rule_id"
   }
   ```
3. Open `backend/app/services/nlp/intent_classifier.py`. If your rule maps to a new semantic context intent, add a new classification rule inside `IntentClassifier.classify()` and update the mapping configs:
   * **`severity_config.json`**: Define the intent severity.
   * **`score_config.json`**: Define point deductions.

---

## 🔒 3. Updating the Machine Learning Model

To upgrade the classifier model:
1. Export your trained vectorizer to `backend/app/services/ai/recruitsafe_vectorizer.pkl`.
2. Export your trained XGBoost booster to `backend/app/services/ai/recruitsafe_xgb.pkl`.
3. Update `backend/app/services/ai/metadata.json` with the new version tags:
   ```json
   {
     "model_name": "recruitsafe_xgb",
     "model_version": "2.0.0",
     "dataset_version": "2.5.0",
     "algorithm": "XGBoost",
     "trained_at": "2026-07-24"
   }
   ```
4. Verify the model loads successfully on server boot by calling the `/api/ml/health` endpoint.

---

## 📊 4. Modifying Fusion Engine Calibration Weights

You can adjust how heavily the rule engine, external verifications, or ML predictions influence the final composite verdict without changing any Python source code:
1. Open `backend/app/config/fusion_config.json`.
2. Modify the weights percentages (the sum of the three main categories must equal `1.0`):
   ```json
   {
     "rules_weight": 0.40,
     "verification_weight": 0.35,
     "ml_weight": 0.25
   }
   ```
3. Save the file. The `DecisionFusionEngine` will read and apply the updated calculations on the next analysis request.
