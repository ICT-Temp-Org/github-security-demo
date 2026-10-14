"""
GHAS Demo Blog Application
==========================

⚠️  INTENTIONALLY VULNERABLE – FOR DEMONSTRATION PURPOSES ONLY  ⚠️

This application contains deliberate security flaws designed to produce
GitHub Advanced Security (GHAS) alerts.  It exists solely to demonstrate
CodeQL code scanning, Dependabot, and secret scanning in a safe, offline
context.

DO NOT:
  • Deploy this application to any public-facing server.
  • Run it on anything other than 127.0.0.1 (localhost).
  • Commit real credentials, API keys, or secrets to this repository.
  • Use any of the insecure patterns shown here in production code.

Each intentional vulnerability is clearly labelled with its CWE reference
and the expected CodeQL query name.
"""

import base64
import os
import pickle  # noqa: S403 – intentional demo
import sqlite3

from flask import Flask, abort, g, render_template, render_template_string, request

# ============================================================
# ⚠️  DEMO VULNERABILITY 1: Hard-coded Flask secret key
#     CWE-259 · CodeQL: py/flask-hardcoded-secret
#
#     The secret key is embedded in source code.  A real
#     application must load it from a secure environment
#     variable or secrets manager.
# ============================================================
_DEMO_SECRET_KEY = "super-secret-hardcoded-key-do-not-use"  # noqa: S105

app = Flask(__name__)
app.secret_key = _DEMO_SECRET_KEY  # ← hard-coded secret – intentional demo

# ============================================================
# ⚠️  DEMO VULNERABILITY 2: Flask debug mode enabled
#     CWE-94 · Werkzeug interactive debugger exposed
#
#     When DEBUG=True the Werkzeug debugger is reachable via
#     the browser and allows arbitrary Python execution.
#     Never enable in production.
# ============================================================
app.config["DEBUG"] = True  # ← intentional demo

# ============================================================
# ⚠️  DEMO SECRET FIXTURE (fake / inert)
#     For secret-scanning demonstration.
#
#     These secrets are all fake
# ============================================================
DEMO_API_KEY = "GHAS_DEMO_ABCDEFGHIJKLMNOP12345678"

PRIVATE_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAixezDL2Tt5NV6/ZpqvSpq+XuDbzaLJV4ypeAkHl5iAAAAAJitDkTxrQ5E
8QAAAAtzc2gtZWQyNTUxOQAAACAixezDL2Tt5NV6/ZpqvSpq+XuDbzaLJV4ypeAkHl5iAA
AAAECRg9UsKm5KsAJT0HonEgOTI11q4HyVf3UlBiDAOhMLtyLF7MMvZO3k1Xr9mmq9Kmr5
e4NvNoslXjKl4CQeXmIAAAAAEWtleS0xNzg1MzI5NjQ0MDQ4AQIDBA==
-----END OPENSSH PRIVATE KEY-----"""

GH_PAT = "ghp__HOiqh6NmRLNH4VKgmsEEMO4sK3JnqIH2"

AWS_KEY = "AKIA_WNEp49LldUDlQRUVgKZXlgzxs2ZciHie"

NI_NUMBER = "QQ 12 34 56 A"

GH_FG_PAT = "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"

# ── Database helpers ──────────────────────────────────────────────────────────

DB_PATH = os.environ.get("BLOG_DB", "blog.db")

SEED_POSTS = [
    {
        "title": "Welcome to the GHAS Demo Blog",
        "body": (
            "This is a demonstration application for GitHub Advanced Security (GHAS).  "
            "It is deliberately insecure and exists purely to showcase code-scanning, "
            "Dependabot, and secret-scanning alerts."
        ),
        "author": "Demo Author",
    },
    {
        "title": "Understanding CodeQL Code Scanning",
        "body": (
            "CodeQL analyses your source code as data, building a database of facts "
            "about the program and then running queries against it to surface security "
            "vulnerabilities and bugs.  The security-extended query suite covers OWASP "
            "Top 10 and many more CWEs."
        ),
        "author": "Security Team",
    },
    {
        "title": "Keeping Dependencies Up to Date with Dependabot",
        "body": (
            "Dependabot automatically opens pull requests to update outdated or "
            "vulnerable dependencies.  It relies on the GitHub Advisory Database to "
            "identify packages with known security advisories."
        ),
        "author": "Security Team",
    },
    {
        "title": "Preventing Secret Leakage with Secret Scanning",
        "body": (
            "GitHub secret scanning detects tokens, API keys, and other credentials "
            "committed to a repository.  Push protection can block commits containing "
            "secrets before they reach the remote, reducing exposure time to near zero."
        ),
        "author": "Security Team",
    },
]


def get_db():
    """Return the per-request SQLite connection, creating it if necessary."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):  # noqa: ARG001
    """Close the database connection at the end of each request."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    """Create the posts table and insert seed data."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS posts "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, body TEXT, author TEXT)"
    )
    conn.execute("DELETE FROM posts")
    for post in SEED_POSTS:
        conn.execute(
            "INSERT INTO posts (title, body, author) VALUES (?, ?, ?)",
            (post["title"], post["body"], post["author"]),
        )
    conn.commit()
    conn.close()


# ── Benign routes ─────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """List all blog posts."""
    db = get_db()
    posts = db.execute("SELECT id, title, author FROM posts").fetchall()
    return render_template("index.html", posts=posts)


@app.route("/post/<int:post_id>")
def post_detail(post_id):
    """Display a single blog post."""
    db = get_db()
    post = db.execute(
        "SELECT id, title, body, author FROM posts WHERE id = ?", (post_id,)
    ).fetchone()
    if post is None:
        abort(404)
    return render_template("post.html", post=post)


# ── Intentionally Vulnerable Demo Routes ─────────────────────────────────────
#
# ⚠️  THE ROUTES BELOW ARE DELIBERATELY INSECURE.
#     They exist to generate CodeQL alerts for demonstration.
#     Do not replicate these patterns in real applications.


@app.route("/demo/sqli")
def demo_sqli():
    """
    ⚠️  DEMO: SQL Injection (CWE-89)
    CodeQL query: py/sql-injection

    The query parameter ``q`` is concatenated directly into an SQL statement
    without sanitisation or parameterisation.  An attacker can manipulate the
    query to access or corrupt arbitrary data.

    Example exploit: /demo/sqli?q=' OR '1'='1
    """
    q = request.args.get("q", "")
    db = get_db()

    # ⚠️  INTENTIONAL SQL INJECTION – never concatenate user input into SQL
    unsafe_query = (
        "SELECT id, title, author FROM posts WHERE title LIKE '%" + q + "%'"
    )
    posts = db.execute(unsafe_query).fetchall()  # noqa: S608
    return render_template("index.html", posts=posts, demo_warning="SQL Injection demo active – query: " + unsafe_query)


@app.route("/demo/xss")
def demo_xss():
    """
    ⚠️  DEMO: Reflected Cross-Site Scripting (CWE-79)
    CodeQL query: py/reflected-xss

    The ``name`` parameter is rendered directly into an HTML response via
    ``render_template_string`` without escaping.  An attacker can inject
    arbitrary JavaScript that executes in the victim's browser.

    Example exploit: /demo/xss?name=<script>alert(document.cookie)</script>
    """
    name = request.args.get("name", "World")

    # ⚠️  INTENTIONAL XSS – user input rendered without sanitisation
    unsafe_html = (
        "<h2>&#9888;&#65039; XSS Demo</h2>"
        "<p>Hello, " + name + "!  This value was rendered without HTML escaping.</p>"
        "<p><a href='/'>&#8592; Back to blog</a></p>"
    )
    return render_template_string(unsafe_html)  # noqa: S703, S704


@app.route("/demo/path")
def demo_path():
    """
    ⚠️  DEMO: Path Traversal / Local File Disclosure (CWE-22)
    CodeQL query: py/path-injection

    The ``file`` parameter controls which file is opened and returned.
    An attacker can use ``../`` sequences to read arbitrary files on the
    server, including ``/etc/passwd`` or application secrets.

    Example exploit: /demo/path?file=../../etc/passwd
    """
    filename = request.args.get("file", "README.md")

    # ⚠️  INTENTIONAL PATH TRAVERSAL – user controls the file path
    try:
        with open(filename, encoding="utf-8", errors="replace") as f:  # noqa: PTH123, WPS226
            content = f.read()
    except OSError as exc:
        content = f"Error reading file: {exc}"

    return render_template_string(
        "<h2>&#9888;&#65039; Path Traversal Demo</h2>"
        "<pre>{{ content | e }}</pre>"
        "<p><a href='/'>&#8592; Back to blog</a></p>",
        content=content,
    )


@app.route("/demo/pickle", methods=["POST"])
def demo_pickle():
    """
    ⚠️  DEMO: Unsafe Deserialisation via pickle (CWE-502)
    CodeQL query: py/unsafe-deserialization

    The raw request body is decoded from Base64 and passed directly to
    ``pickle.loads``.  Sending a crafted payload enables arbitrary code
    execution on the server.

    Never deserialise untrusted data using pickle.
    """
    data = request.get_data()
    if not data:
        return (
            "<h2>&#9888;&#65039; Pickle Deserialisation Demo</h2>"
            "<p>POST a Base64-encoded pickle payload to this endpoint.</p>"
            "<p>Example (Python):<br>"
            "<code>import pickle, base64, requests<br>"
            "payload = base64.b64encode(pickle.dumps({'demo': True}))<br>"
            "requests.post('http://127.0.0.1:5000/demo/pickle', data=payload)</code></p>"
            "<p><a href='/'>&#8592; Back to blog</a></p>"
        )

    # ⚠️  INTENTIONAL UNSAFE DESERIALISATION
    try:
        decoded = base64.b64decode(data)
        obj = pickle.loads(decoded)  # noqa: S301 – intentional demo
        result = repr(obj)
    except Exception as exc:  # noqa: BLE001
        result = f"Error: {exc}"

    return render_template_string(
        "<h2>&#9888;&#65039; Pickle Deserialisation Demo</h2>"
        "<pre>{{ result | e }}</pre>"
        "<p><a href='/'>&#8592; Back to blog</a></p>",
        result=result,
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    # ⚠️  DEMO: Running with debug=True exposes the Werkzeug interactive
    #     debugger.  A production application must use a production WSGI
    #     server (e.g. gunicorn) bound explicitly to 127.0.0.1.
    app.run(host="127.0.0.1", port=5000, debug=True)  # noqa: S201
