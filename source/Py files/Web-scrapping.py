# pip install selenium
# pip install webdriver-manager

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("https://www.redbus.in/")

time.sleep(5)

body_govt_bus=WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="homeV2-root"]/div[3]'))) # wait till the GOVT bus pannel appears
view_all_govt_bus = driver.find_elements(By.XPATH,'//*[@id="homeV2-root"]/div[3]/div[1]/div[2]/a')
view_all_govt_bus_link = view_all_govt_bus[0].get_attribute("href")

driver.get(view_all_govt_bus_link)

time.sleep(5)

data = driver.find_elements(By.CSS_SELECTOR,"a.D113_link")

### creating the dictionary to store the govt buses and their link to route detail page
links = {}
for i in data:
    _url = i.get_attribute("href")
    links[i.text] = _url

#### initialise super lists to store all the data
routenames_list = []
routelink_list = []

### loop to open each available routes
for i in links.keys():      #links 1 is used only for testing, use links in actual code
    driver = webdriver.Chrome()
    driver.implicitly_wait(1) 
    driver.get(links[i]) ## here to links1 to links (based on req)
    time.sleep(4)
    if not driver.maximize_window():
        driver.maximize_window()
    time.sleep(2)


    body=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME,'footer'))) # wait till the footer tag is available in the site
    routenames = driver.find_elements(By.CSS_SELECTOR,"a.route")
    routelink = [j.get_attribute("href") for j in routenames]
    pages = driver.find_elements(By.CLASS_NAME,'DC_117_pageTabs')
    if len(routenames) > 0:
        routenames_list.extend([t.text for t in routenames])
        routelink_list.extend(routelink)
    
    wait=WebDriverWait(driver,20)
    
    if len(pages) > 1:
        for k in range(2,len(pages)+1):
            pagination_container=wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="root"]/div/div[4]/div[12]')))
            next_page_button=pagination_container.find_element(By.XPATH,f'.//div[contains(@class,"DC_117_pageTabs") and text()="{k}"]')
            
            # driver.maximize_window()
            actions = ActionChains(driver)
            actions.move_to_element(next_page_button).perform()
            time.sleep(2)
            
            next_page_button.click()
            body=WebDriverWait(driver, 9).until(EC.presence_of_all_elements_located((By.TAG_NAME,'body')))
            routenames = driver.find_elements(By.CSS_SELECTOR,"a.route")
            routelink = [j.get_attribute("href") for j in routenames]
            routenames_list.extend([t.text for t in routenames])
            routelink_list.extend(routelink)

def bus_id_data_derive(bus_id1):
    bus_id1_data = []
    for bus_id1_instance in bus_id1:
        div_elements = bus_id1_instance.find_elements(By.TAG_NAME, "div")
        # classes[]
        temp_dict = {}
        for div in div_elements:
            class_name = div.get_attribute("class")
            if 'column' in class_name:
                continue   
            temp_dict[class_name] = div.text
            # print('\n',class_name," : ",div.text)
        bus_id1_data.append(temp_dict)
    return bus_id1_data

#######  collecting bus details #############
################## introduce a loop to open all the route links #########################
from selenium.common.exceptions import NoSuchElementException
route_bus_dict = {}     
route_bus_dict1 = {}    
route_bus_detail_dict = {}   
route_travel_date_dict = {}   

for route in range(len(routelink_list)):
    driver = webdriver.Chrome()
    driver.get(routelink_list[route])
    time.sleep(10)

    try:
        bus_found = driver.find_element(By.XPATH,'//*[@id="root"]/div/div[2]/div/div[2]/div[1]/div[1]/span[1]/span')
    except NoSuchElementException:
        print("no bus found")
        route_travel_date = driver.find_element(By.XPATH,'//*[@id="searchDat"]').get_attribute("value")
        if routenames_list[route] in route_travel_date_dict.keys():
            alternate_travel_name = routenames_list[route]+str(route)
            route_travel_date_dict[alternate_travel_name] = {'link':routelink_list[route],'travel_date':route_travel_date,'bus_found':'no'}
        else:
            route_travel_date_dict[routenames_list[route]] = {'link':routelink_list[route],'travel_date':route_travel_date,'bus_found':'no'}
        continue
    except:
        bus_found = driver.find_element(By.XPATH,'//*[@id="root"]/div/div[2]/div/div[2]/div[1]/div[1]/span[1]/span')
        
    count_of_bus_found = bus_found.text.split()
    
    try:
        view_govt_bus=WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'i[class="p-left-10 icon icon-down"]')))
    except:
        pass

    route_travel_date = driver.find_element(By.XPATH,'//*[@id="searchDat"]').get_attribute("value")

    if routenames_list[route] in route_travel_date_dict.keys():
        alternate_travel_name = routenames_list[route]+str(route)
        route_travel_date_dict[alternate_travel_name] = {'link':routelink_list[route],'travel_date':route_travel_date,'bus_found':'yes'}
    else:
        route_travel_date_dict[routenames_list[route]] = {'link':routelink_list[route],'travel_date':route_travel_date,'bus_found':'yes'}
    
    
    vgb = driver.find_elements(By.CSS_SELECTOR,'i[class="p-left-10 icon icon-down"]')
    
   
    if len(vgb) > 0:
        for v in vgb[::-1]:
            actions = ActionChains(driver)
            actions.move_to_element(v).perform()
            time.sleep(5)
            v.click()
    
    
    body1=driver.find_element(By.TAG_NAME,"body")
    while True:
        bus_detail_count = driver.find_elements(By.XPATH,'//*[@class="travels lh-24 f-bold d-color"]')
        
        bus_id1 = driver.find_elements(By.XPATH,'//div[contains(@class,"clearfix row-one")]')
        
        body1.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        
        if len(bus_detail_count) == int(count_of_bus_found[0]):
            break
        
    if routenames_list[route] in route_bus_dict1.keys():
        alternate_name1 = routenames_list[route]+str(route)
        route_bus_dict1[alternate_name1] = bus_id1 
    else:
        route_bus_dict1[routenames_list[route]] = bus_id1 
    #==================== saving the details in dic =================#    
    if routenames_list[route] in route_bus_detail_dict.keys():
        alternate_name = routenames_list[route]+str(route)
        route_bus_detail_dict[alternate_name] = bus_id_data_derive(bus_id1)
    else:
        route_bus_detail_dict[routenames_list[route]] = bus_id_data_derive(bus_id1)

    driver.quit()




import json
with open("route_bus_detail_dict.txt",'w') as file1:
    json.dump(route_bus_detail_dict,file1)
with open("route_travel_date_dict.txt",'w') as file2:
    json.dump(route_travel_date_dict,file2)
