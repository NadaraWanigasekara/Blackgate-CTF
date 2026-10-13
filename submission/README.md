# BLACKGATE Submission Site (flags + scoring)

The only place flags are submitted, for all six stages .
Sequential unlock, hints with point costs, timer and scoreboard. Stores **hashed** flags only.

```bash
cp .env.example .env   # set SECRET_KEY
docker compose up -d --build
```
Open `http://<host>:8090`.  Change a flag: `python3 rehash_flag.py 6 'CTF{new_flag}'` then rebuild.
