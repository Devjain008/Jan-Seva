
services:
  - type: web
    name: bfo-janseva
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: bash run.sh
    envVars:

      # ── Common ────────────────────────────────────────────
      - key: PYTHONUNBUFFERED
        value: "1"
