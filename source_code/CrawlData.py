import json
import ast
from kafka import KafkaProducer
from bs4 import BeautifulSoup
import requests
import urllib.request
import argparse


HEADERS = ({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})




if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('--st', type=int, default=1)
    args.add_argument('--end', type=int, default=200)
    args = args.parse_args()
    baseurl='https://meeyland.com'
    producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    ##page number tu 1 -1000
    page_from = args.st
    page_to =  args.end
    total = 0
    for p in range(page_from,page_to+1):
        page_crawl = urllib.request.urlopen('https://meeyland.com/mua-ban-nha-dat/chung-cu-ha-noi/page-'+str(p)+'?p=f55eb37fc612f37244c7a9bbb0c8abf3') # tinh den ngay 30/12/2021
        soup = BeautifulSoup(page_crawl, 'html.parser').findAll('div', class_='card-title')
        if not len(soup) == 24 :
            print(len(soup)) #check missing
        for element in soup:
            link = element.find('a',class_='call-traking').get('href')
            detail = urllib.request.urlopen(baseurl+link)
            print("Crawling:" + str(baseurl+link))
            detail_parse = BeautifulSoup(detail, 'html.parser')
            find_item = detail_parse.find("div", {"id": "meey-value"})
            if find_item == None:
                print("error: "+baseurl+link)
                continue
            related_houses = detail_parse.find("div", {"id": "related-article-detail"})
            # loan_rates = detail_parse.find("div", {"id": "meey-caculator"})
            json_res = find_item.get('data-article')
            json_laste = json.loads(json_res) 
            json_laste["related_houses"] = str(related_houses)
            # json_laste["loan_rates"] = str(loan_rates)
            producer.send('amazon-laptops', value=json_laste)
        total+=1
        print("Crawled page :" + str(p))
    print("Finished ! Total : " + str(total))



