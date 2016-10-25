#!/usr/bin/env python
# encoding=utf8
import sys
import time
import pymongo
from selenium import webdriver

reload(sys)
sys.setdefaultencoding('utf8')

class UserObject:
    def __init__(self):
        self.name = ""
        self.birth = ""
        self.jobList = []

    def parseJobList(self,jobList):

        jobs = jobList.split(",")
        for job in jobs:
            self.jobList.append(job)

    def setItem(self, name, birth, jobList):
        self.name = name
        self.birth = birth
        self.parseJobList(jobList)

    def getName(self):
        return self.name
    def getBirth(self):
        return self.birth
    def getJobList(self):
        return self.job
    def getJSONObject(self):
        obj = {"name":self.name, "birth":self.birth, "jobList":self.jobList}

        return obj


connection = None
db = None
collection = None

def connectDB():
    connection = pymongo.MongoClient("localhost", 27017)
    db = connection.people
    collection  = db.peopleList

def searchList(driver):

    resultList = []

    while 1:

        img_listarea = driver.find_element_by_css_selector('ul.img_listarea')

        for item in img_listarea.find_elements_by_css_selector('li'):

            userObj = UserObject()

            contents = item.find_element_by_css_selector('dl')
            title = contents.find_element_by_css_selector('dt')
            dds = contents.find_elements_by_css_selector('dd')

            nameEle = title.find_element_by_css_selector('a').get_attribute("innerHTML")
            birthEle = dds[0].find_element_by_css_selector('span').get_attribute("innerHTML")
            jobEle = dds[1].find_element_by_css_selector('span').get_attribute("innerHTML")

            name = nameEle.replace("<span>","").replace("</span>","")
            job = jobEle.replace("[現]","").replace("[前]","")

            print(name+","+birthEle+","+job)

            userObj.setItem(name,birthEle,job)
            collection.insert(userObj.getJSONObject())
            #resultList.append(userObj.getJSONObject())

        nextBtn = driver.find_element_by_css_selector('#pager > a.next')

        if nextBtn == None:
            break
        else:
            nextBtn.click()

keyItems = [u'가수',u'영화배우',u'국회의원',u'방송인']
driver = webdriver.Chrome('/Users/Elenore/Documents/Develop/PeopleCrawler/mac/chromedriver')  # Optional argument, if not specified will search path.

connectDB()

for key in keyItems :

    driver.get('http://people.joins.com');
    search_box = driver.find_element_by_css_selector('#sw')
    search_box.send_keys(key)
    search_btn = driver.find_element_by_css_selector("a.b_search")
    search_btn.click()
    time.sleep(1) # Let the user actually see something!

    searchList(driver)

driver.quit()
