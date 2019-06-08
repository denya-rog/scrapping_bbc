import re
import json
import logging

import requests
from bs4 import BeautifulSoup
from bottle import route, request, run, template, response
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger("server_run")


def translate_url(url, link, chapter):
    """Returns  absolute link from abolute and relative links """
    if link.startswith("http"):
        return link
    elif link.startswith("//"):
        return "http:"+link
    elif link.startswith("/"):
        return url.strip('/') + link
    else:
        return url + chapter.strip('/') + '/' + link



@route('/')
def index():

    chapter = request.query.chapter 
    num = request.query.news 
    logger.info("Get params")
    if chapter==None or num==None:
        print("missing parameter")
        
    url = 'https://www.bbc.com/'

    ret_dict = dict()
    ret_dict["chapter"] = chapter

    response.content_type = 'application/json'

    r = requests.get(url + chapter)
    if r.status_code != 200:
        ret_dict["error"] = "Wrong  chapter. Check if chapter exists"
        logger.info("no response - wrong chapter - {}".format(url + chapter) )
        return  json.dumps(ret_dict, indent=4)

    try:
        num = int(num)
        if num<1:
            ret_dict["error"] = "Wrong  number of news. Check parameters shold be like ?chapter=sport&news=5"
            logger.info("number of news less then 1 .num = {}".format(str(num)) )
            return  json.dumps(ret_dict, indent=4)
    except: 
        ret_dict["error"] = "Insert not a number into number of news. Check parameters shold be like ?chapter=sport&news=5 "
        logger.info("number of news is not integer .num = {}".format(str(num)) )
        return  json.dumps(ret_dict, indent=4)

    options = Options()
    options.headless = True

    driver = webdriver.Firefox(options=options)
    driver.get(url + chapter)

    html = driver.page_source
    bso = BeautifulSoup(html, features="lxml")
    logger.info("make bs object from url {}".format(url + chapter))

    #catching navigation header and footer links in div
    div = bso.findAll("div",class_=re.compile(".*?nav.*|.*?bbccom.*|.*?header.*"))
    div += bso.findAll('div', id=re.compile(".*?nav.*"))

    if div==[]:   
        ret_dict["error"] = "strange site"
        logger.info("Site {} has no headers, nvigation bar and footers".format(url + chapter))
        return  json.dumps(ret_dict, indent=4)            

    nav_links = []
    
    for di in list(set(div)):
        nav_links += di.findAll("a")

    nav_links = list(set(nav_links))
    objects = bso.findAll("a")

    news =  [{"title": i.getText().strip("\n").strip(" "), 
              "url": translate_url(url, i["href"], chapter)  
             }  for i in objects if i not in nav_links and len(i.getText())>25]
    ret_dict["news"] = news[:num]
    logger.info("everything ok")
    return  json.dumps(ret_dict,  indent=4)


run(host='0.0.0.0', port=9180)


