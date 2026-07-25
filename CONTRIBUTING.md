# Contributing to RecruitSafe

First off, thank you for considering contributing to RecruitSafe! It is people like you who make RecruitSafe such a powerful, reliable open-source tool.

---

## 📖 Table of Contents

1. [Code of Conduct](#-code-of-conduct)
2. [How Can I Contribute?](#-how-can-i-contribute)
3. [Pull Request Process](#-pull-request-process)
4. [Coding Standards](#-coding-standards)
5. [Reporting Security Vulnerabilities](#-reporting-security-vulnerabilities)

---

## 🤝 Code of Conduct

This project and everyone participating in it is governed by the RecruitSafe Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## 🛠️ How Can I Contribute?

### Reporting Bugs
* Check the existing issues database to make sure the bug hasn't been reported.
* Open a new issue detailing:
  - Expected behavior vs. actual behavior.
  - Clear steps to reproduce the issue.
  - Environment details (Node/Python version, OS).

### Suggesting Enhancements
* Open an issue explaining the proposed feature and why it would be beneficial to the platform.
* Outline the implementation approach if you plan to write the code yourself.

---

## 🔄 Pull Request Process

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Write clean, documented code and include automated tests.
3. Verify that all existing unit tests and validation frameworks pass:
   ```bash
   # Inside backend/
   python -m pytest
   python -m tests.run_validation_framework
   ```
4. Update associated documentation files under the `docs/` folder.
5. Commit your changes using descriptive commit messages:
   ```bash
   git commit -m "feat: add support for check XYZ"
   ```
6. Push to your fork and submit a Pull Request.

---

## 📏 Coding Standards

* **Python**: Adhere to PEP 8 standards. Document all public classes and functions.
* **Javascript (React)**: Use functional components, clean hooks, and modular UI cards.
* **Testing**: Write unit tests for any new regex patterns, verification modules, or logic flows.

---

## 🔒 Reporting Security Vulnerabilities

> [!IMPORTANT]
> If you identify a security vulnerability (such as a database leakage or token signing issue), please do not open a public issue. Report it confidentially to the maintainers' security email.
