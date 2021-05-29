from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pymysql

# 資料庫設定
DB = pymysql.connect(user='root', password='********', host='localhost',
                     port=3306, database='test', charset='utf8')

# 要更新爬蟲資料必須先刪除舊資料
delete_all_rows = """truncate table weather_crawler """
cur = DB.cursor()
cur.execute(delete_all_rows)
cur.close()
DB.commit()

chrome = webdriver.Chrome('./chromedriver')
chrome.get('https://www.cwb.gov.tw/V8/C/W/week.html')
chrome.execute_script('window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" })')
time.sleep(3)


detail_html_sp = BeautifulSoup(chrome.page_source, 'html.parser')
detail_container = detail_html_sp.find('main', class_='main-content container')

city_html = detail_html_sp.find_all('h4')
city_name_list = []
for el in city_html:
    name = el.text.strip()
    city_name_list.append(name)
    
city_date_list = []
day_weather_list = []
night_weather_list = []
rows = detail_html_sp.find_all('div', class_='panel-body')
for i in range(0, len(rows)):
    dates = rows[i].find_all('li', class_='date')
    city_date = []
    for date in dates:
        character = date.text.strip().replace('\n', ' ')
        city_date.append(character)   
            
    city_date_list.append(city_date)
    
    day_weather = rows[i].find_all('li', class_='Day')
    city_day_weather = []
    for weather in day_weather:
        temp = weather.find('span', class_='tem-C is-active').text.replace('\u2002-\u2002', '-')
        image = weather.find('img')['title']
        character = image + ' ' + temp + '°C'
        city_day_weather.append(character)
         
            
    day_weather_list.append(city_day_weather)
    
    night_weather = rows[i].find_all('li', class_='Night')
    city_night_weather = []
    for weather in night_weather:
        temp = weather.find('span', class_='tem-C is-active').text.replace('\u2002-\u2002', '-')
        image = weather.find('img')['title']
        character = image + ' ' + temp + '°C'
        city_night_weather.append(character)
         
            
    night_weather_list.append(city_night_weather)
    
store_time = len(city_name_list)    

for i in range(0, store_time):
    cur = DB.cursor()
    handle_date_message = str(city_date_list[i]).replace("'", "\\\'")
    handle_day_message = str(day_weather_list[i]).replace("'", "\\\'")
    handle_night_message = str(night_weather_list[i]).replace("'", "\\\'")
    
    store_target = {
        'city': city_name_list[i],
        'date': handle_date_message,
        'day': handle_day_message,
        'night': handle_night_message,
    }

    sql = "INSERT INTO weather_crawler (`city`, `date`, `day`, `night`, `time_create`) VALUES('{city}', '{date}', " \
          "'{day}', '{night}', NOW())"
    sql = sql.format(**store_target)
    cur.execute(sql)
    cur.close()
    DB.commit()

DB.close()  
