from __future__ import print_function

import ast
import json
from bs4 import BeautifulSoup
import requests
from elasticsearch import Elasticsearch
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


# def parseReviews(rw):
#   reviews = BeautifulSoup(rw, 'html.parser')
#   rate = ast.literal_eval(reviews.find("span",{"data-hook":"rating-out-of-text"}).getText().split()[0])
#   number = ast.literal_eval(reviews.find("div",{"data-hook":"total-review-count"}).find("span").getText().replace(",","").split()[0])
#   arrrw = []
#   for rev in reviews.findAll("div",{"data-hook":"review-collapsed"}):
#     arrrw.append(rev.find("span").getText().strip())
#   return rate , number ,arrrw

# def processLaptopDetails(details):
#   productDetails = BeautifulSoup(details, 'html.parser')
#   dictInfo ={}
#   dictTmp = {}
#   for content in productDetails.find('table',{"id":"productDetails_techSpec_section_1"}).findAll("tr"):
#     key = str(content.find("th").getText()).strip().replace("\u200e","")
#     val = str(content.find("td").getText()).strip().replace("\u200e","")
#     dictTmp[key] = val
#   for content in productDetails.find('table',{"id":"productDetails_techSpec_section_2"}).findAll("tr"):
#     key = str(content.find("th").getText()).strip().replace("\u200e","")
#     val = str(content.find("td").getText()).strip().replace("\u200e","")
#     dictTmp[key] = val
#   table2 = productDetails.find('table',{"id":"productDetails_detailBullets_sections1"}).findAll("tr")
#   dictInfo["Cau Hinh"] = dictTmp
#   dictInfo["ASIN"] = str(table2[0].find("td").getText()).strip()
#   dictInfo["bestSellersRank"] = str(table2[2].find("span").get_text()).strip()
#   dictInfo["dateFirstAvailable"] = str(table2[2].find("td").getText()).strip()
#   return dictInfo

# def parserRelateLaptop(relateLaptops):
#   productDetails = BeautifulSoup(relateLaptops, 'html.parser')
#   dictTmp = {}
#   asinlist = ''
#   asinLinkList = ""
#   asinNameList = ""
#   for content in productDetails.find('ol',{"class":"a-carousel"}).findAll("li"):
#     div_relate = content.find('div',{"class":"p13n-asin"})
#     asinlist += str(div_relate.get('data-asin')) +" "
#     a = div_relate.find('a',{"class":"a-link-normal"})
#     asinLinkList += str(a.get("title")) +"\n"
#     asinNameList += str(a.get("href")) +"\n"
#   dictTmp["relatedListASIN"] = asinlist
#   dictTmp["relatedListLink"] = asinLinkList
#   dictTmp["relatedListName"] = asinNameList
#   return dictTmp



def pushElastics(x):
    es = Elasticsearch([{'host': "elasticsearch", 'port': "9200"}],timeout=5,max_retries=100)
    print("Pushinng to Elasticsearch...")
    for record in x:
      res_push = es.index(index='data_nha_hanoi', ignore=400, doc_type='data_nha',id=str(record[0]), body=record[1])
      print(res_push)
    es.transport.close()
    # print(json.dumps(x[1], indent = 3))

def printRdd(x):
    print(json.dumps(x[1], indent = 3))

def writeRDD(rdd):
    print("-------------------------------------------------------")
    count_recieve = rdd.count()
    print("RDDs RECEIVED : " + str(count_recieve))
    # rdd.foreach(pushElastics)
    # make sure ES is up and running
    if(count_recieve > 0):
      # rdd.saveAsTextFile("hdfs://namenode:9000/Crawl_nha/part-.txt")
      try:
        res_code = requests.get('http://elasticsearch:9200/').status_code
      except:
        print("Connection refused")
        res_code = 404
      #connect to our cluster
      if (res_code == 200):
        print("connected to elasticsearch status_code:"+ str(res_code))
        rdd.foreachPartition(pushElastics)
      else:
        print("cannot connect to elasticsearch:"+ str("Connection refused"))
      rdd.foreach(printRdd)
      print("TAKE(1) RDD TEST: " + str(json.dumps(rdd.take(1), indent = 3)))
    print("-------------------------------------------------------")



def parseData(x):
    y = json.loads(x[1])
    y["ID"] = y["_id"]
    y.pop("_id", None)
    # tmp =  processLaptopDetails(y["laptopDetails"])
    # y["idhash"] = tmp["ASIN"]
    # y["laptopDetails"] = tmp["Cau Hinh"]
    # y["dateFirstAvailable"] = tmp["dateFirstAvailable"]
    # y["rate"] , y["totalRate"] , y["listReview"] = parseReviews(y["reviews"])
    # y["relateLaptops"] =  parserRelateLaptop(y["relateLaptops"])
    # y["bestSellersRank"] = tmp["bestSellersRank"]
    return (y["ID"], y)
sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
sc.setLogLevel("WARN")
ssc = StreamingContext(sc, 5)


kvs = KafkaUtils.createDirectStream(ssc, ["amazon-laptops"], {"metadata.broker.list": "kafka:9092"})

lines = kvs.map(parseData)


uniqueData = lines.reduceByKey(lambda a, b: a)
uniqueData.saveAsTextFiles("hdfs://namenode:9000/CrawlNha2/streamRDD.txt")
results = uniqueData.foreachRDD(writeRDD)


ssc.start()
ssc.awaitTermination()