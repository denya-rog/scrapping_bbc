import re
import json
import requests

from bs4 import BeautifulSoup
from bottle import route, request, run, template, response
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

chapter_b = "dd"
num_b = -1
"""
@route('/')
def index():
    global temperature
    temperature = request.query.chapter or temperature
    response.content_type = 'application/json'
    return json.dumps({"ppp":"dddd"})

    #return template('<b>Temperature: {{temperature}}</b>',  temperature=temperature)

"""
def translate_url(url, link):
    if link.startswith("http"):
        return link
    else:
        return url.format(link.lstrip("/"))



@route('/')
def index():
    #global chapter_b, num_b
    print(request.query.chapter)
    print(request.query.news)
    #print(request.query_string)
    chapter = request.query.chapter 
    num = request.query.news 
    if chapter==None or num==None:
        print("missing parameter")
        
    url = 'https://www.bbc.com/{}'

    ret_dict = dict()
    ret_dict["chapter"] = chapter

    response.content_type = 'application/json'
    r = requests.get(url.format(chapter))
    if r.status_code !=200:
        ret_dict["error"]= "Wrong  chapter. Check if chapter exists"
        return  json.dumps(ret_dict, indent=4)

    try:
        num = int(num)
        if num<1:
            ret_dict["error"]= "Wrong  number of news. Check parameters shold be like ?chapter=sport&news=5"
            return  json.dumps(ret_dict, indent=4)
    except: 
        ret_dict["error"]= "Insert not a number into number of news Check parameters shold be like ?chapter=sport&news=5 "
        return  json.dumps(ret_dict, indent=4)

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    driver.get(url.format(chapter))

    html = driver.page_source
    bso = BeautifulSoup(html, features="lxml")
    print(url.format(chapter))

    #catching navigation and footer links
    div = bso.findAll("div",class_=re.compile(".*?nav.*|.*?bbccom.*|.*?header.*"))
    div += bso.findAll('div', id=re.compile(".*?nav.*"))

    if div==[]:   
        ret_dict["error"]= "strange site"
        return  json.dumps(ret_dict, indent=4)            

    nav_links = []
    
    for di in list(set(div)):
        nav_links += di.findAll("a")

    nav_links = list(set(nav_links))
    objects = bso.findAll("a")
    news =  [{"title": i.getText().strip("\n").strip(" "), "url":translate_url(url,i["href"])  }  for i in objects if i not in nav_links and len(i.getText())>25]
    ret_dict["news"] = news[:num]
    return  json.dumps(ret_dict,  indent=4)


 


run(host='loclhost', port=9180)


