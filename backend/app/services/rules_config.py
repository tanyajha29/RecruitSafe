import os
from typing import Dict

# Configurable rule weights mapping. Can be overridden by environment variables if set.
RULE_WEIGHTS: Dict[str, int] = {
    # Positive Rules
    "official_corporate_email": int(os.getenv("RS_WEIGHT_CORP_EMAIL", 20)),
    "https": int(os.getenv("RS_WEIGHT_HTTPS", 10)),
    "whois_available": int(os.getenv("RS_WEIGHT_WHOIS", 8)),
    "valid_ssl": int(os.getenv("RS_WEIGHT_SSL", 8)),
    "domain_age_old": int(os.getenv("RS_WEIGHT_DOMAIN_AGE", 15)),
    "structured_hiring_process": int(os.getenv("RS_WEIGHT_HIRING_PROCESS", 10)),
    
    # Negative Rules
    "payment_request": int(os.getenv("RS_WEIGHT_PAYMENT_REQUEST", -50)),
    "telegram_only": int(os.getenv("RS_WEIGHT_TELEGRAM_ONLY", -40)),
    "whatsapp_only": int(os.getenv("RS_WEIGHT_WHATSAPP_ONLY", -40)),
    "no_interview": int(os.getenv("RS_WEIGHT_NO_INTERVIEW", -35)),
    "immediate_joining": int(os.getenv("RS_WEIGHT_IMMEDIATE_JOINING", -20)),
    "too_good_salary": int(os.getenv("RS_WEIGHT_TOO_GOOD_SALARY", -25)),
    "poor_grammar": int(os.getenv("RS_WEIGHT_POOR_GRAMMAR", -10)),
    "free_email": int(os.getenv("RS_WEIGHT_FREE_EMAIL", -20)),
    "no_company_name": int(os.getenv("RS_WEIGHT_NO_COMPANY_NAME", -20))
}

RULE_EXPLANATIONS: Dict[str, str] = {
    "official_corporate_email": "Official corporate email domain verifies employer identity.",
    "https": "Secure HTTPS connection prevents communications sniffing and man-in-the-middle attacks.",
    "whois_available": "WHOIS registry details are verified and queryable.",
    "valid_ssl": "Valid SSL certificate issued by a trusted Certificate Authority.",
    "domain_age_old": "Established web presence older than 2 years reduces likelihood of burn-and-replace scams.",
    "structured_hiring_process": "Multi-stage structured interview loop reduces hiring fraud risk.",
    
    "payment_request": "Asking candidates to pay for training, processing, or devices is a major scam indicator.",
    "telegram_only": "Using Telegram for candidate screening avoids corporate logging controls.",
    "whatsapp_only": "Communication restricted to personal WhatsApp numbers avoids official HR audits.",
    "no_interview": "Direct selection/hiring promises without screening bypass standard competency evaluations.",
    "immediate_joining": "High-urgency immediate start pressure forces quick, unverified actions.",
    "too_good_salary": "Offering compensation packages significantly above market average is a phishing trap.",
    "poor_grammar": "Job posting text contains systemic grammatical errors and spelling anomalies.",
    "free_email": "Recruiting contacts use public free email providers instead of official brand domains.",
    "no_company_name": "Employer name is omitted or anonymous, preventing standard candidate checks."
}
