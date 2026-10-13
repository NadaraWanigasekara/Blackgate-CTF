#!/usr/bin/env python3
"""Change a stage's flag: python3 rehash_flag.py 6 'CTF{new_flag}'
Updates flags.json (hash only). For stage 6, also put the same value in box/.env as FLAG."""
import hashlib, json, sys
n, flag = sys.argv[1], sys.argv[2]
d = json.load(open('flags.json'))
d['hashes'][n] = hashlib.sha256((d['pepper'] + flag).encode()).hexdigest()
json.dump(d, open('flags.json', 'w'), indent=1)
print(f'Stage {n} hash updated.')
