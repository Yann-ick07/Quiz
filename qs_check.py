#!/usr/bin/env python3
"""
qs_check.py - Führt alle Qualitätssicherungsmaßnahmen aus.

Verwendung:
    python qs_check.py          # alle QS-Checks
    python qs_check.py --fix    # black automatisch anwenden

QS-Maßnahmen:
    1. flake8  – Linting (PEP8, Syntaxfehler, ungenutzte Imports)
    2. black   – Code-Formatierung (einheitlicher Stil)
    3. bandit  – Sicherheits-Scan (bekannte Schwachstellen)
    4. coverage – Testabdeckung (muss >= 70% sein)
"""

import subprocess
import sys

PYTHON = sys.executable
FIX_MODE = "--fix" in sys.argv

results = {}


def run(label: str, cmd: list) -> bool:
    """Führt einen Befehl aus und gibt True zurück wenn erfolgreich."""
    print(f"\n{'─'*55}")
    print(f"  {label}")
    print(f"{'─'*55}")
    result = subprocess.run(cmd)
    ok = result.returncode == 0
    results[label] = "✅ PASSED" if ok else "❌ FAILED"
    return ok


# ── 1. Linting ────────────────────────────────────────────────────────────────
run("QS 1: Linting (flake8)", [PYTHON, "-m", "flake8", "."])

# ── 2. Formatierung ───────────────────────────────────────────────────────────
if FIX_MODE:
    run("QS 2: Formatierung – Anwenden (black)", [PYTHON, "-m", "black", "."])
else:
    run("QS 2: Formatierung – Prüfen (black --check)", [PYTHON, "-m", "black", "--check", "."])

# ── 3. Sicherheits-Scan ───────────────────────────────────────────────────────
run(
    "QS 3: Sicherheits-Scan (bandit)",
    [
        PYTHON,
        "-m",
        "bandit",
        "-r",
        ".",
        "--exclude",
        "./.git,./data,./templates,./htmlcov",
        "-ll",  # only medium+ severity
        "-q",
    ],
)

# ── 4. Test-Coverage ──────────────────────────────────────────────────────────
run("QS 4: Tests + Coverage", [PYTHON, "-m", "coverage", "run", "tests.py"])
run("QS 4: Coverage Report (min. 70%)", [PYTHON, "-m", "coverage", "report", "--fail-under=70"])

# ── Zusammenfassung ───────────────────────────────────────────────────────────
print(f"\n{'═'*55}")
print("  QS-ZUSAMMENFASSUNG")
print(f"{'═'*55}")
for label, status in results.items():
    print(f"  {status}  {label}")

all_passed = all("PASSED" in s for s in results.values())
print(f"{'═'*55}")
if all_passed:
    print("  ✔  Alle QS-Checks bestanden!")
else:
    print("  ✘  Einige QS-Checks fehlgeschlagen.")
    sys.exit(1)
