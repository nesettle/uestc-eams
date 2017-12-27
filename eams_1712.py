############## ! CONFIG PART ! ##############
user_username = '2016xxxxxx'
user_password = 'p4ssw0rd'
nthread       = 1 # 预选请使用1
port          = [1295]
lesson        = [332444]
name          = ['营养与健康']
#############################################

__author__ = 'Cyrus'

import requests
import re
import sys
import time
import queue
import threading

init = "http://idas.uestc.edu.cn/authserver/login?service=http%3A%2F%2Fportal.uestc.edu.cn%2F"
init_eams = "http://eams.uestc.edu.cn/eams/home!index.action"
url_lesson = 'http://eams.uestc.edu.cn/eams/electionLessonInfo.action?lesson.id='
url_scan_lesson = "http://eams.uestc.edu.cn/eams/stdElectCourse!data.action?profileId="
url_scan_entrance = "http://eams.uestc.edu.cn/eams/stdElectCourse!defaultPage.action?electionProfile.id="
url_catch = "http://eams.uestc.edu.cn/eams/stdElectCourse!batchOperator.action?profileId="
url_table = "http://eams.uestc.edu.cn/eams/courseTableForStd.action?_=0&semester.id="  # 163, 17-18, t1
url_test_estimate = "http://eams.uestc.edu.cn/eams/textEvaluateStudent!search.action?semester.id="  # 163, 17-18, t1


def get_mid_text(text, left_text, right_text, start=0):
	#	获取中间文本
	left = text.find(left_text, start)
	if left == -1:
		return ('', -1)
	left += len(left_text)
	right = text.find(right_text, left)
	if right == -1:
		return ('', -1)
	return (text[left:right], right)


def safe_get(session, req):
	#	包括报错的安全get请求
	flag = 1
	while flag > 0:
		if flag > 32:
			print("错误：这他妈网络太差了")
			return ""
		try:
			res = session.get(req).text
		except:
			print("警告：你的网炸了")
			flag += 1
		else:
			flag = 0
	return res


def safe_post(session, req, data):
	#	包括报错的安全post请求
	flag = 1
	while flag > 0:
		if flag > 32:
			print("错误：这他妈网络太差了")
			return ""
		try:
			res = session.post(req, data=data).text
		except:
			print("警告：你的网炸了")
			flag += 1
		else:
			flag = 0
	return res


def login(username, password):
	headers = {
		"Host": "idas.uestc.edu.cn",
		"User-Agent": "CYRUS/5.0 (Windows CNSS; WOW64; rv:51.0) CNSS/20100101 CYRUS/51.0",
		"Referer": "http://idas.uestc.edu.cn/authserver/login?service=http%3A%2F%2Fportal.uestc.edu.cn%2F"
	}
	u = requests.session()
	u.cookies.clear()
	r = u.get(init, headers=headers)
	lt = re.findall('name="lt" value="(.*)"/>', r.text)[0]
	data = {
		"username": username,
		"password": password,
		"lt": lt,
		"dllt": "userNamePasswordLogin",
		"execution": "e1s1",
		"_eventId": "submit",
		"rmShown": "1"
	}
	r = u.post(init, headers=headers, data=data)

	if ("电子科技大学登录" in r.text):
		print("提示：登录失败")
		print("提示：系统已退出")
		sys.exit()
	else:
		print("提示：用户[%s]登录成功"%username)
		s = u.get(init_eams).text
		if s.partition("重复登录")[1]!="":
			url_t = get_mid_text(s,"请<a href=\"","\">点击此处")
			u.get(url_t[0])
			s = u.get(init_eams).text
			if s.partition("重复登录")[1]!="":
				print("提示：eams提示了重复登录，并处理失败")
			else:
				print("提示：eams提示了重复登录，但是处理成功")
		return u


def scan(url, minx, maxx, wrongword, out):
	#	url			模板链接
	#	minx  		起始值（包含）
	#	maxx		终止值（包含）
	#	wrongword	错误关键字（list）
	#	out			[=1]为需要临时输出
	res = []
	for i in range(minx, maxx + 1):
		req = url + str(i)
		s = safe_get(session, req)
		flag = 1
		for key in wrongword:
			if s.find(key) != -1:
				print("扫描：%-5d-失败" % i)
				flag = 0
				break
		if flag:
			print("扫描：%-5d-成功" % i)
			res.append(i)
			if out == 1:
				print(s)
	return res


def find(x, fl, local=0, out=1, more=[]):
	if x == 88888888:
		for line in open(fl):
			req = url_lesson + line[0:6]
			s = safe_get(session, req)
			res = [line[0:6]]
			res.append(s.partition("课程序号:")[2].partition("\"> ")[2].partition("<")[0])
			res.append(s.partition("课程名称:")[2].partition("\"> ")[2].partition("<")[0])
			res.append(s.partition("课程类别:")[2].partition("\">")[2].partition("<")[0])
			res.append(s.partition("校区:")[2].partition("\">")[2].partition("<")[0])
			res.append(s.partition("教师:")[2].partition("\">")[2].partition("<")[0])
			res.append(s.partition("实际人数:")[2].partition("\">")[2].partition("<")[0])
			res.append(s.partition("人数上限:")[2].partition("\">")[2].partition("<")[0])
			print(res)
		return []
	if local != 0:
		print("Local processing: %s" % x)
		for line in open("all_class_171801.txt"):
			if line.partition(x)[1] != "":
				req = url_lesson + line[2:8]
				s = safe_get(session, req)
				res = [line[2:8]]
				res.append(s.partition("课程序号:")[2].partition("\"> ")[2].partition("<")[0])
				res.append(s.partition("课程名称:")[2].partition("\"> ")[2].partition("<")[0])
				res.append(s.partition("课程类别:")[2].partition("\">")[2].partition("<")[0])
				res.append(s.partition("校区:")[2].partition("\">")[2].partition("<")[0])
				res.append(s.partition("教师:")[2].partition("\">")[2].partition("<")[0])
				res.append(s.partition("实际人数:")[2].partition("\">")[2].partition("<")[0])
				res.append(s.partition("人数上限:")[2].partition("\">")[2].partition("<")[0])
				for i in more:
					res.append(s.partition(i)[2].partition("\">")[2].partition("<")[0])
				print(res)
				return res
	print("Processing: %s" % x)
	for line in open(fl):
		req = url_lesson + line[0:6]
		s = safe_get(session, req)
		res = s.partition("课程序号:")[2].partition("content\"> ")[2].partition("<")[0]
		if res.partition(x)[1] != "":
			print("扫描：%s-%s-成功" % (line[0:6], res))
			res = [line[0:6]]
			res.append(s.partition("课程序号:")[2].partition("\"> ")[2].partition("<")[0])
			res.append(s.partition("课程名称:")[2].partition("\"> ")[2].partition("<")[0])
			res.append(s.partition("课程类别:")[2].partition("\">")[2].partition("<")[0])
			res.append(s.partition("校区:")[2].partition("\">")[2].partition("<")[0])
			res.append(s.partition("教师:")[2].partition("\">")[2].partition("<")[0])
			for i in more:
				res.append(s.partition(i)[2].partition("\">")[2].partition("<")[0])
			if out == 0:
				print(res)
			return res
		else:
			if out != 0:
				print("扫描：%s-%s-失败" % (line[0:6], res))


def biu(session, port, class_info, name, choose=True, sleep=0):
	'''选课系统'''
	global count
	global t
	global m
	global success
	while success[t % m] == 0:
		
		'''抢课'''
		postdata = {'operator0': '%s:%s:0' % (str(class_info), str(choose).lower())}
		pre0 = safe_get(session, url_scan_entrance + str(port))
		response = safe_post(session, url_catch + str(port), postdata)
		
		info, end = get_mid_text(response, 'text-align:left;margin:auto;">', '</br>')
		if end == -1:
			info += '网络错误！'
		info = info.replace(' ', '').replace('\n', '').replace('\t', '')
		info += '  id:%s  port:%s' % (class_info, port)
		count += 1
		print(name + '正在进行第%d次尝试' % (count,))
		print(info)
		if '成功' in info:
			print("%s选课完成" % name)
			success[t % m] = 1
			global success_int
			success_int += 1
			break
		elif '本批次' in info or '只开放给' in info:
			print("emmmm...真的选不了")
			break
		elif '网络错误' in info:
			print('jesession已经过期 正在获取jesession')
			while True:
				try:
					response = safe_get(session, url_catch + str(port))
				except Exception:
					print('获取获取jesession失败：网络错误！')
					continue
				if '(possibly due to' not in response:
					print('获取获取jesession成功')
					break
				else:
					print('获取获取jesession失败：傻逼你电抽风了！')
		time.sleep(sleep)
		

def biubiu(session, port, class_info, name, choose=True, sleep=0):
	'''选课系统'''
	global count
	global t
	global m
	global success
	while success[t % m] == 0:
		'''选课'''
		postdata = {
			'operator0': '%s:%s:0' % (str(class_info), str(choose).lower()),
			'virtualCashCost%s' % (str(class_info)):0
		}
		pre0 = safe_get(session, url_scan_entrance + str(port))
		response = safe_post(session, url_catch + str(port), postdata)
				
		info, end = get_mid_text(response, 'text-align:left;margin:auto;">', '</br>')
		if end == -1:
			info += '网络错误！'
		info = info.replace(' ', '').replace('\n', '').replace('\t', '')
		info += '  id:%s  port:%s' % (class_info, port)
		count += 1
		print(name + '正在进行第%d次预选' % (count,))
		print(info)
		if '成功' in info:
			print("%s预选完成" % name)
			success[t % m] = 1
			global success_int
			success_int += 1
			break
		elif '本批次' in info or '只开放给' in info:
			print("emmmm...真的选不了")
			break
		elif '网络错误' in info:
			print('jesession已经过期 正在获取jesession')
			while True:
				try:
					response = safe_get(session, url_catch + str(port))
				except Exception:
					print('获取获取jesession失败：网络错误！')
					continue
				if '(possibly due to' not in response:
					print('获取获取jesession成功')
					break
				else:
					print('获取获取jesession失败：傻逼你电抽风了！')
		time.sleep(sleep)



def allclass(s):
	res = []
	while s.partition("class=\"griddata")[1] != "":
		s = s.partition("class=\"griddata")[2]
		x = get_mid_text(s, "<td>", "</td>")[0]
		res.append(x)
	return res


print("初始化系统中...")
try:
	session = login(user_username, user_password)
except:
	print("提示：系统已退出")
	sys.exit()
count = 0
success_int = 0

#查找入口
#entrance = scan(url_scan_entrance, 1000, 2000, ["没有开放的选课轮次", "不在选课时间内"], 0)
#print(entrance)

#查找课程
#lesson = find("C1600930.06","status_171801.txt")
#print(lesson)

#打印所有结果（关平台可用）
#find(88888888)

m = len(lesson)
success = []
for i in range(m):
	success.append(0)

free = queue.LifoQueue(nthread)
for t in range(nthread):
	if success_int == m:
		print("所有课程已完成")
		sys.exit()
	free.put("thread" + str(t))
	if success[t % m] == 0:
		th = threading.Thread(target=biubiu, args=(session, port[t % m], lesson[t % m], name[t % m]))
		th.start()
