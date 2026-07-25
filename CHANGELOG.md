# Changelog

All notable changes to the RecruitSafe project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.0.0] - 2026-07-25

### Added
* Dynamic dashboard explanation modal detailing the Trust Score calculation factors.
* Comprehensive, multi-tiered test framework evaluating spaCy pipeline syntax and Decision Fusion boundary regressions.
* Root repository documentation suite including setup, architecture, and security guides.

### Changed
* Refactored frontend dashboards to translate Trust percentages into clear risk assessments.
* Renamed UI cards: **Confidence Score** is now **Analysis Confidence**, **Input Quality** is now **Information Available**.
* Separated generic application links from official company outreach domains.
* Shifted evidence table indicators: renamed Red Flags to **Risk Indicators**.
* Replaced the text `"Missing"` in verifications with the status `"Not Found"`.
* Updated backend PDF report generator to match the new UI wording, labels, and design elements.

---

## [3.0.0] - 2026-07-15

### Added
* Completed context-aware intent classification mapping text scopes to semantic categories (e.g. `MANDATORY_PAYMENT`, `OPTIONAL_TRAINING`).
* Single-loaded spaCy NLP service wrapper avoiding pipeline instantiation bottlenecks.
* Dynamic scoring config files (`severity_config.json`, `score_config.json`).

### Changed
* Upgraded rule evaluations to utilize token dependencies, entities, and noun chunks instead of static regex matches.

---

## [2.0.0] - 2026-07-05

### Added
* Live network lookup checks for DNS reachability, SSL certificate validity, and WHOIS domain registrations.
* Automatic PDF audit report generation using ReportLab layout designs.

### Changed
* Extended Beanie ODM database schemas to store active footprint verifications.

---

## [1.0.0] - 2026-06-15

### Added
* Core regular expression keyword pattern match engine.
* FastAPI REST controllers and MongoDB database integration templates.
* Initial React Vite single-page dashboard.
