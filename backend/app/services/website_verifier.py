import re
import ssl
import socket
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List

import httpx
import tldextract
import whois
import dns.resolver
from bs4 import BeautifulSoup

from app.models.cache import CacheEntry

logger = logging.getLogger("recruitsafe")

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "rebrand.ly", "is.gd", "buff.ly", "adf.ly"}

class WebsiteVerifier:
    """
    Modular, deterministic service to check domain structures, DNS status,
    HTTPS availability, SSL validation, WHOIS age, HTTP redirects, and crawl page layouts.
    """

    @staticmethod
    def extract_url(text: str) -> Optional[str]:
        """Extracts the first valid URL from job text."""
        if not text:
            return None
        match = re.search(r'https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*', text)
        if match:
            return match.group(0)
        # Look for domain patterns without schema, e.g. company.com
        match_domain = re.search(r'\b(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})\b', text)
        if match_domain:
            domain = match_domain.group(1)
            # Filter out email addresses
            if "@" + domain not in text:
                return "https://" + domain
        return None

    @staticmethod
    def parse_domain(url: str) -> str:
        """Parses clean domain via tldextract."""
        if not url:
            return ""
        extracted = tldextract.extract(url)
        if extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}".lower().strip()
        return extracted.domain.lower().strip()

    @classmethod
    async def verify_dns(cls, domain: str) -> Dict[str, Any]:
        """Performs A record lookup via dnspython."""
        result = {"resolves": False, "ips": []}
        clean_domain = domain.lower().strip()
        if not clean_domain:
            return result

        try:
            answers = dns.resolver.resolve(clean_domain, 'A')
            result["resolves"] = len(answers) > 0
            result["ips"] = [str(rdata) for rdata in answers]
        except Exception:
            result["resolves"] = False
        return result

    @classmethod
    async def check_ssl_cert(cls, domain: str) -> Dict[str, Any]:
        """Retrieves and validates SSL details over socket connection with caching."""
        clean_domain = domain.lower().strip()
        result = {
            "has_valid_ssl": False,
            "issuer": None,
            "expiration_date": None,
            "error": None
        }

        if not clean_domain:
            return result

        cache_key = f"ssl_v2_2:{clean_domain}"
        try:
            cached = await CacheEntry.find_one({"key": cache_key})
            if cached and cached.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                val = cached.value
                exp_date = datetime.fromisoformat(val["expiration_date"]) if val.get("expiration_date") else None
                return {
                    "has_valid_ssl": val["has_valid_ssl"],
                    "issuer": val["issuer"],
                    "expiration_date": exp_date,
                    "error": val.get("error")
                }
        except Exception as e:
            logger.warning(f"Cache lookup failed for SSL {clean_domain}: {e}")

        context = ssl.create_default_context()
        context.timeout = 3.0

        try:
            with socket.create_connection((clean_domain, 443), timeout=3.0) as sock:
                with context.wrap_socket(sock, server_hostname=clean_domain) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        issuer = dict(x[0] for x in cert.get('issuer', []))
                        result["issuer"] = issuer.get('commonName')
                        not_after_str = cert.get('notAfter')
                        if not_after_str:
                            try:
                                result["expiration_date"] = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                            except ValueError:
                                pass
                        
                        has_valid = True
                        if result["expiration_date"]:
                            now = datetime.now() if result["expiration_date"].tzinfo is None else datetime.now(timezone.utc)
                            if now > result["expiration_date"]:
                                has_valid = False
                        result["has_valid_ssl"] = has_valid
        except Exception as e:
            result["error"] = str(e)
            result["has_valid_ssl"] = False

        # Cache result
        try:
            cache_val = {
                "has_valid_ssl": result["has_valid_ssl"],
                "issuer": result["issuer"],
                "expiration_date": result["expiration_date"].isoformat() if result["expiration_date"] else None,
                "error": result["error"]
            }
            await CacheEntry.find_one({"key": cache_key}).upsert(
                {"$set": {
                    "value": cache_val,
                    "expires_at": datetime.utcnow() + timedelta(days=7)
                }},
                on_insert=CacheEntry(
                    key=cache_key,
                    value=cache_val,
                    expires_at=datetime.utcnow() + timedelta(days=7)
                )
            )
        except Exception as e:
            logger.warning(f"Failed to cache SSL for {clean_domain}: {e}")

        return result

    @classmethod
    async def get_whois_record(cls, domain: str) -> Dict[str, Any]:
        """Resolves WHOIS details with 7-day persistent caching."""
        clean_domain = domain.lower().strip()
        result = {
            "domain_age_days": None,
            "registration_date": None,
            "expiration_date": None,
            "registrar": None,
            "country": None,
            "whois_failed": True
        }

        if not clean_domain:
            return result

        cache_key = f"whois_v2_2:{clean_domain}"
        try:
            cached = await CacheEntry.find_one({"key": cache_key})
            if cached and cached.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                val = cached.value
                reg_date = datetime.fromisoformat(val["registration_date"]) if val.get("registration_date") else None
                exp_date = datetime.fromisoformat(val["expiration_date"]) if val.get("expiration_date") else None
                return {
                    "domain_age_days": val["domain_age_days"],
                    "registration_date": reg_date,
                    "expiration_date": exp_date,
                    "registrar": val["registrar"],
                    "country": val["country"],
                    "whois_failed": val["whois_failed"]
                }
        except Exception as e:
            logger.warning(f"Cache lookup failed for WHOIS {clean_domain}: {e}")

        try:
            w = whois.whois(clean_domain)
            if not w or not hasattr(w, "creation_date") or not w.creation_date:
                raise ValueError("WHOIS creation_date missing or invalid record format.")

            reg_date = None
            if isinstance(w.creation_date, list):
                dates = [d for d in w.creation_date if isinstance(d, datetime)]
                if dates:
                    reg_date = dates[0]
            elif isinstance(w.creation_date, datetime):
                reg_date = w.creation_date

            if not reg_date:
                raise ValueError("WHOIS creation date could not be parsed into a valid datetime object.")

            exp_date = None
            if w.expiration_date:
                if isinstance(w.expiration_date, list):
                    dates = [d for d in w.expiration_date if isinstance(d, datetime)]
                    if dates:
                        exp_date = dates[0]
                elif isinstance(w.expiration_date, datetime):
                    exp_date = w.expiration_date

            now = datetime.now() if reg_date.tzinfo is None else datetime.now(timezone.utc)
            age_days = (now - reg_date).days

            if age_days < 0:
                raise ValueError(f"Calculated domain age is negative: {age_days}")

            registrar = w.registrar[0] if isinstance(w.registrar, list) else w.registrar
            country = w.country[0] if isinstance(w.country, list) else w.country

            result = {
                "domain_age_days": age_days,
                "registration_date": reg_date,
                "expiration_date": exp_date,
                "registrar": str(registrar) if registrar else None,
                "country": str(country) if country else None,
                "whois_failed": False
            }
        except Exception as e:
            logger.warning(f"WHOIS parsing failure for {clean_domain}: {e}")
            result["whois_failed"] = True

        # Cache result
        try:
            cache_val = {
                "domain_age_days": result["domain_age_days"],
                "registrar": result["registrar"],
                "country": result["country"],
                "registration_date": result["registration_date"].isoformat() if result["registration_date"] else None,
                "expiration_date": result["expiration_date"].isoformat() if result["expiration_date"] else None,
                "whois_failed": result["whois_failed"]
            }
            await CacheEntry.find_one({"key": cache_key}).upsert(
                {"$set": {
                    "value": cache_val,
                    "expires_at": datetime.utcnow() + timedelta(days=7)
                }},
                on_insert=CacheEntry(
                    key=cache_key,
                    value=cache_val,
                    expires_at=datetime.utcnow() + timedelta(days=7)
                )
            )
        except Exception as e:
            logger.warning(f"Failed to cache WHOIS for {clean_domain}: {e}")

        return result

    @classmethod
    async def verify_website(cls, url: str, careers_url_exists: bool = False) -> Dict[str, Any]:
        """Crawl website homepage, extract meta indicators, schema markup, and checks HTTPS."""
        normalized_url = url.strip()
        if not re.match(r'^https?://', normalized_url, re.IGNORECASE):
            normalized_url = "http://" + normalized_url

        if careers_url_exists:
            logger.info(f"WebsiteVerifier: Careers URL already extracted from job listing. Skipping active search.")

        result = {
            "url": url,
            "final_url": normalized_url,
            "is_reachable": False,
            "has_redirects": False,
            "redirect_hops": 0,
            "is_shortened": False,
            "page_title": None,
            "meta_description": None,
            "has_privacy_policy": False,
            "has_terms_conditions": False,
            "has_careers": True if careers_url_exists else False,
            "has_contact": False,
            "has_linkedin": False,
            "has_organization_schema": False,
            "linkedin_company_url": None,
            "dns": {"resolves": False, "ips": []},
            "ssl": {"has_valid_ssl": False, "issuer": None, "expiration_date": None},
            "whois": {"domain_age_days": None, "registrar": None, "country": None, "whois_failed": True}
        }

        domain = cls.parse_domain(normalized_url)
        if domain in SHORTENERS:
            result["is_shortened"] = True

        # 1. DNS Resolution Check
        dns_res = await cls.verify_dns(domain)
        result["dns"] = dns_res

        # 2. SSL checks
        ssl_res = await cls.check_ssl_cert(domain)
        result["ssl"] = ssl_res

        # 3. WHOIS check
        whois_res = await cls.get_whois_record(domain)
        result["whois"] = whois_res

        # 4. HTTP Reachability and crawling via httpx
        try:
            async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
                response = await client.get(normalized_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RecruitSafe/2.2"
                })
                result["is_reachable"] = response.status_code == 200
                result["final_url"] = str(response.url)
                result["redirect_hops"] = len(response.history)
                result["has_redirects"] = len(response.history) > 0

                # Analyze content via BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Page title
                if soup.title and soup.title.string:
                    result["page_title"] = soup.title.string.strip()

                # Meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    result["meta_description"] = meta_desc.get('content').strip()

                # Links and Text Scanning
                links = [a.get('href', '').lower() for a in soup.find_all('a', href=True)]
                page_text = soup.get_text().lower()

                # Privacy Policy check
                result["has_privacy_policy"] = any("privacy" in link for link in links) or "privacy policy" in page_text

                # Terms & Conditions check
                result["has_terms_conditions"] = any("terms" in link or "condition" in link for link in links) or "terms of service" in page_text or "terms and conditions" in page_text

                # Careers Page check
                if careers_url_exists:
                    result["has_careers"] = True
                else:
                    result["has_careers"] = any(k in link for link in links for k in ["career", "job", "join", "hiring", "recruit"]) or "careers" in page_text

                # Contact Page check
                result["has_contact"] = any("contact" in link or "support" in link for link in links) or "contact us" in page_text

                # LinkedIn Link check
                linkedin_links = [a.get('href') for a in soup.find_all('a', href=True) if "linkedin.com/company" in a.get('href', '')]
                if linkedin_links:
                    result["has_linkedin"] = True
                    result["linkedin_company_url"] = linkedin_links[0]

                # schema.org structured data Organization check
                scripts = soup.find_all('script', type='application/ld+json')
                for script in scripts:
                    try:
                        content = script.string or ""
                        if '"Organization"' in content or '"@context": "https://schema.org"' in content:
                            result["has_organization_schema"] = True
                            break
                    except Exception:
                        pass

        except Exception as e:
            logger.warning(f"HTTP fetch failed for WebsiteVerifier: {normalized_url} - {e}")
            result["is_reachable"] = False

        return result
