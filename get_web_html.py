import requests
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
}

url = "https://www.google.com/search?q=top+10+electricians+in+area&near=california"
response = requests.get(url=url, headers=headers)
page_content = response.text

with open('./url-content.html', 'w', encoding='utf8') as fp:
    fp.write(page_content)