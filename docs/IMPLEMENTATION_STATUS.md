# Implementation Status

## Features
- Flask portal with six sequentially unlocked stages and session-based progress tracking
- Flag validation, progress reset, live scoreboard and elapsed-time tracking
- Two optional hints per stage, each with a point cost
- Stage 1 (OSINT): profile, directory and archive artefacts, including a decoy record and a handle confirmed through PNG metadata
- Stage 2 (Steganography): single-channel LSB payload with a single-byte XOR layer
- Stage 3 (Cryptography): Base64, XOR and ROT13 layered encoding
- Stage 4 (Forensics): server log containing decoy DEBUG entries
- Stage 5 (Networking): multi-stream PCAP with one decoy and one relevant conversation
- Stage 6 (Web): SQLite-backed login form behind a bypassable input filter, isolated on an internal network
- Docker Compose deployment

## Scoring
Each stage carries a base value of 100 to 250 points, scaled to difficulty. Revealing a hint deducts its cost from that stage's value, down to a minimum of 20 points. The total score and elapsed time are displayed on the portal and update live.

## Security Controls
- Flags stored only as peppered SHA-256 hashes (`portal/flags.json`)
- Random session signing key per deployment
- Stage 6 access enforced server-side
- Rate limiting on flag submissions
- Separate portal and stage networks, with the Stage 6 network marked internal
- Portal source mounted read-only
