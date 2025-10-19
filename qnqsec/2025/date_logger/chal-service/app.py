from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import secrets

app = Flask(__name__)
messages = {
    "2025/09/24": "00ps, I should have sometime to contribute challenges right?\nBut I want to date ...",
    "2025/10/03": "Hmm... I forgot something but just can't remember them ;P",
    "2025/10/08": "WTF, IS DEADLINE, FINE, THE FLAG IS QnQSec{F_u_L1NuX_:cry:}"
}

@app.route("/", methods=["GET", "POST"])
def search_message():
    search = request.args.get("search", "") or request.form.get("search", "")
    filename = request.args.get("filename", "") or request.form.get("filename", "")

    if not search or not filename:
        return "Missing parameters: need search and filename", 400

    match_date = None
    for date, msg in messages.items():
        if search in msg:
            match_date = date
            break
    
    if match_date:
        safe_filename = secure_filename(filename)
        random_hex = secrets.token_hex(8) 
        out_path = os.path.join("/tmp", random_hex + safe_filename)
        with open(out_path, "w") as f: 
            f.write(match_date) 

    return f"Whale said womp!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337, debug=False)
