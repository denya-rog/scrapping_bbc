import requests

host = "http://localhost/" 
request_pattern = host +"?chapter={}&news={}"

# check news parametr with correct chapter parameter
print("Check news parameter")

# check inserting float-like news parameter 
r = requests.get(request_pattern.format("sport", ".8"))
assert r.json()["error"]=="Insert not a number into number of news. Check parameters should be like ?chapter=sport&news=5 ", "don't return error, when converts from str(float) to int"
assert r.json()["news"]==[] , "try to search news, in case, when shouldn't, with news -not integer, (float)"
print("pass 1")

# check inserting string as news parameter
r = requests.get(request_pattern.format("sport", "d!"))
assert r.json()["error"]=="Insert not a number into number of news. Check parameters should be like ?chapter=sport&news=5 " , "don't return error, when converts from str to int"
assert r.json()["news"]==[] , "try to search news, in case, when shouldn't, with news -not integer, (string)"
print("pass 2")

# check inserting negativ news parameter
r = requests.get(request_pattern.format("sport", "-1"))
assert r.json()["error"]=="Wrong  number of news. Check parameters should be like ?chapter=sport&news=5" , "don't return error, when gets negative"
assert r.json()["news"]==[] , "try to search news, in case, when shouldn't, with news -negativ  integer"
print("pass 3")

# check inserting 0 as news parameter
r = requests.get(request_pattern.format("sport", "0"))
assert r.json()["error"]=="Wrong  number of news. Check parameters should be like ?chapter=sport&news=5" , "don't return error, when gets zero"
assert r.json()["news"]==[] , "try to search news, in case, when shouldn't, with number of news - zero"
print("pass 4")

# check inserting 1 as news parameter
r = requests.get(request_pattern.format("sport", "1"))
assert r.json()["error"]==None , "return error, when shouldn't"
assert len(r.json()["news"])==1, "found not required number of news"
print("pass 5")

# check inserting 2 as news parameter
r = requests.get(request_pattern.format("sport", "2"))
assert r.json()["error"]==None , "return error, when shouldn't"
assert len(r.json()["news"])==2, "found not required number of news"
print("pass 6")

# check inserting 5 as news parameter
r = requests.get(request_pattern.format("sport", "5"))
assert r.json()["error"]==None , "return error, when shouldn't"
assert len(r.json()["news"])==5, "found not required number of news"
print("pass 7")

# check inserting 1000000 as news parameter
r = requests.get(request_pattern.format("sport", "1000000"))
assert r.json()["error"]!=None , "don't return error, when should"
assert len(r.json()["news"])!=[], "don't found any link, when should"
print("pass 8")


# Check chapter parameter with valid news
print("Check chapter parameter")

# check valid chapter parameter
r = requests.get(request_pattern.format("sport", "1"))
assert r.json()["error"]==None , "return error, when shouldn't"
assert len(r.json()["news"])==1, "found not required number of news"
print("pass 9")

# check unvalid chapter parameter
r = requests.get(request_pattern.format("srt", "1"))
assert r.json()["error"]=="Wrong  chapter. Check if chapter exists or site aviable" , "returns wrong error"
assert r.json()["news"]==[], "try to search news, when shouldn't"
print("pass 10")


# Check number of parameters
print("Check number of parameters")

#check less parameters:
r = requests.get(host+"?news=1")
assert r.json()["error"]=="missing parameter, should be like ?chapter=sport&news=5" , "returns wrong error"
assert r.json()["news"]==[], "try to search news, when shouldn't"
print("pass 11.1")

r = requests.get(host+"?chapter=sport")
assert r.json()["error"]=="missing parameter, should be like ?chapter=sport&news=5" , "returns wrong error"
assert r.json()["news"]==[], "try to search news, when shouldn't"
print("pass 11.2")

#check more parameters
r = requests.get(host+"?chapter=sport&h=9&news=5")
assert r.json()["error"]==None , "returns error, when shouldn't"
assert len(r.json()["news"])==5, "found not required number of news"
print("pass 12")

print("All test are passed")
