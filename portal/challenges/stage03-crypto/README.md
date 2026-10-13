# Stage 03: Lazy Transmission

`message.txt` has been encoded in three layers. Reverse them in the following order:
1. Base64 decode
2. XOR with a single-byte key
3. ROT13

The resulting plaintext contains the flag.

Flag format: `CTF{<word>_<word>_<2 digits>}`.
