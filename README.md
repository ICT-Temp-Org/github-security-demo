# ⚠️ GitHub Advanced Security Demo Repository

> **WARNING – INTENTIONALLY VULNERABLE APPLICATION**
>
> This repository contains **deliberate security flaws** designed to produce GitHub Advanced Security (GHAS) alerts.
> It exists solely to demonstrate CodeQL code scanning, Dependabot, and secret scanning in a safe, offline setting.
>
> - **Do NOT deploy** this application to any public-facing server or cloud environment.
> - **Run only on `127.0.0.1`** (localhost). Never bind to `0.0.0.0` or an external interface.
> - **Do NOT commit real credentials**, API keys, or secrets to this repository.
> - **Do NOT install the vulnerable `requirements.txt`** on a production machine.
> - If any network access is ever introduced, use HTTPS exclusively.

---

## Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Running Locally](#running-locally)
- [Intentional Vulnerabilities (CodeQL)](#intentional-vulnerabilities-codeql)
- [Dependabot Alerts](#dependabot-alerts)
- [Secret Scanning – Custom Pattern Setup](#secret-scanning--custom-pattern-setup)
- [Enabling GHAS Features](#enabling-ghas-features)
- [Running the Tests](#running-the-tests)
- [Licence](#licence)

---

## Overview

This is a minimal Python/Flask read-only blog application.  Its sole purpose is to serve as a GHAS demonstration vehicle.  It deliberately includes:

| GHAS Feature | What is demonstrated |
|---|---|
| **Code scanning (CodeQL)** | SQL injection, reflected XSS, path traversal, unsafe pickle deserialisation, hard-coded secret key, debug mode enabled |
| **Dependabot** | Pinned old Python dependencies with known security advisories |
| **Secret scanning** | A synthetic inert token in the `GHAS_DEMO_[A-Z0-9]{24}` format, detectable via a custom pattern |

---

## Repository Structure

```
github-security-demo/
├── .github/
│   ├── dependabot.yml          # Dependabot config for pip & Actions
│   └── workflows/
│       ├── codeql.yml          # CodeQL advanced-setup workflow
│       └── test.yml            # Benign CI test workflow
├── templates/
│   ├── base.html
│   ├── index.html              # Blog listing
│   └── post.html               # Post detail
├── tests/
│   └── test_app.py             # pytest tests (benign routes only)
├── app.py                      # Flask application (intentionally vulnerable)
├── requirements.txt            # ⚠️ Deliberately outdated deps (Dependabot demo)
├── requirements-test.txt       # Current safe deps for CI tests
├── .gitignore
├── LICENSE
└── README.md
```

---

## Running Locally

> ⚠️ Only run this application on your local machine.  Never expose it to the internet.

```bash
# 1. Clone the repository
git clone https://github.com/ICT-Temp-Org/github-security-demo.git
cd github-security-demo

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install the safe test dependencies (recommended)
#    OR install the deliberately vulnerable set if you are demonstrating
#    Dependabot only (not recommended outside of that use case):
pip install -r requirements-test.txt   # safe – recommended
# pip install -r requirements.txt      # ⚠️ vulnerable – Dependabot demo only

# 4. Start the application (binds to 127.0.0.1:5000 only)
python app.py
```

Open <http://127.0.0.1:5000> in your browser.

---

## Intentional Vulnerabilities (CodeQL)

All vulnerable routes are prefixed with `/demo/` and are clearly documented in `app.py`.

| Route | Vulnerability | CWE | Expected CodeQL query |
|---|---|---|---|
| `app.py` module level | Hard-coded Flask secret key | CWE-259 | `py/flask-hardcoded-secret` |
| `app.py` module level | Flask debug mode enabled | CWE-94 | — |
| `GET /demo/sqli?q=…` | SQL injection | CWE-89 | `py/sql-injection` |
| `GET /demo/xss?name=…` | Reflected cross-site scripting | CWE-79 | `py/reflected-xss` |
| `GET /demo/path?file=…` | Path traversal / local file disclosure | CWE-22 | `py/path-injection` |
| `POST /demo/pickle` | Unsafe pickle deserialisation | CWE-502 | `py/unsafe-deserialization` |

### Demonstration

1. Ensure the **Code scanning** workflow (`codeql.yml`) has run (see [Enabling GHAS Features](#enabling-ghas-features)).
2. Go to **Security → Code scanning alerts** in the repository.
3. Each vulnerability above should appear as a separate alert with file, line, and remediation guidance.

> **Note:** CodeQL alert titles and counts may vary slightly between CodeQL versions and query suite updates.  If an expected alert is missing, check the workflow run logs.

---

## Dependabot Alerts

`requirements.txt` pins deliberately old dependency versions with known security advisories:

| Package | Pinned version | Example advisory |
|---|---|---|
| Flask | 0.12.4 | End-of-life; multiple advisories |
| Werkzeug | 0.14.1 | CVE-2019-14806 (debugger PIN bypass) |
| Jinja2 | 2.10 | CVE-2020-28493 (ReDoS) |
| requests | 2.18.0 | CVE-2018-18074 (credential forwarding) |
| cryptography | 2.1.4 | Multiple CVEs |
| Pillow | 5.0.0 | Multiple CVEs (buffer overflows) |

> **Note:** The exact number of open Dependabot alerts will vary over time as advisories are added or retired from the GitHub Advisory Database.

Once Dependabot is enabled (see below), go to **Security → Dependabot alerts** to see the outstanding advisories.  Dependabot will also open pull requests proposing safe upgrades.

---

## Secret Scanning – Custom Pattern Setup

The repository contains the following synthetic, entirely non-functional token:

```
GHAS_DEMO_ABCDEFGHIJKLMNOP12345678
```

This token is **fake and unusable** — it does not correspond to any real service or credential.  It is formatted as `GHAS_DEMO_` followed by exactly 24 uppercase alphanumeric characters so that you can demonstrate GitHub secret scanning with a **custom pattern**, without ever committing a live credential.

### Creating the custom secret-scanning pattern

1. Go to **Settings → Security → Secret scanning → Custom patterns** in this repository (or at organisation level for a broader demo).
2. Click **New pattern**.
3. Fill in the form:
   - **Pattern name:** `GHAS Demo Token`
   - **Secret format (regex):** `GHAS_DEMO_[A-Z0-9]{24}`
   - **Before secret (optional):** leave blank
   - **After secret (optional):** leave blank
4. Click **Save and dry run** to preview matches, then **Publish pattern**.
5. GitHub will scan the repository history and raise an alert for the token in `app.py`.

### Viewing the alert

Go to **Security → Secret scanning alerts**.  You should see one alert for the custom `GHAS Demo Token` pattern pointing to `app.py`.

> **Important:** Never replace the synthetic fixture with a real token.

---

## Enabling GHAS Features

All three GHAS pillars can be enabled from **Settings → Code security**:

| Feature | How to enable |
|---|---|
| **Code scanning** | Enable "Code scanning" → the `codeql.yml` workflow will run automatically |
| **Dependabot alerts** | Enable "Dependabot alerts" |
| **Dependabot security updates** | Enable "Dependabot security updates" to auto-open PRs |
| **Secret scanning** | Enable "Secret scanning" (and optionally "Push protection") |

---

## Running the Tests

The test suite covers the benign blog routes only.  It uses `requirements-test.txt` (current, safe dependencies).

```bash
pip install -r requirements-test.txt
pytest tests/ -v
```

Expected output:

```
tests/test_app.py::test_index_returns_200 PASSED
tests/test_app.py::test_index_lists_posts PASSED
tests/test_app.py::test_index_html_content_type PASSED
tests/test_app.py::test_post_detail_returns_200 PASSED
tests/test_app.py::test_post_detail_shows_title_and_body PASSED
tests/test_app.py::test_post_detail_shows_author PASSED
tests/test_app.py::test_post_detail_second_post PASSED
tests/test_app.py::test_missing_post_returns_404 PASSED
tests/test_app.py::test_missing_post_large_id PASSED
```

The CI workflow (`.github/workflows/test.yml`) runs these tests automatically on every push and pull request.

---

## Licence

MIT — see [LICENSE](LICENSE).
