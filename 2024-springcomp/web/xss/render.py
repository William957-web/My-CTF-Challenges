import asyncio
from flask import Flask, request, render_template, make_response
from pyppeteer import launch

app = Flask(__name__)

@app.route('/')
def main():
    response = make_response(render_template('index.html'))
    return response

@app.route('/g3tcookieeee')
def getcookie():
    response = make_response(render_template('index.html'))
    response.set_cookie('flag', 'ICED{XsS_repl@c3_WAf_c4n_B33_easily_pwned}')
    return response

@app.route('/visit', methods=['GET', 'POST'])
def visit():
    if request.method == 'POST':
        content = request.form['content']
        content = content.replace('%3C', '').replace('%3c', '').replace('%3E', '').replace('%3e', '').replace('<', '').replace('>', '')

        async def run():
            browser = await launch(headless=True)
            page = await browser.newPage()
            await page.goto("https://iced-2024comp-xss-onrender-com.onrender.com/g3tcookieeee")
            await asyncio.sleep(5)
            await page.goto("https://iced-2024comp-xss-onrender-com.onrender.com/?content="+content)
            await asyncio.sleep(5)
            await browser.close()
            return f"<h1>Admin have visited it!</h1><br>Final URL: {'https://iced-2024comp-xss-onrender-com.onrender.com/?content='+content}</br>"
        asyncio.get_event_loop().run_until_complete(run())
    else:
        return "Method not allowed"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80, use_reloader=False)
