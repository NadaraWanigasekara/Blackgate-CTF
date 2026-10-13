# BLACKGATE Box (Stage 6, "Nightfall Admin Gateway")

Deliberately vulnerable login (the page opens with the case-file backstory for players) (SQL injection behind a weak space/`--`/`#` filter).
Self-contained: own network, own `.env`, nothing shared with the platform.

```bash
cp .env.example .env     # FLAG must match the Stage 6 hash in platform/flags.json
docker compose up -d --build
```
Reachable at `http://<host>:9000`. Set `BOX_BIND=127.0.0.1` to keep it local-only.

Containment: non-root user, read-only filesystem, all capabilities dropped,
no-new-privileges, 256 MB / 0.5 CPU / 100-process limits. The SQLite DB lives in a
tmpfs and resets on restart. Deploy it on a separate host or VLAN if possible, and
never expose it to the internet.
