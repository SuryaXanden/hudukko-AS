import re, json, requests
from flask import Flask, redirect, url_for, request, Response, render_template, jsonify
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41 Safari/537.36'}
results = set()

def atd(img, link, price, title):
    global results
    results.add((img, link, price, title))

def makeList():
    global results
    results = [list(i) for i in results]

def sortByprice():
    global results
    try:
        results = sorted(results, key=lambda x: float(x[3]))
    except:
        pass

def sanitizeAmazon(tempap):
    san = re.sub('\\,', '', tempap, 0, re.MULTILINE)
    san = float(san)
    return san

def makeJSON(item,price):
    global results
    makeList()
    snapdeal_url = 'http://hudukkoli.herokuapp.com/api/scrapeSnapdeal?product='+str(item)+'&price='+str(price)+''
    snapdeal_response = requests.get(snapdeal_url)
    snapdeal_data = snapdeal_response.json()
    arrayOfSnapdealJSON = []
    for dic in snapdeal_data:
        arrayOfSnapdealJSON.append(list(dic.values()))
    results = results + arrayOfSnapdealJSON
    JSON = []
    sortByprice()
    if len(results) > 0:
        for i in results:
            try:
                JSON.append({'link':str(i[0]), 'image':str(i[1]), 'title':str(i[2]), 'price':str(i[3])})
            except:
                pass
            results = json.dumps(JSON)
    return results

def amazon(item,price):
    global headers
    url = str('https://www.amazon.in/s/ref=sr_st_price-asc-rank?keywords=' + str(item) + ' below ' + str(price) + '')
    page = requests.get(url, headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    main_ul = soup.find('ul', id='s-results-list-atf')
    try:
        lis = main_ul.findAll('li')
        for li in main_ul:
            maindiv = li.div.div
            a_tag = maindiv.div.a
            link = str(a_tag['href'])
            if link is not None:
                img = str(a_tag.img['src'])
                title = str(a_tag.img['alt'])
                if img is not None:
                    checking = maindiv.div.div.find_next_sibling('div').div.find_next_sibling('div').div.div.a.get_text().strip().split(' ')
                price = float(sanitizeAmazon(str(checking[0])))
                if price <= price:
                    atd(link, img , title, str(price))
    except AttributeError:
        print('Amazon in except')
        amazon(item,price)

def flow(item,price):
    amazon(item,price)
    print(makeJSON(item,price))
    # return makeJSON() #uncomment

flow('shoes','5000')

'''
@app.route("/")
def index():
    item = request.args.get('item')
    price = request.args.get('price')
    item, price = (item.strip(),int(int(price) * 1.1))
    print(item,price)
    fin = flow(item,price)
    return (fin, 200, 'application/json')

if __name__ == '__main__':
    # app.run()
    app.run(debug=True)

#http://127.0.0.1:5000/?item=shoes&price=6000
'''
