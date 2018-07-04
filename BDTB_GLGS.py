__author__ = 'Snuggled'
# -*- coding = UTF-8 -*-
import urllib.request
import urllib.error
import re

class BDTB_GLGS:
	#初始化，传入各种参数
	def __init__(self):
		self.baseUrl = 'https://tieba.baidu.com/p/'  #基础地址
		self.default_title = '百度贴吧'
		self.page_index = 1  #将要读取的页数
		self.content_num = 1  #打印的楼层层数
		self.file = None  #将读取的内容写入文件

	#传入页码，获取该页帖子代码
	def getPage(self,question_num,see_lz=1,pn=1):
		try:
			url = self.baseUrl+str(question_num)+'?see_lz='+str(see_lz)+'&pn='+str(pn)
			request = urllib.request.Request(url)
			response = urllib.request.urlopen(request)
			return response.read().decode()
		except urllib.error.URLError as e:
			if hasattr(e,"reason"):
			    print('连接BDTB失败',e.reason)
			return None

	#获取到帖子的标题
	def getTitle(self,page_html):
		title_pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>',re.S)
		result = re.search(title_pattern,page_html)
		if result:
			return result.group(1)
		return None

	#获取帖子的总页数
	def getTotlePage(self,page_html):
		page_pattern = re.compile('回复贴，共.*?>(.*?)</span>',re.S)
		result = re.search(page_pattern,page_html)
		if result:
			return int(result.group(1))
		return None

    #从html代码中获取每层楼的内容
	def getContents(self,page_html):
		contents_pattern = re.compile('d_post_content j_d_post_content ">(.*?)</div>',re.S)
		result = re.finditer(contents_pattern,page_html)
		if result:
			str_contents = self.replace(result)
			return str_contents
		return None

    #替换掉无关的字符串
	def replace(self,result):
		str_contents = []
		for content in result:
			item = re.sub('<img.*?>|<br>',"\n",content.group(1))
			item = re.sub('<a href.*?>|</a>| {4,7}','',item)  #{4,7}前面有个空格
			str_contents.append(item.strip())
		return str_contents

    #打开txt文件
	def open_file(self,title):
		if title:
			self.file = open(title+'.txt','w+',encoding = 'utf-8')
		else:
			self.file = open(self.default_title+'.txt','w+',encoding = 'utf-8')

    #写入文件
	def write_file(self,str_contents):
		for str_content in str_contents:
			self.file.write("楼层:"+str(self.page_index)+'--------------------\n')
			self.file.write(str_content+'\n')
			self.page_index += 1

    #开始入口
	def start(self,question_num,see_lz):
		page_html = self.getPage(question_num,see_lz,self.page_index)
		page_title = self.getTitle(page_html)
		page_totle_num = self.getTotlePage(page_html)
		self.open_file(page_title)
		for i in range(page_totle_num):
			str_contents = self.getContents(page_html)
			self.write_file(str_contents)
			self.page_index += 1 
			page_html = self.getPage(question_num,see_lz,self.page_index)

if __name__ == "__main__":
    spider = BDTB_GLGS()
    spider.start(1599251208,1)