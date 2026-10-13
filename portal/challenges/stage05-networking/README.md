# Stage 05: Packets in the Dark

File: `nightfall_incident.pcap`

The capture contains two TCP conversations on different ports, only one of which holds the evidence. Use Wireshark's Statistics > Conversations (TCP) to list them, then Follow > TCP Stream to determine which one responds to a request for evidence.

Flag format: `CTF{<word>_<word>_<2 digits>}`.
