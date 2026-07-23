import re
from typing import Dict, Any, List, Optional, Tuple
from app.services.extraction.models import CanonicalEntity, EvidenceRecord, SourceEnum, StatusEnum

class RawExtractor:
    """
    Layer 1: Raw Extractor.
    Extracts raw text entities using Label, Regex, and Section parsing.
    Preserves exact input strings, line numbers, section headers, and character offsets.
    """

    LABELS_MAP = {
        "company_name": ["Company Name", "Company", "Organization", "Employer", "Firm"],
        "job_title": ["Job Title", "Job-Title", "Job_Title", "Position", "Role", "Title"],
        "employment_type": ["Employment Type", "Job Type", "Type"],
        "salary": ["Salary", "Salary Range", "CTC", "Compensation", "Package"],
        "location": ["Location", "Work Location", "City", "State", "Country"],
        "experience": ["Experience Required", "Experience", "Work Experience", "Req Exp"],
        "education": ["Education", "Education Required", "Degree", "Qualification"],
        "recruiter_email": ["Recruiter Email", "Email", "Contact Email", "Apply Email"],
        "recruiter_phone": ["Recruiter Phone", "Phone", "Contact Number", "Mobile", "Contact"],
        "website": ["Official Website", "Website", "Company Website", "Web"],
        "careers_url": ["Careers URL", "Careers Page", "Careers"],
        "application_url": ["Application URL", "Apply Link", "Apply URL", "Apply"],
        "skills": ["Skills", "Required Skills", "Core Skills", "Technologies"],
        "benefits": ["Benefits", "Perks", "Compensation & Benefits"],
        "hiring_steps": ["Hiring Steps", "Hiring Process", "Interview Steps", "Selection Process"],
        "joining_timeline": ["Joining Timeline", "Joining", "Start Date", "Joining Date"],
        "notice_period": ["Notice Period", "Notice"],
        "work_mode": ["Work Mode", "Worksite Type", "Work Mode Type"],
        "company_description": ["About Us", "Company Description", "About Company", "About the Company"]
    }

    @classmethod
    def clean_raw_value(cls, val: str) -> str:
        if not val:
            return ""
        cleaned = val.strip()
        noise_patterns = [
            r'^(?:we\s+are\s+)?looking\s+for\s+(?:a\s+|an\s+|the\s+)?',
            r'^(?:we\s+are\s+)?seeking\s+(?:a\s+|an\s+|the\s+)?',
            r'^(?:we\s+are\s+)?hiring\s+for\s+(?:a\s+|an\s+|the\s+)?',
            r'^(?:we\s+are\s+)?hiring\s+(?:a\s+|an\s+|the\s+)?'
        ]
        for pat in noise_patterns:
            cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE).strip()
        cleaned = cleaned.strip('"\' \t\n\r:-')
        if cleaned.endswith('.'):
            abbrs = ["ltd.", "inc.", "corp.", "co.", "pvt."]
            if not any(cleaned.lower().endswith(a) for a in abbrs):
                cleaned = cleaned[:-1].strip()
        return cleaned

    @classmethod
    def find_line_number(cls, text: str, char_offset: int) -> int:
        return text[:char_offset].count('\n') + 1

    @classmethod
    def parse_sections(cls, text: str) -> Dict[str, Tuple[str, Tuple[int, int]]]:
        lines = text.split('\n')
        sections = {}
        current_header = "Intro"
        current_lines = []
        start_offset = 0

        header_pattern = re.compile(
            r'^(?:required\s+skills|skills|technologies|requirements|qualifications|experience|education|degree|benefits|perks|hiring\s+process|interview|selection|about\s+us|responsibilities|duties)\b',
            re.IGNORECASE
        )

        running_offset = 0
        for line in lines:
            line_len = len(line) + 1  # include newline
            cleaned = line.strip()
            if not cleaned:
                running_offset += line_len
                continue

            is_header = False
            if len(cleaned) < 50:
                if header_pattern.search(cleaned) or (cleaned.endswith(':') and len(cleaned) < 30):
                    is_header = True

            if is_header:
                if current_lines:
                    sections[current_header] = (
                        "\n".join(current_lines).strip(),
                        (start_offset, running_offset)
                    )
                current_header = cleaned.rstrip(':').strip()
                current_lines = []
                start_offset = running_offset
            else:
                current_lines.append(line)

            running_offset += line_len

        if current_lines:
            sections[current_header] = (
                "\n".join(current_lines).strip(),
                (start_offset, len(text))
            )

        return sections

    @classmethod
    def extract_by_label(cls, text: str, label_keywords: List[str]) -> Optional[Tuple[str, EvidenceRecord]]:
        for keyword in label_keywords:
            inline_pattern = r'(?:^|\n)\s*(?:\*\*)?' + re.escape(keyword) + r'(?:\*\*)?\s*[:-]\s*([^\n]+)'
            match = re.search(inline_pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                val = cls.clean_raw_value(match.group(1))
                if val.lower() not in ["unspecified company", "recruitment outreach", "not disclosed"]:
                    line_num = cls.find_line_number(text, match.start(1))
                    ev = EvidenceRecord(
                        matched_text=match.group(0).strip(),
                        matched_pattern=inline_pattern,
                        line_number=line_num,
                        character_offsets=[match.start(1), match.end(1)]
                    )
                    return val, ev

            next_line_pattern = r'(?:^|\n)\s*(?:\*\*)?' + re.escape(keyword) + r'(?:\*\*)?\s*[:-]\s*\n\s*([^\n]+)'
            match = re.search(next_line_pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                val = cls.clean_raw_value(match.group(1))
                if val.lower() not in ["unspecified company", "recruitment outreach", "not disclosed"]:
                    line_num = cls.find_line_number(text, match.start(1))
                    ev = EvidenceRecord(
                        matched_text=match.group(0).strip(),
                        matched_pattern=next_line_pattern,
                        line_number=line_num,
                        character_offsets=[match.start(1), match.end(1)]
                    )
                    return val, ev
        return None

    @classmethod
    def extract_all_raw(cls, text: str) -> Dict[str, CanonicalEntity]:
        raw_text = text or ""
        sections = cls.parse_sections(raw_text)
        entities: Dict[str, CanonicalEntity] = {}

        def get_section(keywords: List[str]) -> Optional[Tuple[str, str, Tuple[int, int]]]:
            for header, (content, offsets) in sections.items():
                if any(kw in header.lower() for kw in keywords):
                    return header, content, offsets
            return None

        # 1. Company Name
        res = cls.extract_by_label(raw_text, cls.LABELS_MAP["company_name"])
        if res:
            val, ev = res
            entities["company_name"] = CanonicalEntity(
                value=val, source=SourceEnum.LABEL.value, confidence=100,
                status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
            )
        else:
            company_patterns = [
                (r'About\s+(?:the\s+)?(?:Company\s+)?([A-Za-z][A-Za-z0-9\s,&.]{2,45})\b', "About Company"),
                (r'At\s+([A-Za-z][A-Za-z0-9\s,&.]{2,45})\b\s*,\s*we\s+are', "At Company, we are"),
                (r'([A-Za-z][A-Za-z0-9\s,&.]{2,45}\s+(?:Technologies|Solutions|Services|Systems|Group|Corp|Corporation|Pvt|Ltd|Inc|Pty|LLC|Pvt\.?\s*Ltd\.?))', "Corporate Entity Suffix"),
                (r'\b(?:at|for)\s+([A-Z][A-Za-z0-9\s,&.]{2,45})\b', "at/for Company")
            ]
            found = False
            for pat, pat_name in company_patterns:
                m = re.search(pat, raw_text)
                if m and m.group(1):
                    val = cls.clean_raw_value(m.group(1))
                    ev = EvidenceRecord(
                        matched_text=m.group(0), matched_pattern=pat_name,
                        line_number=cls.find_line_number(raw_text, m.start(1)),
                        character_offsets=[m.start(1), m.end(1)]
                    )
                    entities["company_name"] = CanonicalEntity(
                        value=val, source=SourceEnum.REGEX.value, confidence=100,
                        status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
                    )
                    found = True
                    break
            if not found:
                entities["company_name"] = CanonicalEntity()

        # 2. Job Title
        res = cls.extract_by_label(raw_text, cls.LABELS_MAP["job_title"])
        if res:
            val, ev = res
            entities["job_title"] = CanonicalEntity(
                value=val, source=SourceEnum.LABEL.value, confidence=100,
                status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
            )
        else:
            title_pat = r'\b([A-Za-z][a-zA-Z\s-]{2,40}\b(?:Developer|Engineer|Manager|Associate|Analyst|Consultant|Specialist|Intern|Lead|Director|Writer|Clerk|Executive|Hiring|Designer|Representative|Scientist|Practitioner|Coder|SRE|Assistant|Officer|Agent))\b'
            m = re.search(title_pat, raw_text, re.IGNORECASE)
            if m and m.group(1):
                val = cls.clean_raw_value(m.group(1))
                ev = EvidenceRecord(
                    matched_text=m.group(0), matched_pattern=title_pat,
                    line_number=cls.find_line_number(raw_text, m.start(1)),
                    character_offsets=[m.start(1), m.end(1)]
                )
                entities["job_title"] = CanonicalEntity(
                    value=val, source=SourceEnum.REGEX.value, confidence=100,
                    status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
                )
            else:
                entities["job_title"] = CanonicalEntity()

        # 3. Employment Type
        res = cls.extract_by_label(raw_text, cls.LABELS_MAP["employment_type"])
        if res:
            val, ev = res
            entities["employment_type"] = CanonicalEntity(
                value=val, source=SourceEnum.LABEL.value, confidence=100,
                status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
            )
        else:
            type_pat = r'\b(Full\s*-?\s*time|Part\s*-?\s*time|Contract|Internship|Temporary|Freelance)\b'
            m = re.search(type_pat, raw_text, re.IGNORECASE)
            if m:
                val = cls.clean_raw_value(m.group(1))
                ev = EvidenceRecord(
                    matched_text=m.group(0), matched_pattern=type_pat,
                    line_number=cls.find_line_number(raw_text, m.start(1)),
                    character_offsets=[m.start(1), m.end(1)]
                )
                entities["employment_type"] = CanonicalEntity(
                    value=val, source=SourceEnum.REGEX.value, confidence=100,
                    status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
                )
            else:
                entities["employment_type"] = CanonicalEntity()

        # 4. Salary
        res = cls.extract_by_label(raw_text, cls.LABELS_MAP["salary"])
        if res:
            val, ev = res
            entities["salary"] = CanonicalEntity(
                value=val, source=SourceEnum.LABEL.value, confidence=100,
                status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
            )
        else:
            sal_pats = [
                r'((?:[₹$£€]|INR|USD|EUR|GBP)\s*\d+(?:,\d+)*(?:\s*(?:-|to|–)\s*(?:[₹$£€]|INR|USD|EUR|GBP)?\s*\d+(?:,\d+)*)?(?:\s*(?:pm|pm\.|p\.m\.|pa|pa\.|p\.a\.|yr|year|month|hr|hour|annum|CTC|LPA))?)',
                r'(\d+(?:\.\d+)?\s*(?:-|to|–)?\s*\d*(?:\.\d+)?\s*(?:LPA|CTC|Lakhs?))'
            ]
            found = False
            for pat in sal_pats:
                m = re.search(pat, raw_text, re.IGNORECASE)
                if m and m.group(1):
                    val = cls.clean_raw_value(m.group(1))
                    ev = EvidenceRecord(
                        matched_text=m.group(0), matched_pattern=pat,
                        line_number=cls.find_line_number(raw_text, m.start(1)),
                        character_offsets=[m.start(1), m.end(1)]
                    )
                    entities["salary"] = CanonicalEntity(
                        value=val, source=SourceEnum.REGEX.value, confidence=100,
                        status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
                    )
                    found = True
                    break
            if not found:
                entities["salary"] = CanonicalEntity()

        # 5. Location & Work Mode
        res = cls.extract_by_label(raw_text, cls.LABELS_MAP["location"])
        if res:
            val, ev = res
            entities["location"] = CanonicalEntity(
                value=val, source=SourceEnum.LABEL.value, confidence=100,
                status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
            )
        else:
            loc_pat = r'\b(Remote|Hybrid|On-site|Onsite|Remote\s*\([A-Za-z\s]+\))\b'
            m = re.search(loc_pat, raw_text, re.IGNORECASE)
            if m:
                val = cls.clean_raw_value(m.group(1))
                ev = EvidenceRecord(
                    matched_text=m.group(0), matched_pattern=loc_pat,
                    line_number=cls.find_line_number(raw_text, m.start(1)),
                    character_offsets=[m.start(1), m.end(1)]
                )
                entities["location"] = CanonicalEntity(
                    value=val, source=SourceEnum.REGEX.value, confidence=100,
                    status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
                )
            else:
                entities["location"] = CanonicalEntity()

        # 6. Recruiter Email
        res = cls.extract_by_label(raw_text, cls.LABELS_MAP["recruiter_email"])
        if res:
            val, ev = res
            entities["recruiter_email"] = CanonicalEntity(
                value=val, source=SourceEnum.LABEL.value, confidence=100,
                status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
            )
        else:
            email_pat = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
            m = re.search(email_pat, raw_text)
            if m:
                val = cls.clean_raw_value(m.group(1))
                ev = EvidenceRecord(
                    matched_text=m.group(0), matched_pattern=email_pat,
                    line_number=cls.find_line_number(raw_text, m.start(1)),
                    character_offsets=[m.start(1), m.end(1)]
                )
                entities["recruiter_email"] = CanonicalEntity(
                    value=val, source=SourceEnum.REGEX.value, confidence=100,
                    status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
                )
            else:
                entities["recruiter_email"] = CanonicalEntity()

        # 7. Recruiter Phone
        res = cls.extract_by_label(raw_text, cls.LABELS_MAP["recruiter_phone"])
        if res:
            val, ev = res
            entities["recruiter_phone"] = CanonicalEntity(
                value=val, source=SourceEnum.LABEL.value, confidence=100,
                status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
            )
        else:
            phone_pats = [r'\b[6789]\d{9}\b', r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b']
            found = False
            for pat in phone_pats:
                m = re.search(pat, raw_text)
                if m:
                    val = cls.clean_raw_value(m.group(0))
                    ev = EvidenceRecord(
                        matched_text=m.group(0), matched_pattern=pat,
                        line_number=cls.find_line_number(raw_text, m.start(0)),
                        character_offsets=[m.start(0), m.end(0)]
                    )
                    entities["recruiter_phone"] = CanonicalEntity(
                        value=val, source=SourceEnum.REGEX.value, confidence=100,
                        status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
                    )
                    found = True
                    break
            if not found:
                entities["recruiter_phone"] = CanonicalEntity()

        # 8. Website
        res = cls.extract_by_label(raw_text, cls.LABELS_MAP["website"])
        if res:
            val, ev = res
            entities["website"] = CanonicalEntity(
                value=val, source=SourceEnum.LABEL.value, confidence=100,
                status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
            )
        else:
            web_pat = r'\b(?<!@)(?:https?://)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[a-zA-Z0-9_.-]+)*\b'
            m = re.search(web_pat, raw_text)
            if m:
                val = cls.clean_raw_value(m.group(0))
                ev = EvidenceRecord(
                    matched_text=m.group(0), matched_pattern=web_pat,
                    line_number=cls.find_line_number(raw_text, m.start(0)),
                    character_offsets=[m.start(0), m.end(0)]
                )
                entities["website"] = CanonicalEntity(
                    value=val, source=SourceEnum.REGEX.value, confidence=100,
                    status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()]
                )
            else:
                entities["website"] = CanonicalEntity()

        # 9. WhatsApp & Telegram
        wa_pat = r'\b(?:wa\.me\/|chat\.whatsapp\.com\/|whatsapp\b)'
        m_wa = re.search(wa_pat, raw_text, re.IGNORECASE)
        if m_wa:
            ev = EvidenceRecord(matched_text=m_wa.group(0), matched_pattern=wa_pat, line_number=cls.find_line_number(raw_text, m_wa.start(0)))
            entities["whatsapp"] = CanonicalEntity(value=m_wa.group(0), source=SourceEnum.REGEX.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
        else:
            entities["whatsapp"] = CanonicalEntity()

        tg_pat = r'\b(?:t\.me\/|telegram\.me\/|telegram\b)'
        m_tg = re.search(tg_pat, raw_text, re.IGNORECASE)
        if m_tg:
            ev = EvidenceRecord(matched_text=m_tg.group(0), matched_pattern=tg_pat, line_number=cls.find_line_number(raw_text, m_tg.start(0)))
            entities["telegram"] = CanonicalEntity(value=m_tg.group(0), source=SourceEnum.REGEX.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
        else:
            entities["telegram"] = CanonicalEntity()

        # 10. Payment Requests
        pay_pat = r'\b(?:registration\s*fee|training\s*fee|security\s*deposit|equipment\s*purchase|caution\s*deposit)\b'
        m_pay = re.search(pay_pat, raw_text, re.IGNORECASE)
        if m_pay:
            ev = EvidenceRecord(matched_text=m_pay.group(0), matched_pattern=pay_pat, line_number=cls.find_line_number(raw_text, m_pay.start(0)))
            entities["payment_requests"] = CanonicalEntity(value=m_pay.group(0), source=SourceEnum.REGEX.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
        else:
            entities["payment_requests"] = CanonicalEntity()

        # 11. Experience & Education (Section Fallback)
        res_exp = cls.extract_by_label(raw_text, cls.LABELS_MAP["experience"])
        if res_exp:
            val, ev = res_exp
            entities["experience"] = CanonicalEntity(value=val, source=SourceEnum.LABEL.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
        else:
            exp_pat = r'(\d+\s*(?:to|-)\s*\d+\s*(?:\+\s*)?years?(?:\s*of)?\s*experience|\d+\s*(?:\+\s*)?years?(?:\s*of)?\s*experience)'
            m = re.search(exp_pat, raw_text, re.IGNORECASE)
            if m and m.group(1):
                val = cls.clean_raw_value(m.group(1))
                ev = EvidenceRecord(matched_text=m.group(0), matched_pattern=exp_pat, line_number=cls.find_line_number(raw_text, m.start(1)), character_offsets=[m.start(1), m.end(1)])
                entities["experience"] = CanonicalEntity(value=val, source=SourceEnum.REGEX.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
            else:
                sec = get_section(["experience"])
                if sec:
                    hdr, content, offsets = sec
                    ev = EvidenceRecord(matched_text=content[:100], section_name=hdr, character_offsets=list(offsets))
                    entities["experience"] = CanonicalEntity(value=cls.clean_raw_value(content), source=SourceEnum.SECTION.value, confidence=95, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
                else:
                    entities["experience"] = CanonicalEntity()

        res_edu = cls.extract_by_label(raw_text, cls.LABELS_MAP["education"])
        if res_edu:
            val, ev = res_edu
            entities["education"] = CanonicalEntity(value=val, source=SourceEnum.LABEL.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
        else:
            edu_pat = r'(\b(?:Bachelor|Master|Degree|Ph\.D|B\.S|B\.Tech|B\.E|BCA|MCA|MBA|Graduate|Post\s*Graduate)\b[^\n]*)'
            m = re.search(edu_pat, raw_text, re.IGNORECASE)
            if m and m.group(1):
                val = cls.clean_raw_value(m.group(1))
                ev = EvidenceRecord(matched_text=m.group(0), matched_pattern=edu_pat, line_number=cls.find_line_number(raw_text, m.start(1)), character_offsets=[m.start(1), m.end(1)])
                entities["education"] = CanonicalEntity(value=val, source=SourceEnum.REGEX.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
            else:
                sec = get_section(["education", "degree"])
                if sec:
                    hdr, content, offsets = sec
                    ev = EvidenceRecord(matched_text=content[:100], section_name=hdr, character_offsets=list(offsets))
                    entities["education"] = CanonicalEntity(value=cls.clean_raw_value(content), source=SourceEnum.SECTION.value, confidence=95, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
                else:
                    entities["education"] = CanonicalEntity()

        # 12. Responsibilities & Requirements & Skills & Benefits
        for ent_key, sec_kw in [("responsibilities", ["responsibilit", "duties"]), ("requirements", ["requirement", "qualificat"]), ("skills", ["skill", "technolog"]), ("benefits", ["benefit", "perk"])]:
            res_ent = cls.extract_by_label(raw_text, cls.LABELS_MAP.get(ent_key, [ent_key]))
            if res_ent:
                val, ev = res_ent
                entities[ent_key] = CanonicalEntity(value=val, source=SourceEnum.LABEL.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
            else:
                sec = get_section(sec_kw)
                if sec:
                    hdr, content, offsets = sec
                    ev = EvidenceRecord(matched_text=content[:100], section_name=hdr, character_offsets=list(offsets))
                    entities[ent_key] = CanonicalEntity(value=cls.clean_raw_value(content), source=SourceEnum.SECTION.value, confidence=95, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
                else:
                    entities[ent_key] = CanonicalEntity()

        # 13. Hiring Steps (List)
        res_hs = cls.extract_by_label(raw_text, cls.LABELS_MAP["hiring_steps"])
        steps_list = []
        if res_hs:
            val, ev = res_hs
            steps_list = [s.strip() for s in val.split(',') if s.strip()]
            entities["hiring_steps"] = CanonicalEntity(value=steps_list, source=SourceEnum.LABEL.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
        else:
            lines = raw_text.split('\n')
            step_kw = ["application", "assessment", "test", "screening", "interview", "hr", "technical", "selection", "offer", "rounds"]
            for idx, line in enumerate(lines, 1):
                cl = line.strip().strip('*•-0123456789. ')
                if len(cl) < 45 and any(kw in cl.lower() for kw in step_kw):
                    steps_list.append(cl)
            seen = set()
            steps_list = [s for s in steps_list if not (s.lower() in seen or seen.add(s.lower()))]
            if steps_list:
                ev = EvidenceRecord(matched_text=", ".join(steps_list))
                entities["hiring_steps"] = CanonicalEntity(value=steps_list, source=SourceEnum.REGEX.value, confidence=95, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
            else:
                entities["hiring_steps"] = CanonicalEntity()

        # 14. Joining Timeline & Notice Period
        res_jt = cls.extract_by_label(raw_text, cls.LABELS_MAP["joining_timeline"])
        if res_jt:
            val, ev = res_jt
            entities["joining_timeline"] = CanonicalEntity(value=val, source=SourceEnum.LABEL.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
        else:
            m = re.search(r'\b(start\s*immediately|join\s*immediately|immediate\s*joining|immediate\s*selection|immediate\s*start)\b', raw_text, re.IGNORECASE)
            if m:
                val = cls.clean_raw_value(m.group(1))
                ev = EvidenceRecord(matched_text=m.group(0), matched_pattern=m.re.pattern, line_number=cls.find_line_number(raw_text, m.start(1)), character_offsets=[m.start(1), m.end(1)])
                entities["joining_timeline"] = CanonicalEntity(value=val, source=SourceEnum.REGEX.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
            else:
                entities["joining_timeline"] = CanonicalEntity()

        res_np = cls.extract_by_label(raw_text, cls.LABELS_MAP["notice_period"])
        if res_np:
            val, ev = res_np
            entities["notice_period"] = CanonicalEntity(value=val, source=SourceEnum.LABEL.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
        else:
            m = re.search(r'\b(\d+\s*days?\s*notice|immediate\s*joining|\d+\s*months?\s*notice)\b', raw_text, re.IGNORECASE)
            if m:
                val = cls.clean_raw_value(m.group(1))
                ev = EvidenceRecord(matched_text=m.group(0), matched_pattern=m.re.pattern, line_number=cls.find_line_number(raw_text, m.start(1)), character_offsets=[m.start(1), m.end(1)])
                entities["notice_period"] = CanonicalEntity(value=val, source=SourceEnum.REGEX.value, confidence=100, status=StatusEnum.EXTRACTED.value, evidence=[ev.to_dict()])
            else:
                entities["notice_period"] = CanonicalEntity()

        # Fill default placeholders for remaining inventory entities if missing
        inventory_defaults = [
            "currency", "salary_period", "country", "city", "state", "work_mode",
            "careers_url", "application_url", "linkedin", "certifications", "company_description"
        ]
        for item_key in inventory_defaults:
            if item_key not in entities:
                entities[item_key] = CanonicalEntity()

        return entities
