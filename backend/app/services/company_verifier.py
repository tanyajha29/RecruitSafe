from typing import Dict, Any, Tuple, Optional

class CompanyVerifier:
    """
    Evaluates corporate footprint indicators from deterministic verifiers
    to determine structured verification levels (Verified, Partially Verified, Unable to Verify).
    """

    @classmethod
    def verify_company(cls, email_data: Optional[Dict[str, Any]], website_data: Optional[Dict[str, Any]]) -> Tuple[str, Dict[str, str]]:
        """
        Runs footprint verification checks.
        Returns:
            overall_status: "Verified", "Partially Verified", "Unable to Verify"
            panel: Structured verification panel mapped to front-end indicators
        """
        panel = {
            "Website": "Unknown",
            "Corporate Email": "Unknown",
            "DNS": "Unknown",
            "SSL": "Unknown",
            "WHOIS": "Unknown",
            "LinkedIn": "Unknown",
            "Privacy Policy": "Unknown",
            "Terms": "Unknown",
            "Careers Page": "Unknown",
            "Domain Age": "Unknown"
        }

        # 1. Email footprint checks
        has_email = email_data is not None and email_data.get("sender_email") != ""
        if has_email:
            panel["Corporate Email"] = email_data.get("verification_status", "Unknown")
        else:
            panel["Corporate Email"] = "Unknown"  # Not present is mapped to Unknown for verification status

        # 2. Website footprint checks
        has_website = website_data is not None
        if has_website:
            dns_info = website_data.get("dns", {})
            ssl_info = website_data.get("ssl", {})
            whois_info = website_data.get("whois", {})

            # DNS Check
            if dns_info.get("resolves", False):
                panel["DNS"] = "Reachable"
            else:
                panel["DNS"] = "Unreachable"

            # SSL Check
            if panel["DNS"] == "Reachable":
                panel["SSL"] = "Valid" if ssl_info.get("has_valid_ssl", False) else "Invalid"
            else:
                panel["SSL"] = "Unknown"

            # WHOIS Check
            if whois_info and not whois_info.get("whois_failed", True):
                panel["WHOIS"] = "Available"
                
                # Format Domain Age
                age_days = whois_info.get("domain_age_days")
                if age_days is not None:
                    if age_days >= 365:
                        years = age_days // 365
                        panel["Domain Age"] = f"{years} Year" + ("s" if years != 1 else "")
                    else:
                        months = age_days // 30
                        panel["Domain Age"] = f"{months} Month" + ("s" if months != 1 else "")
                else:
                    panel["Domain Age"] = "Unknown"
            else:
                panel["WHOIS"] = "Not Found"
                panel["Domain Age"] = "Unknown"

            # Crawled signals checks
            panel["LinkedIn"] = "Found" if website_data.get("has_linkedin", False) else "Not Found"
            panel["Privacy Policy"] = "Found" if website_data.get("has_privacy_policy", False) else "Not Found"
            panel["Terms"] = "Found" if website_data.get("has_terms_conditions", False) else "Not Found"
            panel["Careers Page"] = "Found" if website_data.get("has_careers", False) else "Not Found"

            # Website overall resolution
            if panel["DNS"] == "Unreachable":
                panel["Website"] = "Unreachable"
            elif panel["SSL"] == "Valid" and panel["WHOIS"] == "Available":
                panel["Website"] = "Verified"
            else:
                panel["Website"] = "Partially Verified"
        else:
            panel["Website"] = "Unknown"
            panel["DNS"] = "Unknown"
            panel["SSL"] = "Unknown"
            panel["WHOIS"] = "Unknown"
            panel["LinkedIn"] = "Unknown"
            panel["Privacy Policy"] = "Unknown"
            panel["Terms"] = "Unknown"
            panel["Careers Page"] = "Unknown"
            panel["Domain Age"] = "Unknown"

        # 3. Overall Verification Status logic
        is_website_verified = panel["Website"] == "Verified"
        is_email_verified = panel["Corporate Email"] == "Verified"

        # Check if WHOIS domain age exceeds 5 years (1825 days)
        is_old_domain = False
        if website_data and website_data.get("whois"):
            age = website_data["whois"].get("domain_age_days")
            if age is not None and age >= 1825:
                is_old_domain = True

        if is_email_verified and (is_website_verified or is_old_domain):
            overall_status = "Verified"
        elif is_email_verified or is_website_verified or is_old_domain or panel["WHOIS"] == "Available":
            overall_status = "Partially Verified"
        else:
            overall_status = "Unable to Verify"

        return overall_status, panel
