__author__ = 'Snuggled'
# -*- coding = UTF-8 -*-
import urllib.request
import urllib.error
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from lxml import etree
import time
import re

#进入拉勾网搜索Python爬虫的岗位，爬取其信息
class LGW:
	#初始化，传入各种参数
	def __init__(self):
		self.baseUrl = 'https://www.lagou.com'
		self.default_title = '拉勾网职位——Python爬虫'
		self.search_job = 'Python爬虫'
		self.pageInIndex = 1
		self.file = None
		self.cookie = {
   			'Cookie':'_ga=GA1.2.1175147762.1530256071;'
   			 		 'user_trace_token=20180629150749-21cc0a80-7b6b-11e8-9775-5254005c3644;'
   			 		 'LGUID=20180629150749-21cc1060-7b6b-11e8-9775-5254005c3644;'
   			 		 'index_location_city=%E5%85%A8%E5%9B%BD;'
   			 		 'isCloseNotice=0;'
   			 		 'JSESSIONID=ABAAABAABEEAAJA8AD37579C59DFF7E6043CAC681B002D7;'
   			 		 'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1530256071,1530256073,1530258255,1530512898;'
   			 		 '_gid=GA1.2.1978856626.1530512899;'
   			 		 'TG-TRACK-CODE=search_code;'
   			 		 'LGRID=20180702153537-83387d3e-7dca-11e8-98e2-5254005c3644;'
   			 		 'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1530516937;'
   			 		 'SEARCH_ID=ceda1f41aee2407984ece245a4566642'
             }
		self.headers = {
    		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/67.0.3396.99 Safari/537.36',
    		'Accept':'application/json, text/javascript, */*; q=0.01',
    		'Host':'www.lagou.com',
    		'Origin':'https://www.lagou.com',
    		'Referer':'https://www.lagou.com/jobs/list_python%E7%88%AC%E8%99%AB?labelWords=sug&fromSearch=true&suginput=p',
		}
		self.data = {
		    'first': False,
		    'pn':1,
		    'kd': self.search_job,
		}

	def autoSele(self,baseUrl,search_job):
		# 加启动配置
		option = webdriver.ChromeOptions()
		option.add_argument('disable-infobars')
		# 启动浏览器
		browser = webdriver.Chrome(chrome_options=option)
		#最大化窗口
		browser.maximize_window()
		#也可以设置浏览器的宽高browser.set_window_size(400,800)
		browser.get(baseUrl)
		time.sleep(3)
		close = browser.find_element_by_id("cboxClose").click()
		time.sleep(3)
		elem = browser.find_element_by_id("search_input")
		elem.clear()
		elem.send_keys(search_job)
		browser.find_element_by_id("search_button").click()
		time.sleep(3)
		print('From this url crawl:',browser.current_url)
		for x in range(1,31):
			self.data['pn'] = x
			allInfo = self.getContent(self.cookie,self.headers,self.data)
			print('提取页数：',x)
			self.write_file(allInfo)
		print('获取完毕！')
		browser.close()

	def getContent(self,cookie,headers,data):
		url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
		page = requests.post(url=url, cookies=cookie, headers=headers, data=data)
		page.encoding = 'utf-8'
		result = page.json()
		jobs = result['content']['positionResult']['result']
		allInfo = []
		for job in jobs:
			time.sleep(3)
			information = {
				'companyShortName' : job['companyShortName'],  #公司简称
				'city' : job['city'],  #公司所在城市
				'companyFullName' : job['companyFullName'],  #公司全名
				'companyLabelList' : job['companyLabelList'],  #公司福利1
				'companyLogo' : job['companyLogo'],  #公司logo链接
				'companySize' : job['companySize'],  #公司规模
				'createTime' : job['createTime'],  #发布时间
				'district' : job['district'],  #城市区名
				'firstType' : job['firstType'],  #职位大类
				'industryField' : job['industryField'],  #公司类型
				'isSchoolJob' : job['isSchoolJob'],  #是否为校园职位
				'jobNature' : job['jobNature'],  #全职or兼职
				'positionAdvantage' : job['positionAdvantage'],  #公司福利2
				'positionId' : job['positionId'],  #公司代号
				'positionName' : job['positionName'],  #职位名称
				'salary' : job['salary'],  #薪资
				'secondType' : job['secondType'],  #具体工作类型
				'stationname' : job['stationname'],  #公司区域名称
				'workYear' : job['workYear'],  #工作经验
				'longitude' : job['longitude'], #经度
				'latitude' : job['latitude'],  #维度
			}

			detail_url = 'https://www.lagou.com/jobs/{}.html'.format(job['positionId'])
			response = requests.get(url=detail_url, headers=headers, cookies=cookie)
			response.encoding = 'utf-8'
			tree = etree.HTML(response.text)
			desc = tree.xpath('//dl[@id="job_detail"]/dd[2]/div/p/text()')  #职位描述
			desc = self.replace(desc)
			posi = tree.xpath('//dl[@id="job_detail"]/dd[3]/input[@name="positionAddress"]/@value')  #具体地点
			resumeHandle = tree.xpath('//div[@class="publisher_data"]/div[2]/span[1]/text()') + tree.xpath('//div[@class="publisher_data"]/div[2]/span[3]/text()')
			activeTime = tree.xpath('//div[@class="publisher_data"]/div[3]/span[1]/text()') + tree.xpath('//div[@class="publisher_data"]/div[3]/span[3]/text()')
			information['desc'] = desc
			information['posi'] = posi
			information['resumeHandle'] = resumeHandle
			information['activeTime'] = activeTime
			allInfo.append(information)
		return allInfo

	#替换掉无关的字符串
	def replace(self,result):
		str_contents = []
		for cont in result:
			item = re.sub(r'\xa0','',cont) 
			str_contents.append(item.strip())
		return str_contents

	#打开txt文件
	def open_file(self,title):
		self.file = open(title+'.txt','w+',encoding = 'utf-8')

    #写入文件
	def write_file(self,allInfo):
		for info in allInfo:
			self.file.write("Page:"+str(self.pageInIndex)+'--------------------\n')
			self.file.write(str(info)+'\n')
			self.pageInIndex += 1

	def start(self):
		#分析一波：进入官网，用selenium自动控制搜索self.search_job会出现30页每页15个招聘职位
		#然后对这450个数据进行详细爬取（进入每一个职位的内部详细页面）
		#(1)selenium控制功能----autoSele(不需要返回值)
		#(2)获取每一个内部页面的[职位名称][薪资][有无经验][学历要求]
		#[全职or兼职][职位诱惑][职位描述][具体地点][发布者的简历处理速度][发布者的活跃时段]
		#[招聘公司名称、领域、发展阶段、规模及公司主页][招聘公司logo]----getContent
		#(3)对每一个招聘岗位建立单独的文件夹
		#里面存有一个txt及公司logo，文件名为公司名称+领域----write_File
		#(4)对之后页数的自动翻页及继续爬取
		self.open_file(self.default_title)
		self.autoSele(self.baseUrl,self.search_job)

if __name__ == "__main__":
    spider = LGW()
    spider.start()