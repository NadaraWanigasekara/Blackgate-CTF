import hashlib
import hmac
import json
import os
import re
import secrets
import time

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
# Session signing key. Falls back to a random per-process key if none is set,
# so progress and score stored in the session cookie cannot be forged.
app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)

# Flags are stored only as peppered SHA-256 hashes (flags.json), never in source.
with open(os.path.join(os.path.dirname(__file__), 'flags.json')) as _f:
    _FLAGDATA = json.load(_f)


def normalize_stage1(submitted):
    """Normalise Stage 1 submissions, which players construct manually.
    Accepts any case, '.', '-' or '_' separators and an optional
    'blackgate_' prefix, reducing each to CTF{kasun_perera}."""
    m = re.fullmatch(r'ctf\{(.*)\}', submitted.strip().lower())
    if not m:
        return submitted
    inner = re.sub(r'[^a-z0-9]+', '_', m.group(1)).strip('_')
    if inner.startswith('blackgate_'):
        inner = inner[len('blackgate_'):]
    return 'CTF{%s}' % inner


def check_flag(n, submitted):
    if n == 1:
        submitted = normalize_stage1(submitted)
    digest = hashlib.sha256((_FLAGDATA['pepper'] + submitted).encode()).hexdigest()
    return hmac.compare_digest(digest, _FLAGDATA['hashes'][str(n)])


# In-memory rate limiter: maximum of 10 flag attempts per client per 60 seconds.
_ATTEMPTS = {}


def rate_limited():
    now = time.time()
    key = request.remote_addr
    hits = [t for t in _ATTEMPTS.get(key, []) if now - t < 60]
    if len(hits) >= 10:
        _ATTEMPTS[key] = hits
        return True
    hits.append(now)
    _ATTEMPTS[key] = hits
    return False


# Stage definitions: id, title, category, difficulty, base points, summary, hints.
# Each hint is (cost_in_points, hint_text); the cost is deducted when revealed.
STAGES = [
    {
        'id': 1,
        'title': 'The Public Trail',
        'category': 'OSINT / Reconnaissance',
        'difficulty': 'Easy',
        'points': 100,
        'flag_format': 'CTF{*****_******}',
        'summary': 'Correlate the public artefacts, rule out the decoy record, '
                    'and identify the infrastructure lead.',
        'hints': [
            (15, 'Two directory entries mention "Infrastructure". Read the '
                 'archive note carefully to see which one was actually active '
                 'during the incident.'),
            (25, 'There is no flag file for this stage. The PNG metadata confirms '
                 'the handle; the flag is that handle written as CTF{first_last} '
                 '(dots become underscores).'),
        ],
    },
    {
        'id': 2,
        'title': "Pixels Don't Lie",
        'category': 'Steganography',
        'difficulty': 'Moderate',
        'points': 150,
        'flag_format': 'CTF{******_******_**}',
        'summary': 'Recover the LSB payload hidden in the image, then undo the '
                    'extra layer of obfuscation applied to it.',
        'hints': [
            (20, 'The payload is not spread across all three colour channels. '
                 'Try isolating red, green and blue separately.'),
            (30, 'Once extracted, the bytes still are not readable text. Try a '
                 'single-byte XOR brute force over the recovered bytes.'),
        ],
    },
    {
        'id': 3,
        'title': 'Lazy Transmission',
        'category': 'Cryptography',
        'flag_format': 'CTF{******_******_**}',
        'difficulty': 'Moderate',
        'points': 150,
        'summary': 'Peel back three layers of encoding to recover the '
                    'transmitted message and its flag.',
        'hints': [
            (20, 'Start with a Base64 decode. The output will not yet be readable.'),
            (30, 'After Base64, the bytes are XORed with a single small key '
                 'before the Caesar layer. Brute force the XOR key, then try ROT13.'),
        ],
    },
    {
        'id': 4,
        'title': 'The Quiet Log',
        'category': 'Digital Forensics',
        'flag_format': 'CTF{******_******_**}',
        'difficulty': 'Moderate',
        'points': 150,
        'summary': 'Separate the real incident evidence from decoy log entries.',
        'hints': [
            (15, 'More than one DEBUG line has an X-TRACE value. Not all of '
                 'them are relevant to the incident.'),
            (20, 'The CACHE-REF marker timestamps the real incident window. '
                 'The X-TRACE line that matters is the one right after it.'),
        ],
    },
    {
        'id': 5,
        'title': 'Packets in the Dark',
        'category': 'Networking',
        'difficulty': 'Hard',
        'points': 200,
        'flag_format': 'CTF{******_******_**}',
        'summary': 'Identify the correct TCP conversation among more than one '
                    'candidate and recover the leaked evidence inside it.',
        'hints': [
            (20, 'There are two separate TCP conversations in this capture, on '
                 'two different ports. Only one of them matters.'),
            (25, 'Follow the TCP stream on port 8080, not 8081, and look at '
                 'the second request/response pair in it, not the first.'),
        ],
    },
    {
        'id': 6,
        'title': 'The Blackgate Gate',
        'category': 'Web Security',
        'difficulty': 'Hard',
        'points': 250,
        'flag_format': 'CTF{******_******_**}',
        'summary': 'Bypass the login form protected by a naive input filter and '
                    'retrieve the capstone flag.',
        'hints': [
            (25, 'The leaked credentials from Stage 5 log in directly, if you '
                 'still have them.'),
            (35, 'If you want to prove the SQL injection instead: the login '
                 'form rejects any literal space character. SQL has other ways '
                 'to separate keywords, such as inline comments (/**/).'),
        ],
    },
]

# Case file shown at the top of each stage: (heading, [paragraphs]).
# Paragraphs may contain <b> tags and are rendered as trusted markup.
# Stage 6 mentions the Stage 1 answer, so a case file is only ever rendered
# once its stage is unlocked (see case_file_for).
CASE_FILES = {
    1: [
        ('What is this system?', [
            'This is the <b>public footprint</b> of <b>Nightfall Freight Co.</b>, a '
            'Colombo-based logistics company: a company profile, a staff directory, '
            'an archive note and an archive photograph.'
        ]),
        ('What happened', [
            'On 1 September 2026 an intruder moved through Nightfall\'s network. '
            'Nobody has yet said whose infrastructure was used. Two directory '
            'entries mention Infrastructure, and only one of them was active '
            'during the incident.'
        ]),
        ('Your role', [
            'You are an authorised security investigator. Correlate the public '
            'records, rule out the decoy, and identify the Infrastructure Lead. '
            'Submit the handle as <b>CTF{first_last}</b>.'
        ]),
    ],
    2: [
        ('What is this system?', [
            'An ordinary-looking image recovered during the investigation. '
            'Nightfall\'s analysts believe it is carrying something that is not '
            'part of the picture.'
        ]),
        ('What happened', [
            'The intruder left data behind in plain sight, hidden in the pixels '
            'themselves and then scrambled with an extra layer of obfuscation.'
        ]),
        ('Your role', [
            'Recover the hidden payload, undo the obfuscation, and submit the '
            'flag it reveals.'
        ]),
    ],
    3: [
        ('What is this system?', [
            'A transmission intercepted from inside Nightfall\'s network, saved '
            'as <b>message.txt</b>.'
        ]),
        ('What happened', [
            'The sender was lazy: instead of real encryption they stacked three '
            'simple encoding layers on top of each other and hoped nobody would '
            'look.'
        ]),
        ('Your role', [
            'Peel the layers back in the right order and read the message. The '
            'flag is inside it.'
        ]),
    ],
    4: [
        ('What is this system?', [
            'The web server log from Nightfall\'s gateway host, <b>server.log</b>, '
            'covering the morning of the incident.'
        ]),
        ('What happened', [
            'Most of the log is routine traffic, and some of it has been padded '
            'with decoy debug entries. Somewhere in it is the evidence that '
            'marks the real incident window.'
        ]),
        ('Your role', [
            'Learn what normal looks like, separate the real evidence from the '
            'decoys, and submit the flag you recover.'
        ]),
    ],
    5: [
        ('What is this system?', [
            'A packet capture taken on Nightfall\'s network during the incident, '
            '<b>nightfall_incident.pcap</b>.'
        ]),
        ('What happened', [
            'The capture holds more than one TCP conversation, but only one of '
            'them carries the evidence. Account details for the person '
            'responsible for the gateway crossed the network unprotected.'
        ]),
        ('Your role', [
            'Find the right conversation, recover the leaked evidence, and submit '
            'the flag. Keep what you learn: you will need it for the final stage.'
        ]),
    ],
    6: [
        ('What is this system?', [
            'This is the <b>Admin Gateway</b> of <b>Nightfall Freight Co.</b>, a '
            'Colombo-based logistics company. It is the web console used to '
            'control shipment manifests and dispatch records, and it is the '
            'final system standing between an outsider and the company\'s core '
            'data.'
        ]),
        ('What happened', [
            'On 1 September 2026 an intruder moved through Nightfall\'s network. '
            'Investigators have already traced the public trail to '
            '<b>Kasun Perera</b>, the Infrastructure Lead who owns and maintains '
            'this gateway. A packet capture taken during the incident shows his '
            'account details were sent across the network in clear text.',
            'Since the breach, Nightfall\'s IT team has put <b>Nightfall Input '
            'Guard v1</b> in front of the login form. They believe it makes the '
            'gateway safe. Management would like that belief tested.',
        ]),
        ('Your role', [
            'You are an authorised security investigator. Get past the gate and '
            'retrieve the capstone flag, which proves you had access to the '
            'console. Work only against this host; everything else in the lab '
            'is out of scope.'
        ]),
    ],
}


def case_file_for(n):
    """Case file for stage n, or None if the stage is out of range or locked."""
    if not 1 <= n <= 6:
        return None
    if n > 1 and (n - 1) not in session['completed']:
        return None
    return {'stage': n, 'sections': CASE_FILES[n]}


def current_stage_id():
    """First stage not yet completed, or None when all six are done."""
    done = set(session['completed'])
    for s in STAGES:
        if s['id'] not in done:
            return s['id']
    return None


def flash(kind, message):
    session['flash'] = [kind, message]


HINT_FLOOR = 20  # minimum points a stage can be worth after hints


def stage_by_id(n):
    return STAGES[n - 1]


@app.before_request
def init_session():
    session.setdefault('completed', [])
    session.setdefault('earned', {})       # {stage_id: points_awarded}
    session.setdefault('hints_used', {})   # {stage_id: [hint_index, ...]}
    session.setdefault('start_ts', None)   # set when Stage 1 is first opened
    session.setdefault('finish_ts', None)


def score_for_stage(n):
    """Points a stage is worth right now, after any hints already used."""
    stage = stage_by_id(n)
    used = session['hints_used'].get(str(n), [])
    cost = sum(stage['hints'][i][0] for i in used)
    return max(stage['points'] - cost, HINT_FLOOR)


def total_score():
    return sum(session['earned'].values())


def dashboard_context():
    cur = current_stage_id()
    flashed = session.pop('flash', None)
    return dict(
        stages=STAGES,
        completed=set(session['completed']),
        result=flashed,
        total_score=total_score(),
        start_ts=session['start_ts'],
        finish_ts=session['finish_ts'],
        current_points={s['id']: score_for_stage(s['id']) for s in STAGES},
        earned=session['earned'],
        current_stage=cur,
        case_file=case_file_for(cur) if cur else None,
    )


@app.route('/')
def index():
    return render_template('index.html', **dashboard_context())


@app.post('/submit')
def submit():
    try:
        n = int(request.form.get('stage', '0'))
    except ValueError:
        n = 0

    flag = request.form.get('flag', '').strip()
    completed = set(session['completed'])

    if not 1 <= n <= 6:
        return redirect(url_for('index'))

    # A completed stage cannot be submitted again; its points are awarded once.
    if n in completed:
        flash('success', f'Stage {n} is already completed. Your points have already been awarded.')
        return redirect(url_for('index'))

    if n == 1 and session.get('start_ts') is None:
        session['start_ts'] = time.time()   # start timer on first Stage 1 submission

    if n > 1 and (n - 1) not in completed:
        flash('error', f'Stage {n} is locked. Complete Stage {n - 1} first.')
    elif rate_limited():
        flash('error', 'Too many attempts. Wait a minute and try again.')
    elif check_flag(n, flag):
        if n not in completed:
            completed.add(n)
            session['completed'] = sorted(completed)
            earned = dict(session['earned'])
            earned[str(n)] = score_for_stage(n)
            session['earned'] = earned
            if n == 6:
                session['finish_ts'] = time.time()
        if n == 6:
            flash('success', 'Capstone flag accepted. Operation Blind Dock complete. '
                             f'Final score: {total_score()} pts.')
            return redirect(url_for('index'))
        # Correct flag: open the next stage, with its case file.
        flash('success', f'Stage {n} accepted (+{session["earned"].get(str(n), 0)} pts). '
                         f'Stage {n + 1} is now unlocked.')
        return redirect(url_for('stage', n=n + 1))
    else:
        flash('error', 'Incorrect flag. Check the challenge evidence and try again.')

    # Wrong flag / locked / rate limited: stay on the stage that was attempted.
    return redirect(url_for('stage', n=n))


@app.route('/stage/<int:n>')
def stage(n):
    """Hints and scoring info for one stage."""
    if not 1 <= n <= 6:
        return redirect(url_for('index'))
    completed = set(session['completed'])
    locked = n > 1 and (n - 1) not in completed
    if n == 1 and session.get('start_ts') is None:
        session['start_ts'] = time.time()   # start timer when Stage 1 is first opened
    used = session['hints_used'].get(str(n), [])
    return render_template(
        'stage.html',
        stage=stage_by_id(n),
        locked=locked,
        hints_used=used,
        current_points=score_for_stage(n),
        case_file=case_file_for(n),
        done=n in completed,
        earned_points=session['earned'].get(str(n)),
        total_score=total_score(),
        result=session.pop('flash', None),
    )


@app.post('/hint/<int:n>/<int:idx>')
def reveal_hint(n, idx):
    if not 1 <= n <= 6:
        return redirect(url_for('index'))
    completed = set(session['completed'])
    locked = n > 1 and (n - 1) not in completed
    stage_data = stage_by_id(n)
    if not locked and 0 <= idx < len(stage_data['hints']):
        used = dict(session['hints_used'])
        stage_hints = list(used.get(str(n), []))
        if idx not in stage_hints:
            stage_hints.append(idx)
            used[str(n)] = stage_hints
            session['hints_used'] = used
    return redirect(url_for('stage', n=n))


@app.post('/reset')
def reset():
    session['completed'] = []
    session['earned'] = {}
    session['hints_used'] = {}
    session['start_ts'] = None
    session['finish_ts'] = None
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
