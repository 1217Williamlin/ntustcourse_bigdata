import pandas as pd
from bs4 import BeautifulSoup
import json
import requests
import re
import time
from tqdm import tqdm
import xlsxwriter



with open('keyword6.txt','r',encoding='utf-8') as file:
    keywords = []
    for word in file.readlines():
        keywords.append(word.strip())

def remove_duplicate(target):
    result = []
    for i in target:
        if i not in result:
            result.append(i)
    return result

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
# 請填10個搜尋詞彙
pages = 6
df = pd.DataFrame()
for keyword in keywords:
    urls = []
    for page in range(1, pages):
        url = 'https://m.momoshop.com.tw/search.momo?_advFirst=N&_advCp=N&curPage={}&searchType=1&cateLevel=2&ent=k&searchKeyword={}&_advThreeHours=N&_isFuzzy=0&_imgSH=fourCardType'.format(page, keyword)
        print(url)
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, features="lxml")
            """
            利用for迴圈得到畫面上所有商品的連結，並儲存到urls陣列裡面
            """
            for item in soup.select('li.goodsItemLi > a'):
                urls.append(item['href'])
        else:
            print("沒有資料")
            break
        #檢查是否有重複的urls並排除
    urls = remove_duplicate(urls)
    for i, url in enumerate(tqdm(urls)):
        columns = []
        values = []
        url = 'https://m.momoshop.com.tw/' + url
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, features="lxml")
        # 標題
        try:
            title = soup.find('meta', {'property': 'og:title'}).get('content')
        except:
            try:
                title = soup.find('p', class_='fprdTitle').text   #title = soup.find('h3', id='goodsName').text
            except:
                title = soup.find('title').text
                title = title.replace(' - momo購物網', '')
        # 品牌
        try:
            brand = soup.find('meta', {'property':'product:brand'})['content']
        except:
            brand = ''
        # 連結
        try:
            link = soup.find('meta', {'property':'og:url'})['content']
        except:
            continue
        # 原價
        try:
            # 正規化內容，移除不必要的字元，例如\n\r等等
            price = soup.select('td > del')[0].text
            price = re.sub(r'\n|\r',"", price) 
        except:
            price = ''
        # 特價
        try:
            amount = soup.find('p', {'class':"priceTxtArea"}).text
            amount = re.sub(r'\n|\r','', amount)
        except:
            amount = ''
                # 類型
        cate = ''.join([i.text for i in soup.findAll('article', {'class': 'pathArea'})])  #join 目的是為了新生成一個新字串
        cate = re.sub('\n|\xa0', ' ', cate)
                # 描述
        try:
            desc = soup.find('div', {'class': 'Area101'}).text
            desc = re.sub('\r|\n| ', '', desc)
        except:
            desc = 'Nan'

        print('==================  {}  =================='.format(i))
        print(title)
        print(brand)
        print(link)
        print(amount)
        print(cate)

        columns += ['title', 'brand', 'link', 'price', 'amount', 'cate', 'desc']
        values += [title, brand, link, price, amount, cate, desc]

        # 規格
        for i in soup.select('div.attributesArea > table > tr'):
            try:
                # 整理規格的內容
                try:
                    column = i.find('th').text
                    column = re.sub('\n|\r| ', '', column)
                except:
                    column = ''
                value = ''.join([j.text for j in i.findAll('li')])
                value = re.sub('\n|\r| ', '', value)
                if column not in columns:
                    columns.append(column)
                    values.append(value)
            except:
                pass
        ndf = pd.DataFrame(data=values, index=columns).T
        df = pd.concat([df,ndf], ignore_index=True)
df.info()

local_time = time.localtime(time.time())
year = local_time.tm_year
month = local_time.tm_mon
day = local_time.tm_mday
# 儲存檔案
df.to_excel('./B10808006_林亭毅_爬蟲_作業一_6.xlsx', engine='xlsxwriter')