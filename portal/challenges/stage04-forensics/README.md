# Stage 04: The Quiet Log

Analyse `server.log`. Several DEBUG entries contain a Base64-encoded `X-TRACE` value, but not all of them relate to the incident. Establish the normal INFO request pattern, then use the timestamp of the `CACHE-REF` entry to identify the relevant X-TRACE value.

Flag format: `CTF{<word>_<word>_<2 digits>}`.
