# Test Plan (three-site deployment)

1. Start `box/`, `portal/` and `submission/` with `docker compose up -d --build`; confirm three containers run (`docker ps`).
2. Portal (8080): all six stages listed, files for stages 1-5 download, Stage 6 shows the box link, no flag form anywhere.
3. Submission (8090): Stage 1 open, stages 2-6 locked; the scoreboard and timer are visible.
4. Solve stages 1-5 with the portal files and submit each flag on the submission site.
5. Submitting a flag for a locked stage is rejected; incorrect flags are rejected; more than 10 rapid attempts are throttled.
6. Reveal a hint: the stage value drops by its cost on the dashboard and stage page.
7. Stage 1: `CTF{priya_alwis}` rejected; `CTF{kasun_perera}`, `CTF{kasun.perera}` accepted (case-insensitive).
8. Box (9000): the Stage 5 credentials work, the filter blocks spaces/`--`/`#`, and a `/**/` injection works.
9. Submit the flag the box returns on the submission site; the timer stops and the final score shows.
10. Reset clears progress, score, hints and timer.
11. Confirm the box and the submission site share no network or secrets (separate compose projects).
12. Confirm a forged session cookie is rejected by the submission site.
