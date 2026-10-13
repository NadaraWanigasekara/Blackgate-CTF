# BLACKGATE: Operation Blind Dock (three separate sites)

| Folder | Site | Port | Role |
|---|---|---|---|
| `submission/` | Flag submission | 8090 | **All flags (1-6) are submitted here.** Scoring, hints, timer, sequential unlock. Hashed flags only. |
| `portal/` | Challenge portal | 8080 | Briefings and downloadable evidence for each stage. Stateless. |
| `box/` | Stage 6 box | 9000 | Deliberately vulnerable target. Isolated and hardened. |
| `instructor/`, `docs/` | - | - | Solutions and test plan. Never deploy. |

Each folder has its own `docker-compose.yml` and `.env`; deploy them on one machine or three.
The sites only link to each other by URL (`PORTAL_URL`, `BOX_URL`, `SUBMIT_URL` in each `.env`).

## Run (one machine)
```bash
cd blackgate-split
./start.sh      # builds and starts all three sites   (use: sudo ./start.sh if Docker needs sudo)
./stop.sh       # stops them
```
Players: start at http://localhost:8080 (files), submit at http://localhost:8090, box at http://localhost:9000.
For other machines, replace `localhost` with the host IP in the three `.env` files (`portal`, `submission`), then run `./start.sh` again.
