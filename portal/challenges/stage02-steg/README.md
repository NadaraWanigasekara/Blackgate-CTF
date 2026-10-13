# Stage 02: Pixels Don't Lie

File: `pixels_dont_lie.png`

The image contains an LSB payload hidden in a single colour channel. The extracted bytes are further obfuscated with a single-byte XOR key. Extracting the least significant bits from all channels will not produce meaningful output; identify the correct channel first, then recover the XOR key.

Suggested tools: zsteg, CyberChef (XOR Brute Force), or a short Python script.

Flag format: `CTF{<word>_<word>_<2 digits>}`.
