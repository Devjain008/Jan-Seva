# render.yaml
# ─────────────────────────────────────────────────────────────────────────────
# OPTION A — SQLite + Persistent Disk  (easiest, ~$1/month)
# OPTION B — PostgreSQL               (free, most reliable)
# Uncomment the option you want to use.
# ─────────────────────────────────────────────────────────────────────────────

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

      # ── OPTION A: SQLite on Persistent Disk ───────────────
      # Uncomment these 3 lines and the `disk` block below.
      # Comment out the DATABASE_URL line in Option B.
      #
      # - key: SQLITE_PATH
      #   value: /data/jansevadb.sqlite

      # ── OPTION B: PostgreSQL (recommended) ────────────────
      # After creating a PostgreSQL service on Render,
      # link it here. Render auto-injects DATABASE_URL.
      #
      # - key: DATABASE_URL
      #   fromDatabase:
      #     name: bfo-janseva-db
      #     property: connectionString

    # ── OPTION A: Persistent Disk ─────────────────────────
    # Uncomment this block if using SQLite.
    #
    # disk:
    #   name: janseva-data
    #   mountPath: /data
    #   sizeGB: 1

# ── OPTION B: PostgreSQL service definition ───────────────
# Uncomment if you want Render to manage the DB too.
#
# databases:
#   - name: bfo-janseva-db
#     databaseName: janseva
#     user: janseva_user
#     plan: free