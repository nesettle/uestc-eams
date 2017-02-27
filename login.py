# -*- coding:UTF-8 -*-

import requests
import re

print(">>>登录信息门户<<<")
username=input("输入学号：")
password=input("输入密码：")

init="http://idas.uestc.edu.cn/authserver/login?service=http%3A%2F%2Fportal.uestc.edu.cn%2F"
url="http://eams.uestc.edu.cn/eams/teach/grade/course/person!search.action?semesterId=123&projectType="
# 可以用登录信息在同一个session内访问任何信息门户or教务处url
headers={
    "Host":"idas.uestc.edu.cn",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    "Referer":"http://idas.uestc.edu.cn/authserver/login?service=http%3A%2F%2Fportal.uestc.edu.cn%2F"
}
u=requests.session()
u.cookies.clear()
r=u.get(init,headers=headers)
lt=re.findall('name="lt" value="(.*)"/>',r.text)[0]
data={
    "username":username,
    "password":password,
    "lt":lt,
    "dllt":"userNamePasswordLogin",
    "execution":"e1s1",
    "_eventId":"submit",
    "rmShown":"1"
}
r=u.post(init,headers=headers,data=data)
#cookies=r.cookies
#同一session内无需cookie
if ("电子科技大学登录" in r.text):
    print (">>>用户名密码不匹配<<<")
    exit()
else:
    print(">>>登录成功<<<")

r=u.get(url,headers=headers)
print (r.text)
