# -*- coding: utf-8 -*-
import urllib
import urllib2
import requests
import json
import codecs
import time
from datetime import datetime
import os
import re
import xlsxwriter
from xlsxwriter.workbook import Workbook
from bs4 import BeautifulSoup
from bs4 import Tag
import pdb
def getSourceFromPage(Page,wantToCache,count):
	if wantToCache:
		if not os.path.exists("cache"):
			os.makedirs("cache")
			
		if os.path.isfile('cache/' + (str(count)) + '.txt'):
			with open('cache/' + (str(count)) + '.txt', 'r') as f:
				Source = f.read()
				return Source

	hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'}
	request = urllib2.Request(Page, headers=hdr)
	try:
		time.sleep(1)
		response = urllib2.urlopen(request)
	except urllib2.HTTPError as err:
		if err.code == 404:
			Source = ""
			return Source
		else:
			time.sleep(2)
			response = urllib2.urlopen(request)

	Source = response.read().decode('utf-8', 'ignore')

	if wantToCache:
		with codecs.open('cache/' + (str(count)) + '.txt', 'w', encoding='utf-8') as f:
			f.write(Source)

	return Source

def format_filename(urlString):
	fileName  = urllib.quote_plus(urlString)
	if len(fileName.strip()) > 185:
		fileName = fileName[-185:]
	return cleanFolderName(fileName)

def cleanFolderName(folderNm):
	folderNm = re.sub('[^\w\-_\. ]', '', folderNm)
	return folderNm

def DurhamUniversity():
	
	workbook = xlsxwriter.Workbook('Durham University.xlsx')
	worksheet = workbook.add_worksheet()
	worksheet.write(0,0,"School English Name")
	worksheet.write(0,1,"Major Name")
	worksheet.write(0,2,"Course Type")
	worksheet.write(0,3,"Duration")
	worksheet.write(0,4,"Qualification")
	worksheet.write(0,5,"Major Website Link")
	schoolName=""
	majorName=""
	courseType=""
	duration=""
	qualification=""
	majorWebLink=""
	row=1
	CoursesList=[]
	source=(getSourceFromPage("https://www.dur.ac.uk/courses/all/#indexA",True,0))
	result_doc = BeautifulSoup(source, 'html5lib')
	CoursesLinks = (result_doc.find("div", {"id":"content"})).findAll('a')
	for CourseLink in CoursesLinks:
		courseLink = "https://www.dur.ac.uk" + CourseLink['href']
		if("/courses/info/?id=" in courseLink):
			CoursesList.append(courseLink)
	for x in range(0,len(CoursesList),1):
		source=(getSourceFromPage(CoursesList[x],True,x+1))
		result_doc = BeautifulSoup(source, 'html5lib')
		print(CoursesList[x])
		majorName= result_doc.find("span", {"class","span7 title"}).text.strip()
		courseType=result_doc.find("span", {"class","span4 entry"}).text.strip()
		if("Postgraduate Taught" in courseType):
			courseType= "Postgraduate Taught"
		elif("Undergraduate" in courseType):
			courseType = "Undergraduate"
		tr = ((result_doc.find("div", {"class","tab-content"})).find("div", {"class","row-fluid"})).findAll('tr')
		for td in tr:
			if("Degree" in td.find('th').text):
				qualification = td.find('td').text.strip()
				break
		for td in tr:
			if("Duration" in td.find('th').text):
				duration = td.find('td').text.strip()
				break
		for td in tr:
			try:
				if("Mode of study" in td.find('th').text):
					if(not("time" in duration)):
						duration = duration + (td.find('td').text.strip())
				break
			except:
				break
		#print(duration)
		#print(qualification)
		#print(courseType)
		majorName=majorName.replace(qualification,"").strip()
		#print(majorName)
		#exit()
		col=0
		row =x+1
		worksheet.write(row,col,"Durham University")
		worksheet.write(row,col+1,majorName)
		worksheet.write(row,col+2,courseType)
		worksheet.write(row,col+3,duration)
		worksheet.write(row,col+4,qualification)
		worksheet.write(row,col+5,CoursesList[x])
		row=row+1
	source=(getSourceFromPage("https://www.durhamisc.com/programmes",True,row))
	result_doc = BeautifulSoup(source, 'html5lib')
	CoursesList=[]
	CoursesLinks = (result_doc.find("li", {"id":"sharedlayout_0_durhamsharedheader_0_ctl03_firstLevelMenuRepeater_liTag_2"})).findAll('a')
	for CourseLink in CoursesLinks:
		CourseLink = "https://www.durhamisc.com" + CourseLink['href']
		counts = CourseLink.split('/')
		if(len(counts)>=6 or ("/programmes/english-language-preparation" in CourseLink)):
			CoursesList.append(CourseLink)
			print(CourseLink)               
	for x in range(0,len(CoursesList),1):
		source=(getSourceFromPage(CoursesList[x],True,row+1))
		result_doc = BeautifulSoup(source, 'html5lib')
		#print(CoursesList[x])
		majorName= result_doc.find("div", {"class","hero_content"}).text.strip()
		duration=result_doc.find("div", {"class","tab-content"}).text.strip().lstrip()
		duration = duration[duration.find("ength")+4:].lstrip().strip()
		duration=duration[duration.find(' ')+1:duration.find("Intakes")].strip().lstrip()
		#print(majorName)
		#print(duration)
		col=0
		worksheet.write(row,col,"Durham University")
		worksheet.write(row,col+1,majorName)
		worksheet.write(row,col+2,"Pathway programmes")
		worksheet.write(row,col+3,duration)
		worksheet.write(row,col+4,"")
		worksheet.write(row,col+5,CoursesList[x])
		row =row+1
	workbook.close()
DurhamUniversity()
print("...........DONE.............")
