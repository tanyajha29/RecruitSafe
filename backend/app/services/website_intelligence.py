import re
import socket
import ssl
import logging
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List

import whois
from app.models.cache import CacheEntry

logger = logging.getLogger("recruitsafe")

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "rebrand.ly", "is.gd", "buff.ly", "adf.ly"}

class WebsiteIntelligence:
    """
    Service to analyze company domains, WHOIS records, SSL certificates,
    and inspect websites for positive safety signals (Privacy, Terms, Careers, LinkedIn).
    """

    @staticmethod
    def extract_domain(url: str) -> str:
        """
        Extracts clean domain name from URL or email address.
        e.g. https://www.google.com/search -> google.com
        """
        if not url:
            return ""
        
        # Clean email format
        if "@" in url:
            url = url.split("@")[-1]
            
        # Clean protocol prefixes
        domain = url.strip().lower()
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'^www\.', '', domain)
        
        # Split paths or queries
        domain = domain.split("/")[0]
        domain = domain.split(":")[0]  # Remove port
        return domain

    @classmethod
    async def get_domain_whois(cls, domain: str) -> Dict[str, Any]:
        """
        Retrieves WHOIS information for a domain with persistent caching.
        """
        clean_domain = cls.extract_domain(domain)
        if not clean_domain:
            return {
                "domain_age_days": None,
                "registration_date": None,
                "expiration_date": None,
                "registrar": None,
                "country": None,
                "whois_failed": True
            }

        # Check Cache first
        cache_key = f"whois:{clean_domain}"
        try:
            cached = await CacheEntry.find_one({"key": cache_key})
            if cached and cached.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                logger.info(f"Persistent Cache HIT: WHOIS for {clean_domain}")
                val = cached.value
                # Deserialize dates
                reg_date = datetime.fromisoformat(val["registration_date"]) if val.get("registration_date") else None
                exp_date = datetime.fromisoformat(val["expiration_date"]) if val.get("expiration_date") else None
                return {
                    "domain_age_days": val.get("domain_age_days"),
                    "registration_date": reg_date,
                    "expiration_date": exp_date,
                    "registrar": val.get("registrar"),
                    "country": val.get("country"),
                    "whois_failed": val.get("whois_failed", False)
                }
        except Exception as e:
            logger.warning(f"Cache lookup failed for WHOIS {clean_domain}: {e}")

        logger.info(f"Persistent Cache MISS: Performing live WHOIS lookup for {clean_domain}")
        
        try:
            w = whois.whois(clean_domain)
            
            reg_date: Optional[datetime] = None
            if w.creation_date:
                if isinstance(w.creation_date, list):
                    reg_date = w.creation_date[0]
                else:
                    reg_date = w.creation_date

            exp_date: Optional[datetime] = None
            if w.expiration_date:
                if isinstance(w.expiration_date, list):
                    exp_date = w.expiration_date[0]
                else:
                    exp_date = w.expiration_date

            age_days: Optional[int] = None
            if reg_date:
                if reg_date.tzinfo is None:
                    now = datetime.now()
                else:
                    now = datetime.now(timezone.utc)
                age_days = (now - reg_date).days

            registrar = w.registrar
            if isinstance(registrar, list) and len(registrar) > 0:
                registrar = registrar[0]
                
            country = w.country
            if isinstance(country, list) and len(country) > 0:
                country = country[0]

            # If no registration date and no registrar, the lookup failed
            if not reg_date and not registrar:
                raise Exception("WHOIS returned empty records")

            result = {
                "domain_age_days": age_days,
                "registration_date": reg_date,
                "expiration_date": exp_date,
                "registrar": str(registrar) if registrar else None,
                "country": str(country) if country else None,
                "whois_failed": False
            }
        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {clean_domain}: {e}. Returning fallback.")
            result = {
                "domain_age_days": None,
                "registration_date": None,
                "expiration_date": None,
                "registrar": None,
                "country": None,
                "whois_failed": True
            }

        # Save to Cache
        try:
            cache_val = {
                "domain_age_days": result["domain_age_days"],
                "registrar": result["registrar"],
                "country": result["country"],
                "registration_date": result["registration_date"].isoformat() if result["registration_date"] else None,
                "expiration_date": result["expiration_date"].isoformat() if result["expiration_date"] else None,
                "whois_failed": result["whois_failed"]
            }
            # Upsert cache entry
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
    async def check_ssl(cls, domain: str) -> Dict[str, Any]:
        """
        Connects to port 443 to extract and verify the SSL certificate with persistent caching.
        """
        clean_domain = cls.extract_domain(domain)
        result = {
            "has_valid_ssl": False,
            "issuer": None,
            "expiration_date": None
        }

        if not clean_domain:
            return result

        # Check Cache first
        cache_key = f"ssl:{clean_domain}"
        try:
            cached = await CacheEntry.find_one({"key": cache_key})
            if cached and cached.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                logger.info(f"Persistent Cache HIT: SSL check for {clean_domain}")
                val = cached.value
                exp_date = datetime.fromisoformat(val["expiration_date"]) if val.get("expiration_date") else None
                return {
                    "has_valid_ssl": val.get("has_valid_ssl"),
                    "issuer": val.get("issuer"),
                    "expiration_date": exp_date
                }
        except Exception as e:
            logger.warning(f"Cache lookup failed for SSL {clean_domain}: {e}")

        logger.info(f"Persistent Cache MISS: Performing SSL check for {clean_domain}")
        
        context = ssl.create_default_context()
        context.timeout = 3.0

        try:
            with socket.create_connection((clean_domain, 443), timeout=3.0) as sock:
                with context.wrap_socket(sock, server_hostname=clean_domain) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        issuer = dict(x[0] for x in cert.get('issuer', []))
                        common_name = issuer.get('commonName', None)
                        
                        not_after_str = cert.get('notAfter')
                        expiry_date = None
                        if not_after_str:
                            try:
                                expiry_date = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                            except ValueError:
                                pass
                                
                        has_valid = True
                        if expiry_date:
                            if expiry_date.tzinfo is None:
                                now = datetime.now()
                            else:
                                now = datetime.now(timezone.utc)
                            if now > expiry_date:
                                has_valid = False
                                
                        result["has_valid_ssl"] = has_valid
                        result["issuer"] = common_name
                        result["expiration_date"] = expiry_date
        except Exception as e:
            logger.warning(f"SSL certificate check failed for {clean_domain}: {e}")

        # Save to Cache
        try:
            cache_val = {
                "has_valid_ssl": result["has_valid_ssl"],
                "issuer": result["issuer"],
                "expiration_date": result["expiration_date"].isoformat() if result["expiration_date"] else None
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
    async def analyze_url(cls, url: str) -> Dict[str, Any]:
        """
        Follows redirect chain and extracts page title, meta description, and parses page content
        for positive layout components.
        """
        normalized_url = url.strip()
        if not re.match(r'^https?://', normalized_url, re.IGNORECASE):
            normalized_url = "http://" + normalized_url

        result = {
            "url": url,
            "final_url": normalized_url,
            "has_redirects": False,
            "redirect_hops": 0,
            "is_shortened": False,
            "page_title": None,
            "meta_description": None,
            # Version 2.0 Web Scraping signals
            "has_privacy_policy": False,
            "has_terms_conditions": False,
            "has_careers": False,
            "has_linkedin": False
        }

        domain = cls.extract_domain(normalized_url)
        if domain in SHORTENERS:
            result["is_shortened"] = True

        # Check Cache first
        cache_key = f"url_analysis:{normalized_url}"
        try:
            cached = await CacheEntry.find_one({"key": cache_key})
            if cached and cached.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                logger.info(f"Persistent Cache HIT: URL analysis for {normalized_url}")
                return cached.value
        except Exception as e:
            logger.warning(f"Cache lookup failed for URL {normalized_url}: {e}")

        logger.info(f"Persistent Cache MISS: Performing live URL scrape for {normalized_url}")
        
        try:
            response = requests.get(
                normalized_url, 
                allow_redirects=True, 
                timeout=5.0, 
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RecruitSafe/2.0"}
            )
            
            result["final_url"] = response.url
            hops = len(response.history)
            result["redirect_hops"] = hops
            
            if hops > 0:
                result["has_redirects"] = True
                
            content = response.text
            
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                result["page_title"] = title_match.group(1).strip()
                
            desc_match = re.search(
                r'<meta\s+[^>]*name=["\']description["\']\s+[^>]*content=["\'](.*?)["\']', 
                content, 
                re.IGNORECASE | re.DOTALL
            )
            if not desc_match:
                desc_match = re.search(
                    r'<meta\s+[^>]*content=["\'](.*?)["\']\s+[^>]*name=["\']description["\']', 
                    content, 
                    re.IGNORECASE | re.DOTALL
                )
            if desc_match:
                result["meta_description"] = desc_match.group(1).strip()

            # Search content body for V2 positive indicators
            result["has_privacy_policy"] = bool(re.search(
                r'\b(?:privacy\s+policy|privacy|data\s+protection)\b', 
                content, re.IGNORECASE
            ))
            result["has_terms_conditions"] = bool(re.search(
                r'\b(?:terms\s+of\s+(?:use|service)|terms\s+and\s+conditions|terms|conditions)\b', 
                content, re.IGNORECASE
            ))
            result["has_careers"] = bool(re.search(
                r'\b(?:careers?|jobs?|work\s+with\s+us|hiring|job\s+opportunities)\b', 
                content, re.IGNORECASE
            ))
            result["has_linkedin"] = "linkedin.com/company" in content.lower()

        except Exception as e:
            logger.warning(f"URL analysis request failed for {normalized_url}: {e}")

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
            logger.warning(f"Failed to cache URL analysis for {normalized_url}: {e}")

        return result
