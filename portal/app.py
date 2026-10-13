import os

from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)

# Other sites players are pointed to. This portal holds no flags, no scores and no state.
SUBMIT_URL = os.getenv('SUBMIT_URL', '').strip()   # flag submission site
BOX_URL = os.getenv('BOX_URL', '').strip()         # Stage 6 target box
CHALLENGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'challenges')

STAGES = [
    {'id': 1, 'title': 'The Public Trail', 'category': 'OSINT / Reconnaissance', 'difficulty': 'Easy',
     'dir': 'stage01-osint',
     'summary': 'Correlate the public artefacts, rule out the decoy record, and identify the infrastructure lead.',
     'files': ['company_profile.txt', 'employee_directory.txt', 'archive_note.txt', 'nightfall_archive.png']},
    {'id': 2, 'title': "Pixels Don't Lie", 'category': 'Steganography', 'difficulty': 'Moderate',
     'dir': 'stage02-steg',
     'summary': 'Recover the LSB payload hidden in the image, then undo the extra layer of obfuscation applied to it.',
     'files': ['pixels_dont_lie.png', 'README.md']},
    {'id': 3, 'title': 'Lazy Transmission', 'category': 'Cryptography', 'difficulty': 'Moderate',
     'dir': 'stage03-crypto',
     'summary': 'Peel back three layers of encoding to recover the transmitted message and its flag.',
     'files': ['message.txt', 'README.md']},
    {'id': 4, 'title': 'The Quiet Log', 'category': 'Digital Forensics', 'difficulty': 'Moderate',
     'dir': 'stage04-forensics',
     'summary': 'Separate the real incident evidence from decoy log entries.',
     'files': ['server.log', 'README.md']},
    {'id': 5, 'title': 'Packets in the Dark', 'category': 'Networking', 'difficulty': 'Hard',
     'dir': 'stage05-networking',
     'summary': 'Identify the correct TCP conversation among more than one candidate and recover the leaked evidence inside it.',
     'files': ['nightfall_incident.pcap', 'README.md']},
    {'id': 6, 'title': 'The Blackgate Gate', 'category': 'Web Security', 'difficulty': 'Hard',
     'dir': None,
     'summary': 'Bypass the login form protected by a naive input filter and retrieve the capstone flag.',
     'files': []},
]


def get_stage(n):
    if not 1 <= n <= 6:
        abort(404)
    return STAGES[n - 1]


@app.route('/')
def index():
    return render_template('index.html', stages=STAGES, submit_url=SUBMIT_URL)


@app.route('/stage/<int:n>')
def stage(n):
    return render_template('stage.html', stage=get_stage(n), submit_url=SUBMIT_URL, box_url=BOX_URL)


@app.route('/assets/<int:n>/<path:filename>')
def asset(n, filename):
    s = get_stage(n)
    if filename not in s['files']:
        abort(404)
    return send_from_directory(os.path.join(CHALLENGES_DIR, s['dir']), filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
