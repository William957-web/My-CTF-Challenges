from flask import Flask, request, jsonify, abort, redirect
from flask_cors import CORS
import subprocess
import threading

app = Flask(__name__)
CORS(app, origins=["http://localhost:5000"])

def terminate_process(process):
    process.terminate()
    print("Process terminated after 10 minutes.")

# 十句話字典
sentences = {
    "1": "Hello, world!",
    "2": "Flask is great for web development.",
    "3": "Security is important in web applications.",
    "4": "Python is a powerful and flexible language.",
    "5": "Always sanitize user input.",
    "6": "CTF challenges improve cybersecurity skills.",
    "7": "Web applications should implement proper access controls.",
    "8": "Never trust user input blindly.",
    "9": "Debugging is a crucial part of development.",
    "10": "Use logging to monitor application behavior.",
    "11": "The flag is AIS3{R3t_2_fL4g_31352a}"
}

@app.route('/search', methods=['GET'])
def search():
    if request.remote_addr != "127.0.0.1":
        abort(403)
    
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    results = [f"<br>{sentence}</br>" for sentence in sentences.values() if query in sentence]
    
    if not results:
        return redirect("/")
    
    return jsonify({"results": results})

@app.route('/visit', methods=['GET'])
def visit():
    url = request.args.get('url')
    if url.startswith('http://') == False and url.startswith('https://') == False:
        return "Bad Hacker"
    process = subprocess.Popen(['chromium', url, '--headless', '--disable-gpu', '--no-sandbox'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    timer = threading.Timer(600, terminate_process, [process])
    timer.start()
    return "Admin is visiting your page!"

@app.route('/', methods=['GET'])
def main():
    return "Hello World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
