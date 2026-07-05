from typing import Dict, Any, Tuple, Optional

class CompanyVerifier:
    """
    Evaluates corporate footprint indicators to determine structured
    verification levels for the job listing (Verified, Partially Verified, Unable to Verify).
    """

    @classmethod
    def verify_company(cls, email_data: Optional[Dict[str, Any]], website_data: Optional[Dict[str, Any]]) -> Tuple[str, Dict[str, str]]:
        """
        Runs the 10-layer company footprint check.
        Returns:
            overall_status: "Verified", "Partially Verified", "Unable to Verify"
            panel: Dictionary mapping check name to verification state
        """
        panel = {
            "Website": "Not Found",
            "Corporate Email": "Not Found",
            "WHOIS": "Not Found",
            "DNS": "Not Found",
            "SSL": "Unknown",
            "LinkedIn": "Not Found",
            "Privacy Policy": "Not Found",
            "Terms & Conditions": "Not Found",
            "Contact Page": "Not Found",
            "Careers Page": "Not Found"
        }

        # 1. Evaluate Website resolution
        has_website = website_data is not None
        if has_website:
            whois_info = website_data.get("whois", {})
            ssl_info = website_data.get("ssl", {})
            
            # DNS / Reachability
            dns_failed = whois_info.get("whois_failed", True) and not ssl_info.get("has_valid_ssl", False)
            if dns_failed:
                panel["DNS"] = "Invalid"  # Unreachable
                panel["Website"] = "Invalid"
            else:
                panel["DNS"] = "Verified"
                # Determine Website overall verification
                if ssl_info.get("has_valid_ssl") and not whois_info.get("whois_failed"):
                    panel["Website"] = "Verified"
                else:
                    panel["Website"] = "Partially Verified"

            # WHOIS
            if whois_info and not whois_info.get("whois_failed", True):
                panel["WHOIS"] = "Verified"
            else:
                panel["WHOIS"] = "Unknown"

            # SSL
            if ssl_info:
                panel["SSL"] = "Verified" if ssl_info.get("has_valid_ssl") else "Invalid"
            else:
                panel["SSL"] = "Unknown"

            # LinkedIn
            panel["LinkedIn"] = "Verified" if website_data.get("has_linkedin") else "Not Found"

            # Privacy Policy
            panel["Privacy Policy"] = "Verified" if website_data.get("has_privacy_policy") else "Not Found"

            # Terms & Conditions
            panel["Terms & Conditions"] = "Verified" if website_data.get("has_terms_conditions") else "Not Found"

            # Careers Page
            panel["Careers Page"] = "Verified" if website_data.get("has_careers") else "Not Found"

            # Contact Page
            # We can also check if metadata contains contact references
            has_contact = website_data.get("has_contact", False) or "contact" in str(website_data.get("page_title", "")).lower()
            panel["Contact Page"] = "Verified" if has_contact else "Not Found"

        # 2. Evaluate Email
        has_email = email_data and email_data.get("domain") != ""
        if has_email:
            is_corp = not email_data.get("is_free_email", True) and not email_data.get("is_disposable", True)
            if is_corp and email_data.get("domain_exists"):
                panel["Corporate Email"] = "Verified"
            elif email_data.get("is_disposable"):
                panel["Corporate Email"] = "Invalid"
            elif email_data.get("is_free_email"):
                panel["Corporate Email"] = "Not Found"  # Not a corporate email
            else:
                panel["Corporate Email"] = "Unknown"

        # 3. Overall Verification Status logic
        # Overall Verified requires at least Corporate Email Verified or Website Verified
        is_website_verified = panel["Website"] == "Verified"
        is_email_verified = panel["Corporate Email"] == "Verified"
        
        # Check if WHOIS indicates a highly established domain (> 5 years)
        is_established = False
        if website_data and website_data.get("whois"):
            age = website_data["whois"].get("domain_age_days")
            if age is not None and age >= 1825:
                is_established = True

        if is_email_verified and (is_website_verified or is_established):
            overall_status = "Verified"
        elif is_email_verified or is_website_verified or is_established or panel["WHOIS"] == "Verified":
            overall_status = "Partially Verified"
        else:
            overall_status = "Unable to Verify"

        return overall_status, panel
