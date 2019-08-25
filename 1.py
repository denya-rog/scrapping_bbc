import json
import time
import re
import logging
import requests

import asyncio
import aiohttp
from bs4 import BeautifulSoup



logging.basicConfig(level="DEBUG")
logger = logging.getLogger("server_run")

def translate_url(url, link, chapter):
    """Returns  absolute link from absolute or relative links """
    if link.startswith("http"):
        return link
    elif link.startswith("//"):
        return "http:"+link
    elif link.startswith("/"):
        return url.strip('/') + link
    else:
        return url + chapter.strip('/') + '/' + link

async def cl_socket(writer, ret_dict):
    writer.write(json.dumps(ret_dict, indent=4).encode())
    await writer.drain()
    writer.close()


async def handle_echo(reader, writer):

    ret_dict = dict()
    url = 'https://www.bbc.com/'

    data = await reader.read(100)
    message = data.decode()
    
    chapter = re.findall(r".*?chapter=(.*?)[&\s]",  message)
    num = re.findall(r".*?news=(.*?)[&\s]",message)

    if not (chapter and num):
        logger.info("Missing parameter")
        ret_dict["error"] = "missing parameter, \
                            should be like ?chapter=sport&news=5"
        await cl_socket(writer, ret_dict)
        return
    else: 
        chapter=chapter[0]
        num = num[0]

    print("\n",chapter,num, "\n")

    r = requests.get(url + chapter)
    if r.status_code != 200:
        print("Enter to requsting")
        logger.info("No response - wrong chapter - {}".format(url + chapter) )
        ret_dict["error"] = "Wrong  chapter. \
Check if chapter exists or site aviable"
        await cl_socket(writer, ret_dict)
        return

    time.sleep(5)
    try:
        num = int(num)
        if num<1:
            print("Enter to requsting")
            logger.info("Number of news less then 1 .num = {}".format(str(num)) )
            ret_dict["error"] = "Wrong  number of news. \
                                Check parameters should be like ?chapter=sport&news=5"
            await cl_socket(writer, ret_dict)
            return 
    except: 
        logger.info("Insert not a number .num = {}".format(str(num)) )
        ret_dict["error"] = "Insert not a number into number of news. s\
                            Check parameters should be like ?chapter=sport&news=5 "
        await cl_socket(writer, ret_dict)

        return 

    html = requests.get(url + chapter).text

    bso = BeautifulSoup(html, features="lxml")
    logger.info("Make bs object from url {}".format(url + chapter))

    #catching navigation header and footer links in div
    div = bso.findAll("div",class_=re.compile(".*?nav.*|.*?bbccom.*|.*?header.*"))
    div += bso.findAll('div', id=re.compile(".*?nav.*"))

    if div==[]:   
        
        logger.info(
                    "Site {} has no headers,\ navigation bar and footers"
                    .format(url + chapter)
                   )
        ret_dict["error"] = "strange site"
        await cl_socket(writer, ret_dict)
        return  

    nav_links = []
    
    for di in list(set(div)):
        nav_links += di.findAll("a")

    nav_links = list(set(nav_links))
    objects = bso.findAll("a")

    news = [{"title": i.getText().strip("\n").strip(" "), 
              "url": translate_url(url, i["href"], chapter)  
             }  for i in objects if i not in nav_links and len(i.getText())>25]
    ret_dict["news"] = news[:num]
    if len(news)<num:
        ret_dict["error"] = (
                             "Found and returns only {} links instead of {}"
                             .format(len(news), num)
                            )

        logger.info(
                    "Found and returns only {} links instead of {}"
                    .format(len(news), num)
                   )

    logger.info("everything ok")
    await cl_socket(writer, ret_dict)

    #return  


loop = asyncio.get_event_loop()
session = aiohttp.ClientSession()
coro = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)





# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
