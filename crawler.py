#!/usr/bin/env python
# encoding=utf8
import sys
import os
import time
import pymongo
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException

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


connection = pymongo.MongoClient("localhost", 27017)
db = connection.people
collection = db.peopleList

def checkDuplicatedItem(connection, userObj):

    result = collection.find({"name":userObj.getName(), "birth":userObj.getBirth()})

    if result.count() > 0 :
        return True

    return False

def parsePerPage(driver):

    try:

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

            if checkDuplicatedItem(connection, userObj) == False :
                collection.insert(userObj.getJSONObject())
            #resultList.append(userObj.getJSONObject())

    except StaleElementReferenceException:
        time.sleep(3)
        parsePerPage(driver)

def searchList(driver):

    resultList = []

    while 1:

        parsePerPage(driver)

        try:
            nextBtn = driver.find_element_by_css_selector('#pager > a.next')
            nextBtn.click()

        except NoSuchElementException:
            break


keyItems = [u'탤런트',u'가수',u'영화배우',u'국회의원',u'방송인']
#keyItems = [u'탤런트']
chromedriver = "/usr/lib/chromium-browser/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)

for key in keyItems :

    driver.get('http://people.joins.com');
    search_box = driver.find_element_by_css_selector('#sw')
    search_box.send_keys(key)
    search_btn = driver.find_element_by_css_selector("a.b_search")
    search_btn.click()
    time.sleep(1) # Let the user actually see something!

    searchList(driver)

driver.quit()
