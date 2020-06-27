import re
from urllib import request

url = 'https://kuyun.tv/vod/play/id/60334/sid/2/nid/1.html'

res = request.urlopen(url,timeout=10)
response = res.read().decode('utf-8')


with open('./test2.html','w',encoding='utf-8') as fp:
    fp.write(response)