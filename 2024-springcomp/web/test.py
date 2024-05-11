import requests as req
url='https://iced-2024comp-enum.onrender.com/@'
for i in range(1, 1001):
    web=req.get(url+str(i))
    if 'Wrong ID qq' not in web.text:
        print(i, web.text)
        break

