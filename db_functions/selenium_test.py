# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 10:46:03 2012

@author: Shreejoy
"""
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
import selenium
import time 
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
import re
from urllib.request import urlopen
import json


def init_browser(targetReg, contrastReg, regionDict):
    browser = webdriver.Firefox()
    link = 'http://mouse.brain-map.org/'
    browser.get(link) # Load page
    elem = browser.find_element_by_xpath('//input[@id="_search_type_gene" and @value="differential"]')
    elem.click()
    
    change_region(browser, targetReg, 1, regionDict)
    change_region(browser, contrastReg, 2, regionDict)

#    slider = browser.find_element_by_xpath('//*[@id="_diff_search_slider"]')
#    slider.send_keys('0.0')
    searchButton = browser.find_element_by_xpath('//*[@id="_search_button"]')
    searchButton.click()
    
    sleep(3)
    return browser
        
def scrape_allen_pages(browser):
    refresh_page(browser)
    sleep(4)
    
    firstPageButton = browser.find_element_by_xpath('/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div/div/span/span/span')
    firstPageButton.click()    
    sleep(4)
    pageStatusElem = browser.find_elements_by_class_name("slick-pager-status")
    numPages = int(re.sub('of ', '', re.search('of \d+', pageStatusElem[0].text).group()))
    
    imageSeriesList = []
    fractList = []
    geneNameList = []
    for i in range(numPages):
        print("page " + str(i+1))
        exprFracts = browser.find_elements_by_class_name("slick-cell")
        for j in range(len(exprFracts)):
            if j % 9 == 1:
                try:
                    fractList.append(exprFracts[j].text)
                except (StaleElementReferenceException, IndexError):
                    print('exception in main loop')
                    print('j = ' + str(j))
                    exprFracts = browser.find_elements_by_class_name("slick-cell")
                    fractList.append('') 
                    continue
            elif j % 9 == 2:
                try:
                    imageSeriesList.append(exprFracts[j].text)
                except (StaleElementReferenceException, IndexError):
                    print('exception in main loop')
                    print('j = ' + str(j))
                    exprFracts = browser.find_elements_by_class_name("slick-cell")                    
                    imageSeriesList.append('')
                    continue
            elif j % 9 == 3:
                try:
                    geneNameList.append(exprFracts[j].text)
                except (StaleElementReferenceException, IndexError):
                    print('exception in main loop')
                    print('j = ' + str(j))
                    exprFracts = browser.find_elements_by_class_name("slick-cell")                    
                    geneNameList.append('')
                    continue
        nextPageElem = browser.find_element_by_xpath('/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div/div/span/span[3]/span')
        nextPageElem.click()
        nextPageElem = browser.find_elements_by_class_name("ui_icon_seek_next")
        sleep(4)
        successBool = False    
        cnt = 0
        while successBool == False and cnt < 5 :
            try:   
    #                print 'trying'
        #        print 'pre - try clause : ' + browser.find_elements_by_class_name("slick-cell")[3].text
        #        print browser.find_element_by_xpath('/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div[2]/div[3]/div/div[10]/div[3]/a').text
                WebDriverWait(browser, 20).until(lambda browser : browser.find_element_by_xpath('/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div[2]/div[3]/div/div[5]/div[3]/a').text.isdigit() )
    #                WebDriverWait(browser, 30).until(lambda browser : browser.find_element_by_xpath('/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div[2]/div[3]/div/div[10]/div[3]/a').text.isdigit() )            
                successBool = True        
    #                print 'try clause : ' + browser.find_elements_by_class_name("slick-cell")[3].text
            except (StaleElementReferenceException):
                print('stale ref')
                cnt = cnt + 1
                print('%s stale refs' % (cnt))
            except TimeoutException:
                print('time out exception, refreshing page') 
                cnt = cnt + 1
                refresh_page(browser)
                
    return fractList, imageSeriesList, geneNameList

def refresh_page(browser):
    browser.refresh()
    sleep(4)
    lightBulb = browser.find_element_by_xpath('/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div/div/span[2]/span[2]/span')
    lightBulb.click()    
    numLinks = browser.find_element_by_xpath('/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div/div/span[2]/span/a')
    numLinks.click()

def get_all_data(browser, targetReg, contrastReg, regionDict):
    change_region(browser, targetReg, 1, regionDict)
    change_region(browser, contrastReg, 2, regionDict)
    # get data in forward way    
    fractList, imageSeriesList, geneNameList = scrape_allen_pages(browser)
    
    # swap regions and get backward data
    swapButton = browser.find_element_by_xpath('//*[@id="_swap_button"]')
    swapButton.click()
    sleep(4)
    revFractList, revImageSeriesList, revGeneNameList = scrape_allen_pages(browser)
    newFractList = []
    for i in range(len(fractList)):
        if is_number(fractList[i]):
            newFractList.append(float(fractList[i]))
        else:
            newFractList.append(0.0)
    for i in range(len(revFractList)):
        if is_number(revFractList[i]):
            newFractList.append(1/float(revFractList[i]))
        else:
            newFractList.append(0.0)    
    newImageSeriesList = imageSeriesList
    newImageSeriesList.extend(revImageSeriesList)
    newGeneNameList = geneNameList
    newGeneNameList.extend(revGeneNameList)
    return newFractList, newImageSeriesList, newGeneNameList
    
def change_region(browser, regAbbrev, boxInd, regionDict):
    searchBox = browser.find_element_by_xpath('//*[@id="_search_domain_%d"]' % boxInd)
    searchBox.send_keys(regAbbrev)
    trashButton = browser.find_element_by_xpath('/html/body/div[%d]/div[3]/span[2]' %(boxInd+8))
    trashButton.click()
    sleep(1)
    regionInd = regionDict[regAbbrev]
    targetElem = browser.find_element_by_css_selector('#_ov_%d_%s' % ( (boxInd-1, regionInd)))
    sleep(1)
    targetElem.click()
    xButton = browser.find_element_by_xpath('/html/body/div[%d]/div[2]/span[2]' %(boxInd+8))
    xButton.click()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def load_region_dict():
    link = 'http://mouse.brain-map.org/ontology.json'
    handle = urlopen(link)
    data = handle.read()
    json_data = json.loads(data)
    regionDict = {k['acronym'] : k['structure_id'] for k in json_data}
    return regionDict
        
#
#imageSeriesList = []
#fractList = []
#geneNameList = []
#for i in range(numPages):
##    browser.implicitly_wait(20)
#    cnt = 0    
#    while cnt < 2:
#        try:
#            exprFracts = browser.find_elements_by_class_name("slick-cell")
#        except StaleElementReferenceExcpetion, e:
#            print 'blah'
#            cnt += 1
#    
##    print exprFracts[1].text
#    for j in range(len(exprFracts)):
#        if j % 9 == 1:
#            fractList.append(exprFracts[j].text)
#        elif j % 9 == 2:
#            imageSeriesList.append(exprFracts[j].text)
#        elif j % 9 == 3:
#            geneNameList.append(exprFracts[j].text)
#            print geneNameList[-1]
#    nextPageElem = browser.find_element_by_xpath('/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div/div/span/span[3]/span')
#    nextPageElem.click()
#    exprFracts = []
#    
#
#
##    broswer.manage().timeouts().implicitlyWait(60, TimeUnit.SECONDS)
##    WebDriverWait(browser, 6000, 500)
#    try:
#        WebDriverWait(browser, 60).until(lambda browser : browser.find_elements_by_class_name("slick-cell")[1].text != oldElem)
##        WebDriverWait(browser, 30).until(lambda browser : float(browser.find_elements_by_class_name("slick-cell")[1].text) < float(oldElem))
##        WebDriverWait(browser, 30).until(lambda browser : browser.find_elements_by_class_name("slick-cell")[1].text.isdigit())
##        currPage = int(re.sub(' of', '', re.search('\d+ of', pageStatusElem[0].text).group()))
##        WebDriverWait(browser, 60).until(lambda browser : browser.find_element_by_class_name("slick-cell"))
#        
#    finally: 
#        print i    
#
#    while browser.find_elements_by_class_name("slick-cell")[0].text.isdigit() == False:
#        WebDriverWait(browser, 10).until(lambda browser : browser.find_elements_by_class_name("slick-cell")[1].text != oldElem)
#        print browser.find_elements_by_class_name("slick-cell")[0].text.isdigit()
#    
#    try:
#        currPage = int(re.sub(' of', '', re.search('\d+ of', pageStatusElem[0].text).group()))
#        WebDriverWait(browser, 10).until(lambda browser : browser.find_elements_by_class_name("slick-cell")[0].text.isdigit())
#        
#    finally: 
#        print i
#
#
def wait_for_text_present(self, text, msg=None):
    msg = msg or " waiting for text %s to appear" % text
    assertion = lambda: self.selenium.is_text_present(text)
    self.spin_assert(msg, assertion)

def spin_assert(self, msg, assertion):
    for i in range(60):
        try:
            self.assertTrue(assertion())
            return
        except Exception as e:
            pass
        sleep(1)
    self.fail(msg)
#
#exprFracts = browser.find_elements_by_class_name("slick-cell")
#
#
#
#html body div.siteContent table.pageContent tbody tr td div#search_page_content table#search_block tbody tr td#result_cell div#result_block div#search_results_container.slickgrid_555003 div.slick-viewport div.grid-canvas div.ui-widget-content div.slick-cell
#
# html body div.siteContent table.pageContent tbody tr td div#search_page_content table#search_block tbody tr td#result_cell div#result_block div#pager_container div.slick-pager span.slick-pager-nav span.ui-state-default span.ui-icon'
#elem = browser.find_element_by_name("search_type_gene")
#//*[@id="_search_type_gene"]
#browser.execute('//*[@id="_search_type_gene"]')
#
#browser = selenium.selenium('localhost', 4444, '*firefox', 'http://mouse.brain-map.org/')
#
#browser.click('//input[@id="_search_type_gene" and @value="differential"]')
#
#elem = browser.find_element_by_xpath('//input[@id="_search_type_gene" and @value="differential"]')
#/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div[2]/div[3]/div/div[3]/div[2]
#
#elem = browser.find_element_by_xpath('/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div[2]/div[3]/div/div[0]/div[3]')
#/html/body/div/table/tbody/tr/td/div/table/tbody/tr/td/div/div[2]/div[3]/div/div[5]/div[2]
#html body div.siteContent table.pageContent tbody tr td div#search_page_content table#search_block tbody tr td#result_cell div#result_block div#search_results_container.slickgrid_555003 div.slick-viewport div.grid-canvas div.ui-widget-content div.slick-cell