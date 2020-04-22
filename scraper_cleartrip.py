# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 11:32:21 2020

@author: debayan.bose
"""
import csv
import selenium.webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
#from multiprocessing.pool import ThreadPool, Pool
#import threading
from selenium import webdriver
#from multiprocessing import Process
#import multiprocessing
import time
import warnings
import datetime
from dateutil.rrule import rrule, DAILY
#import config
import pandas as pd
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from pymongo import MongoClient 
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

def get_driver():
#    options = webdriver.ChromeOptions()    
#    options.add_argument("--headless")
#    options.add_argument("window-size=1920,1080")
#    options.add_argument("start-maximised")
#    options.add_argument("--use-fake-ui-for-media-stream")
#    options.add_argument("--disable-user-media-security=true")
#    options.add_argument('--no-proxy-server') 
#    capabilities = DesiredCapabilities.CHROME.copy()
#    capabilities['acceptSslCerts'] = True 
#    capabilities['acceptInsecureCerts'] = True
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, executable_path=r'C:/D Backup/geckodriver.exe')

    #driver = selenium.webdriver.Chrome(executable_path='C:/Users/debayan.bose/Downloads/chromedriver_win32/chromedriver.exe',chrome_options=options,desired_capabilities=capabilities)
    #driver = selenium.webdriver.Chrome()
    return driver

def find_all(a_str, sub):
            start = 0
            while True:
                start = a_str.find(sub, start)
                if start == -1: return
                yield start
                start += len(sub) # use start += 1 to find overlapping matches


def scrape_cleartrip(url,depdate):
        #div[@title='Create Page']   
        depdate = str(datetime.datetime.strptime(depdate, "%m/%d/%Y").date().strftime('%d/%m/%Y'))
        driver=get_driver()
        try:
            driver.get(url)
            time.sleep(10)
        except:
            print('invalid URL')
            return None
        try:
            element = driver.find_element_by_link_text("All flights")
            element.click()
        except:
            try:
                driver.close()
                driver.quit()
                driver=get_driver()
                driver.get(url)
                time.sleep(10)
                element = driver.find_element_by_link_text("All flights")
                element.click()
            except:
                print('Page not loaded')
                return None
        # URL requested in browser.
        try:
            for i in range(50): # adjust integer value for need
               # you can change right side number for scroll convenience or destination 
               driver.execute_script("window.scrollBy(0, 500)")
               # you can change time integer to float or remove
               #time.sleep(0.5)
        except:
            try:
                
                driver.close()
                driver.quit()
                driver=get_driver()
                driver.get(url)
                time.sleep(10)
                element = driver.find_element_by_link_text("All flights")
                element.click()
                for i in range(50): # adjust integer value for need
                   # you can change right side number for scroll convenience or destination 
                   driver.execute_script("window.scrollBy(0, 500)")
                   # you can change time integer to float or remove
                   #time.sleep(0.5)
            except:
                print('Page crashed')
                return None
        
        body = driver.page_source
        soup = BeautifulSoup(body, "lxml")
        #fil = open("out_clear_headless.txt", "w", encoding='utf-8')
        #fil.write(str(soup))
        print(url)
        temp1 = soup.find_all('title', attrs={'dir': 'rtl'})[0].text
        temp1 = temp1.replace('Cleartrip | ','')
        origin = temp1.split(' → ')[0]
        destination = temp1.split(' → ')[1]
        dt_format = str(datetime.datetime.strptime(depdate, "%d/%m/%Y").date().strftime('%d%m%Y'))
        flight_detail = soup.find_all('tbody', attrs={'class': 'segment'})
        flightData = []
        for j in range(len(flight_detail)):
            try:
                
                data = str(flight_detail[j])
                
                flight_name = flight_detail[j].find('th', attrs={'class': "vendor count1"}).text #flight name
                flight_name = flight_name.replace('\n','')
                flight_name = flight_name.replace(' ','')
                deptime = flight_detail[j].find('th', attrs={'class': "depart"}).text #departure time
                arrtime = flight_detail[j].find('th', attrs={'class': "arrive"}).text #departure time
                duration = flight_detail[j].find('th', attrs={'class': "duration"}).text #departure time
                stops = flight_detail[j].find('td', attrs={'class': "duration"}).text #stops
                
                if stops == 'non-stop':
                    end_flt_position = list(find_all(data,'_'+dt_format))[0]
                    st_flt_position = list(find_all(data,'data-fk="'))[0]
                    temp_new = data[st_flt_position:end_flt_position]
                    temp_new = temp_new.replace('AIR_ASIA','')
                    flight_number = temp_new.split('_')[1]
                else:
                    end_flt_position1 = list(find_all(data,'_'+dt_format))[0]
                    st_flt_position1 = list(find_all(data,'data-fk="'))[0]
                    temp_new1 = data[st_flt_position1:end_flt_position1]
                    temp_new1 = temp_new1.replace('AIR_ASIA','')
                    flight_number1 = temp_new1.split('_')[1]
                    
                    end_flt_position2 = list(find_all(data,'_E'))[1]
                    st_flt_position2 = list(find_all(data,'$$'))[0]
                    temp_new2 = data[st_flt_position2:end_flt_position2]
                    temp_new2 = temp_new2.replace('AIR_ASIA','')
                    flight_number2 = temp_new2.split('_')[1]
                    if flight_number1 == flight_number2:
                        flight_number = flight_number1
                    else:
                        flight_number = flight_number1 +'/' + flight_number2
                price = flight_detail[j].find('th', attrs={'class': "price"}).text #departure time
                price = price.replace('\n','')
                price = price.replace('Rs.','')
                price = price.replace(',','')
                price = price.replace(' ','')
                flightData.append([depdate, flight_name,flight_number,deptime,origin,duration,arrtime,destination,price,stops])    
            except:
                continue
        flightData = pd.DataFrame(flightData)
        print("no records inserted ",len(flightData), 'for:   ',url)
        driver.close()
        driver.quit()
        return flightData

def scrapenew_cleartrip(origin,destin,fromdate,todate,job_time, passengers, stops):
    a = datetime.datetime.strptime(fromdate, "%d/%m/%Y").date()
    b = datetime.datetime.strptime(todate, "%d/%m/%Y").date()
    trDate = list()
    for dt in rrule(DAILY, dtstart=a, until=b):
        dept_date = str(dt.strftime("%m/%d/%Y"))
        trDate.append(dept_date)
    all_urls = list()  
    for j in range(len(trDate)):
        #url = 'https://www.cleartrip.com/flights/results?from=DEL&to=BLR&depart_date=09/01/2020&adults=1&childs=0&infants=0&class=Economy&airline=&carrier=&intl=n&page=loaded'
        url = 'https://www.cleartrip.com/flights/results?from='
        url = url + origin + '&to=' + destin
        dt_format = str(datetime.datetime.strptime(trDate[j], "%m/%d/%Y").date().strftime('%d/%m/%Y'))
        url = url + '&depart_date=' +dt_format
        
        passengers = 'A-1_C-0_I-0'
        adults = passengers[2]
        children = passengers[6]
        infants = passengers[10]
        url = url + '&adults=' + adults + '&childs=' + children + '&infants' + infants + '&class=Economy&airline=&carrier=&intl=n&page=loaded'
        all_urls.append(url)
        
    data=list()
    for urls in range(len(all_urls)):
        temp1 = scrape_cleartrip(all_urls[urls],trDate[urls])
        if not (temp1 is None):
            data.append(temp1)
    if len(data) == 0:
        return 0
    df = pd.concat(data)
    df.columns = ['DepartureDate','FlightName', 'FlightCode', 'DepTime','DepCity','FlightDuration','ArrivalTime','ArrivalCity','fare','stops']
#    for i in range(len(data)):
#        for j in range(len(data[i])):
#            df = df.append(pd.Series(data[i][j],index = ['DepartureDate','FlightName', 'FlightCode', 'DepTime','DepCity','FlightDuration','ArrivalTime','ArrivalCity','fare','stops']),ignore_index=True)
#   
                 
    df['fare'] = [w.replace('₹ ', '') for w in df['fare']]
    df['fare'] = [w.replace(',', '') for w in df['fare']]
    df['fare']= np.array(df['fare'],float)
    df['sector']= origin +'_'+destin
    df['ArrivalTime'] = [w[0:5] for w in df['ArrivalTime']]
    df['job_time'] = job_time
    
    df['NSTOP'] = df['stops']
    for j in range(len(df)):
        if df['stops'].iloc[j] == 'non-stop':
            df['NSTOP'].iloc[j] = '0'
    df['NSTOP'] = [w.replace('stop','') for w in df['NSTOP']]
    df['NSTOP'] = [w.replace('s','') for w in df['NSTOP']]
    
    df['NSTOP'] = [w.replace(' ','') for w in df['NSTOP']]
    df['NSTOP'] = np.array(df['NSTOP'],int)
    df['stops'] = df['NSTOP']
    del df['NSTOP']
    if (stops >= 0):
        df = df.query("stops == "+str(stops))

    if len(df.index) == 0:
        return 0
    df['source'] = 'CLEARTRIP'
#    conn = MongoClient(config.DB_SERVER)
#    db = conn.database 
#    new_database = db.scrapedb  
#    data = df.to_dict(orient='records') 
#    result = new_database.insert_many(data)
    
    return df


if __name__ == '__main__':
    mydata = scrapenew_cleartrip('BLR','CCU','15/01/2020','15/01/2020','12/12/2019 16:48',
                       passengers='A-1_C-0_I-0', stops = 0 )
