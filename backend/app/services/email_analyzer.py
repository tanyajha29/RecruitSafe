import dns.resolver
import socket
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List

from app.models.cache import CacheEntry
from app.services.website_intelligence import WebsiteIntelligence

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

def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes the Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
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

class EmailAnalyzer:
    @staticmethod
    def parse_domain(email: str) -> str:
        """Extracts the domain portion of an email address."""
        if not email or "@" not in email:
            return ""
        return email.split("@")[-1].lower().strip()

    @classmethod
    async def get_dns_records(cls, domain: str) -> Dict[str, Any]:
        """
        Queries and checks MX, SPF, and DMARC TXT records for a domain with persistent caching.
        """
        clean_domain = WebsiteIntelligence.extract_domain(domain)
        result = {
            "has_mx": False,
            "has_spf": False,
            "has_dmarc": False
        }

        if not clean_domain or clean_domain in FREE_DOMAINS or clean_domain in DISPOSABLE_DOMAINS:
            return result

        # Check Cache
        cache_key = f"dns:{clean_domain}"
        try:
            cached = await CacheEntry.find_one({"key": cache_key})
            if cached and cached.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                logger.info(f"Persistent Cache HIT: DNS records for {clean_domain}")
                return cached.value
        except Exception as e:
            logger.warning(f"Cache lookup failed for DNS {clean_domain}: {e}")

        logger.info(f"Persistent Cache MISS: Querying live DNS records for {clean_domain}")
        
        try:
            # 1. Resolve MX records
            try:
                mx_answers = dns.resolver.resolve(clean_domain, 'MX')
                result["has_mx"] = len(mx_answers) > 0
            except Exception:
                result["has_mx"] = False

            # 2. Resolve SPF (via TXT records)
            try:
                txt_answers = dns.resolver.resolve(clean_domain, 'TXT')
                for txt in txt_answers:
                    txt_str = "".join([t.decode('utf-8') if isinstance(t, bytes) else str(t) for t in txt.strings])
                    if "v=spf1" in txt_str.lower():
                        result["has_spf"] = True
                        break
            except Exception:
                result["has_spf"] = False

            # 3. Resolve DMARC (via _dmarc TXT records)
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
            logger.warning(f"DNS queries failed for {clean_domain}: {e}")

        # Save to Cache
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
            logger.warning(f"Failed to cache DNS for {clean_domain}: {e}")

        return result

    @classmethod
    async def check_typosquatting(cls, email_domain: str, company_domain: str) -> Dict[str, Any]:
        """
        Compares email domain against company official domain to detect lookalikes.
        """
        e_dom = email_domain.lower().strip()
        c_dom = company_domain.lower().strip()
        
        if e_dom.startswith("www."): e_dom = e_dom[4:]
        if c_dom.startswith("www."): c_dom = c_dom[4:]

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

        if e_dom in FREE_DOMAINS or e_dom in DISPOSABLE_DOMAINS:
            result["reason"] = "Recruiter is using a free public or disposable email domain."
            return result

        # Compute Levenshtein distance
        dist = levenshtein_distance(e_dom, c_dom)
        result["distance"] = dist

        # Small edit distance indicates highly likely typosquatting
        if 1 <= dist <= 3:
            result["is_suspicious_typosquatting"] = True
            result["reason"] = f"Recruiter domain '{email_domain}' closely resembles official company domain '{company_domain}' (edit distance: {dist})."
            return result

        # Substring lookalike check (e.g. company-hr.com vs company.com)
        c_name = c_dom.split(".")[0]
        if c_name in e_dom and dist > 3:
            result["is_suspicious_typosquatting"] = True
            result["reason"] = f"Recruiter domain '{email_domain}' contains company name but uses an unofficial domain suffix."
            return result

        result["reason"] = "Recruiter domain does not match official company domain."
        return result

    @classmethod
    async def analyze_recruiter_email(cls, email: str, company_website_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs full async recruiter email audit checking DNS lookups, typosquatting, and free domains.
        """
        clean_email = email.strip()
        domain = cls.parse_domain(clean_email)
        
        result = {
            "sender_email": clean_email,
            "domain": domain,
            "is_valid_format": bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', clean_email)),
            "domain_exists": False,
            "is_free_email": False,
            "is_disposable": False,
            "dns_records": {
                "has_mx": False,
                "has_spf": False,
                "has_dmarc": False
            },
            "typosquatting_check": None
        }

        if not domain:
            return result

        # DNS existence lookup
        try:
            socket.gethostbyname(domain)
            result["domain_exists"] = True
        except socket.gaierror:
            result["domain_exists"] = False

        if domain in FREE_DOMAINS:
            result["is_free_email"] = True
        if domain in DISPOSABLE_DOMAINS:
            result["is_disposable"] = True

        # DNS queries (MX, SPF, DMARC)
        dns_data = await cls.get_dns_records(domain)
        result["dns_records"] = dns_data

        # If MX is found, the domain technically resolves mail
        if dns_data["has_mx"]:
            result["domain_exists"] = True

        # Typosquatting checks
        if company_website_url:
            company_domain = WebsiteIntelligence.extract_domain(company_website_url)
            if company_domain:
                typo_data = await cls.check_typosquatting(domain, company_domain)
                result["typosquatting_check"] = typo_data

        return result
