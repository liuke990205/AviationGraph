from tqdm import tqdm
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
import numpy as np
'''
df = pd.read_excel("D:\城市名单 _只有铁岭后3.xlsx", usecols=[0],names=None)  # 读取项目名称列,不要列名
df_li = df.values.tolist()
result = []
for s_li in df_li:
    result.append(s_li[0])
print(result)
'''
result = ["朔州"]
name,level,hot,address,num=[],[],[],[],[]
def get_one_page(key,page):
   try:
   #打开浏览器窗口
      option_chrome = webdriver.ChromeOptions()
      option_chrome.add_argument('--headless')

      driver = webdriver.Chrome(chrome_options=option_chrome)
      time.sleep(1)

      url = "http://piao.qunar.com/ticket/list.htm?keyword="+str(key)+"&region=&from=mpl_search_suggest&page="+str(page)
      driver.get(url)
      infor = driver.find_elements_by_class_name("sight_item")
      for i in range(len(infor)):
         #获取景点名字
         name.append(infor[i].find_element_by_class_name("name").text)
         #获取景点评级
         try:
            level.append(infor[i].find_element_by_class_name("level").text)
         except:
            level.append("")
         #获取景点热度
         hot.append(infor[i].find_element_by_class_name("product_star_level").text[3:])
         #获取景点地址
         address.append(infor[i].find_element_by_class_name("area").text)
         #获取景点销量
         try:
            num.append(infor[i].find_element_by_class_name("hot_num").text)
         except:
            num.append(0)

      driver.quit()
      return
   except TimeoutException or WebDriverException:
      return get_one_page()
n = 0
for key in tqdm(result):
   print ("正在爬取{}".format(key))
   # 取前13页
   n = n + 1
   for page in range(1,14):
      print ("正在爬取第{}页".format(page))
      get_one_page(key,page)
      if n % 2 ==0:
         sight = {'name': name, 'level': level, 'hot': hot, 'address': address, 'num':num}
         sight = pd.DataFrame(sight, columns=['name', 'level', 'hot', 'address', 'num'])
         sight.to_csv("sight5.csv",mode='a', header=False,encoding="utf_8_sig")
sight = {'name': name, 'level': level, 'hot': hot, 'address': address, 'num':num}
sight = pd.DataFrame(sight, columns=['name', 'level', 'hot', 'address', 'num'])
sight.to_csv("sight5.csv",mode='a', header=False,encoding="utf_8_sig")