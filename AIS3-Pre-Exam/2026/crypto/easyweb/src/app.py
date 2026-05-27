import os
import json
from binascii import Error as BinasciiError
from html import escape
from urllib.parse import urlencode
from urllib.request import urlopen

from Crypto.Cipher import AES
from flask import Flask, make_response, request


app = Flask(__name__)

KEY = os.urandom(16)
DATA_DIR = "data"
COOKIE_NAME = "session"
SITE_KEY = "6Leq69ssAAAAADwiN4eEAcohhMxLrEbZo_UlkmDR"
SECRET_KEY = "6Leq69ssAAAAADPvneyvukEVWZGotd_APb1akl4V"
FLAG = "AIS3{copy_and_paste_the_flag}"
os.makedirs(DATA_DIR, exist_ok=True)


def pad(value):
    size = 16 - (len(value) % 16)
    return value + bytes([size]) * size


def unpad(value):
    if not value:
        raise ValueError("empty")
    size = value[-1]
    if size < 1 or size > 16 or value[-size:] != bytes([size]) * size:
        raise ValueError("padding")
    return value[:-size]


def lock(value):
    return AES.new(KEY, AES.MODE_ECB).encrypt(pad(value.encode())).hex()


def unlock(value):
    raw = bytes.fromhex(value)
    return unpad(AES.new(KEY, AES.MODE_ECB).decrypt(raw)).decode()


def page(body):
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>pen 🖊️</title>
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
</head>
<body>
{body}
</body>
</html>"""


def form(message=""):
    return page(f"""<h1>pen 🖊️</h1>
{message}
<form method="post" id="pen-form" onsubmit="return beforeSubmit(event)">
<input name="name" id="name">
<input name="note">
<input type="hidden" name="g-recaptcha-response" id="captcha-response">
<input type="hidden" name="captcha-client-error" id="captcha-client-error">
<div class="g-recaptcha" data-sitekey="{SITE_KEY}" data-size="invisible" data-callback="afterCaptcha" data-error-callback="captchaError" data-expired-callback="captchaExpired"></div>
<div id="captcha-status"></div>
<button>go</button>
</form>
<script>
function afterCaptcha(token) {{
  document.getElementById("captcha-response").value = token;
  document.getElementById("pen-form").submit();
}}

function sendCaptchaError(message) {{
  document.getElementById("captcha-client-error").value = message;
  document.getElementById("captcha-status").innerText = message;
  document.getElementById("pen-form").submit();
}}

function captchaError() {{
  sendCaptchaError("captcha client error");
}}

function captchaExpired() {{
  document.getElementById("captcha-response").value = "";
  document.getElementById("captcha-status").innerText = "captcha expired";
}}

function beforeSubmit(event) {{
  var name = document.getElementById("name").value;
  if (name.startsWith("/") || name.startsWith(".")) {{
    document.getElementById("captcha-status").innerText = "bad hacker";
    return false;
  }}
  if (document.getElementById("captcha-response").value) {{
    return true;
  }}
  event.preventDefault();
  try {{
    if (!window.grecaptcha) {{
      sendCaptchaError("captcha script not loaded");
      return false;
    }}
    grecaptcha.execute();
  }} catch (error) {{
    sendCaptchaError("captcha execute failed: " + error.message);
  }}
  return false;
}}
</script>""")


def captcha_ok():
    token = request.form.get("g-recaptcha-response", "")
    client_error = request.form.get("captcha-client-error", "")
    if client_error:
        print(f"captcha client error: {client_error}", flush=True)
        return False, client_error
    if not token:
        print("captcha failed: missing token", flush=True)
        return False, "missing token"

    data = urlencode(
        {
            "secret": SECRET_KEY,
            "response": token,
            "remoteip": request.remote_addr or "",
        }
    ).encode()

    try:
        with urlopen("https://www.google.com/recaptcha/api/siteverify", data, timeout=5) as res:
            result = json.loads(res.read().decode())
            print(f"captcha verify response: {result}", flush=True)
            if result.get("success") is True:
                return True, ""
            errors = ",".join(result.get("error-codes", ["unknown"]))
            return False, errors
    except (OSError, json.JSONDecodeError) as e:
        print(f"captcha verify error: {e}", flush=True)
        return False, str(e)


@app.route("/", methods=["GET", "POST"])
def index():
    resp = make_response("")
    saved = request.cookies.get(COOKIE_NAME)

    if saved:
        try:
            filename = unlock(saved)
            with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
                note = f.read()
            resp.set_data(page(f"<h1>pen 🖊️</h1><pre>{escape(note)}</pre>"))
            return resp
        except (BinasciiError, OSError, UnicodeDecodeError, ValueError):
            resp.delete_cookie(COOKIE_NAME)
            resp.set_data(form())
            return resp

    if request.method == "GET":
        resp.set_data(form())
        return resp

    name = request.form.get("name", "")
    note = request.form.get("note", "")

    if not name or name[0] in "./":
        resp.set_data("bad hacker")
        resp.status_code = 403
        return resp

    filename = f"{name}.txt"
    if filename[0] in "./":
        resp.set_data("bad hacker")
        resp.status_code = 403
        return resp

    ok, reason = captcha_ok()
    if not ok:
        resp.set_data(form(f"no ({escape(reason)})"))
        return resp

    resp.set_cookie(COOKIE_NAME, lock(filename), httponly=True, samesite="Lax")

    try:
        with open(os.path.join(DATA_DIR, filename), "w", encoding="utf-8") as f:
            f.write(note)
        resp.headers["Location"] = "/"
        resp.status_code = 302
    except OSError as e:
        print(f"write error: {e}", flush=True)
        resp.set_data("error")
        resp.status_code = 500
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=48763, debug=False)
