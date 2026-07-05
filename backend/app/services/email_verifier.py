import re
import socket
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

import dns.resolver
from email_validator import validate_email, EmailNotValidError

try:
    from rapidfuzz.distance import Levenshtein
except ImportError:
    class Levenshtein:
        @staticmethod
        def distance(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return Levenshtein.distance(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

from app.models.cache import CacheEntry

logger = logging.getLogger("recruitsafe")

FREE_DOMAINS = {
    "gmail.com", "yahoo.com", "yahoo.co.in", "outlook.com", "hotmail.com", 
    "aol.com", "zoho.com", "mail.com", "yandex.com", "protonmail.com",
    "proton.me", "gmx.com", "icloud.com", "mail.ru", "live.com"
}

DISPOSABLE_DOMAINS = {
    "mailinator.com", "10minutemail.com", "tempmail.com", "guerrillamail.com",
    "sharklasers.com", "dispostable.com", "yopmail.com", "trashmail.com"
}

class EmailVerifier:
    """
    Modular service to verify email syntax, DNS MX presence, disposable status,
    and typosquatting likeness against official corporate domains.
    """

    @staticmethod
    def validate_syntax(email: str) -> bool:
        """Validates email format syntax via email-validator."""
        try:
            validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False

    @staticmethod
    def extract_domain(email: str) -> str:
        """Extracts the domain portion of an email address."""
        if not email or "@" not in email:
            return ""
        return email.split("@")[-1].lower().strip()

    @classmethod
    def is_free(cls, domain: str) -> bool:
        return domain.lower().strip() in FREE_DOMAINS

    @classmethod
    def is_disposable(cls, domain: str) -> bool:
        return domain.lower().strip() in DISPOSABLE_DOMAINS

    @classmethod
    async def verify_dns_mx(cls, domain: str) -> Dict[str, Any]:
        """Queries DNS MX & A records with caching."""
        clean_domain = domain.lower().strip()
        result = {
            "dns_exists": False,
            "has_mx": False,
            "has_spf": False,
            "has_dmarc": False
        }

        if not clean_domain or cls.is_free(clean_domain) or cls.is_disposable(clean_domain):
            return result

        cache_key = f"email_dns:{clean_domain}"
        try:
            cached = await CacheEntry.find_one({"key": cache_key})
            if cached and cached.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                return cached.value
        except Exception as e:
            logger.warning(f"Cache check failed in EmailVerifier: {e}")

        try:
            # 1. Resolve IP (A record)
            try:
                socket.gethostbyname(clean_domain)
                result["dns_exists"] = True
            except Exception:
                result["dns_exists"] = False

            # 2. Resolve MX records
            try:
                mx_answers = dns.resolver.resolve(clean_domain, 'MX')
                result["has_mx"] = len(mx_answers) > 0
                if result["has_mx"]:
                    result["dns_exists"] = True
            except Exception:
                result["has_mx"] = False

            # 3. Resolve SPF
            try:
                txt_answers = dns.resolver.resolve(clean_domain, 'TXT')
                for txt in txt_answers:
                    txt_str = "".join([t.decode('utf-8') if isinstance(t, bytes) else str(t) for t in txt.strings])
                    if "v=spf1" in txt_str.lower():
                        result["has_spf"] = True
                        break
            except Exception:
                result["has_spf"] = False

            # 4. Resolve DMARC
            try:
                dmarc_answers = dns.resolver.resolve(f"_dmarc.{clean_domain}", 'TXT')
                for txt in dmarc_answers:
                    txt_str = "".join([t.decode('utf-8') if isinstance(t, bytes) else str(t) for t in txt.strings])
                    if "v=dmarc1" in txt_str.lower():
                        result["has_dmarc"] = True
                        break
            except Exception:
                result["has_dmarc"] = False

        except Exception as e:
            logger.warning(f"DNS lookup failed for email domain {clean_domain}: {e}")

        # Cache result
        try:
            await CacheEntry.find_one({"key": cache_key}).upsert(
                {"$set": {
                    "value": result,
                    "expires_at": datetime.utcnow() + timedelta(days=7)
                }},
                on_insert=CacheEntry(
                    key=cache_key,
                    value=result,
                    expires_at=datetime.utcnow() + timedelta(days=7)
                )
            )
        except Exception as e:
            logger.warning(f"Cache save failed in EmailVerifier: {e}")

        return result

    @classmethod
    def check_typosquatting(cls, email_domain: str, company_domain: str) -> Dict[str, Any]:
        """Compares recruiter domain with official company domain to detect similarity likeness."""
        e_dom = email_domain.lower().strip().replace("www.", "")
        c_dom = company_domain.lower().strip().replace("www.", "")

        result = {
            "is_exact_match": False,
            "is_suspicious_typosquatting": False,
            "distance": 0,
            "reason": ""
        }

        if not e_dom or not c_dom:
            return result

        if e_dom == c_dom:
            result["is_exact_match"] = True
            return result

        if cls.is_free(e_dom) or cls.is_disposable(e_dom):
            result["reason"] = "Recruiter email domain belongs to a public or disposable provider."
            return result

        dist = Levenshtein.distance(e_dom, c_dom)
        result["distance"] = dist

        if 1 <= dist <= 3:
            result["is_suspicious_typosquatting"] = True
            result["reason"] = f"Email domain '{email_domain}' closely resembles company domain '{company_domain}' (distance: {dist})."
            return result

        c_name = c_dom.split(".")[0]
        if c_name in e_dom and len(e_dom) > len(c_dom):
            result["is_suspicious_typosquatting"] = True
            result["reason"] = f"Email domain '{email_domain}' uses company name with an unofficial suffix."
            return result

        result["reason"] = "Recruiter domain does not match official company domain."
        return result

    @classmethod
    def inspect_security_headers(cls, headers_text: str) -> Dict[str, bool]:
        """
        Parses security authentication headers from raw email (.eml) data.
        Looks for SPF, DKIM, and DMARC alignments.
        """
        result = {"spf_pass": False, "dkim_pass": False, "dmarc_pass": False}
        if not headers_text:
            return result

        lines = headers_text.splitlines()
        for line in lines:
            if re.search(r'spf\s*=\s*pass', line, re.IGNORECASE) or "Received-SPF: pass" in line:
                result["spf_pass"] = True
            if re.search(r'dkim\s*=\s*pass', line, re.IGNORECASE):
                result["dkim_pass"] = True
            if re.search(r'dmarc\s*=\s*pass', line, re.IGNORECASE):
                result["dmarc_pass"] = True
        return result

    @classmethod
    async def verify_recruiter_email(cls, email: str, company_domain: Optional[str] = None, eml_headers: Optional[str] = None) -> Dict[str, Any]:
        """Executes full Email Verification checks."""
        clean_email = email.strip()
        domain = cls.extract_domain(clean_email)
        is_valid = cls.validate_syntax(clean_email)

        result = {
            "sender_email": clean_email,
            "domain": domain,
            "is_valid_format": is_valid,
            "domain_exists": False,
            "is_free_email": cls.is_free(domain),
            "is_disposable": cls.is_disposable(domain),
            "dns_records": {"has_mx": False, "has_spf": False, "has_dmarc": False},
            "typosquatting_check": None,
            "security_headers": {"spf_pass": False, "dkim_pass": False, "dmarc_pass": False},
            "verification_status": "Unknown"
        }

        if not is_valid or not domain:
            result["verification_status"] = "Invalid"
            return result

        # Run DNS & MX checks
        dns_res = await cls.verify_dns_mx(domain)
        result["dns_records"] = dns_res
        result["domain_exists"] = dns_res["dns_exists"]

        # Parse security headers if eml_headers are provided
        if eml_headers:
            result["security_headers"] = cls.inspect_security_headers(eml_headers)

        # Typosquatting checks
        if company_domain:
            result["typosquatting_check"] = cls.check_typosquatting(domain, company_domain)

        # Determine verification status
        if result["is_disposable"] or (not result["is_free_email"] and not result["domain_exists"]):
            result["verification_status"] = "Invalid"
        elif result["is_free_email"]:
            result["verification_status"] = "Unknown"  # Public email cannot be verified as corporate
        else:
            # Corporate domain
            if dns_res["has_mx"]:
                result["verification_status"] = "Verified"
            else:
                result["verification_status"] = "Verification Pending"

        return result
