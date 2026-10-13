import os
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)
FLAG = os.environ['FLAG']  # supplied via docker-compose
DB = '/tmp/nightfall.db'

PAGE = '''<!doctype html>
<meta name="viewport" content="width=device-width">
<title>Nightfall Admin</title>
<style>
body{font-family:system-ui;background:#101722;color:#eee;max-width:720px;margin:70px auto;padding:20px}
input,button{width:100%;padding:12px;margin:5px 0;box-sizing:border-box}
input{background:#182536;color:#fff;border:1px solid #345}
button{cursor:pointer}
.box{border:1px solid #345;padding:24px;border-radius:14px}
</style>
<div class="box">
  <h1>Nightfall Freight &mdash; Admin Gateway</h1>
  <p>Restricted system. Authorised personnel only. Protected by Nightfall Input Guard v1.</p>
  <form method="post">
    <input name="username" placeholder="Username">
    <input name="password" type="password" placeholder="Password">
    <button>Sign in</button>
  </form>
  {% if msg %}<p>{{ msg }}</p>{% endif %}
</div>
'''


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
    conn.execute('DELETE FROM users')
    conn.execute('INSERT INTO users VALUES (?, ?)', ('kasun.perera', 'nightfall-demo'))
    conn.commit()
    conn.close()


init_db()


def blocked_by_waf(value):
    # Nightfall Input Guard v1: blocks spaces, '--' and '#'.
    # Inline SQL comments (/**/) are not filtered and can substitute for whitespace.
    return ' ' in value or '--' in value or '#' in value


@app.route('/', methods=['GET', 'POST'])
def home():
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if blocked_by_waf(username) or blocked_by_waf(password):
            msg = 'Blocked by Nightfall Input Guard: request contains a disallowed character.'
        else:
            conn = sqlite3.connect(DB)
            query = (
                "SELECT username FROM users WHERE username='"
                + username + "' AND password='" + password + "'"
            )
            try:
                row = conn.execute(query).fetchone()
                msg = 'Access granted. Flag: ' + FLAG if row else 'Access denied.'
            except sqlite3.Error:
                msg = 'Database rejected the input.'
            finally:
                conn.close()

    return render_template_string(PAGE, msg=msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
