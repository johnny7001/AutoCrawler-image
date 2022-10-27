import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from db.jpmnbDB import DB
from pkg.message import message
from pkg.get_key import get_key
db = DB()

# 獲取網頁原始碼
def get_htmlCode(url):
    resp = requests.get(url)
    resp.text
    resp.encoding = 'utf8'
    content = resp.text
    return content

# 獲取各目錄頁的標題, 網址
def get_categoryData(url, content):
    head_urlList = url.split('/')
    head_url = head_urlList[0] + '//' + head_urlList[2]
    # print(head_url) 
    category_url = ''
    soup = BeautifulSoup(content, 'html.parser')
    allURl = soup.find_all('li', class_='menu-item')
    for url in allURl:
        title = url.find('a').get('title') # 目錄標題
        if title != None:
            tail_url = url.find('a').get('href') #
            category_url = head_url + tail_url # 目錄網址
            # print(title, category_url)
            updated_at = '{0:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.now(timezone.utc) + timedelta(hours=8)) # 更新時間
            status = 0 # 狀態, 預留用
            # 判斷目錄頁名稱是否存在, 設定category_name = unique, 若不存在則insert, 存在則更新網址
            sql = "INSERT INTO `jpmnb_category` (`category_name`, `category_url`, `updated_at`, `status`) \
                VALUES ('{}', '{}', '{}', '{}') ON DUPLICATE KEY UPDATE `category_url` = '{}';\
                    ".format(title, category_url, updated_at, status, category_url)
            db.query(sql)
            message(f'insert {title}, {category_url}, {status} success!!')
    db.close()    

# 抓取最終頁 (不包括精品散圖)
def get_finalPage(content):
    soup = BeautifulSoup(content, 'html.parser')
    # 最終頁
    tail_page = 0
    pageUrl_list = []
    pageNum_list = []
    # 找到該目錄所有的頁數
    totalPages = soup.find('div', class_='pagination1').find_all('a')
    for page_num in totalPages:
        pageUrl_list.append(page_num.get('href'))
        pageNum_list.append(page_num.text)
    pageDict = dict(zip(pageUrl_list, pageNum_list))
    # 假如有尾頁就抓取尾頁的頁碼
    if '尾页' in list(pageDict.values()):
        tail_page = get_key(pageDict, '尾页')[0].split('index')[1].replace('.html', '')
    else:
        while ('下一页' in pageNum_list):
            pageNum_list.remove('下一页')
        while ('尾页' in pageNum_list):
            pageNum_list.remove('尾页')
        pageNum_list.sort(reverse=True)
        tail_page = int(pageNum_list[0])
    return tail_page

# 精品散圖最終頁
def get_finalPage1(content):
    soup = BeautifulSoup(content, 'html.parser')
    tail_page = 0
    pageNum_list = []
    # 找到該目錄所有的頁數
    pageList = soup.find('div', class_='list')
    totalPages = pageList.find('div', class_='pagination1').find_all('a')
    for page in totalPages:
        pageNum_list.append(page.text)
    pageNum_list.sort(reverse=True)
    tail_page = int(pageNum_list[0])
    return tail_page
        

# 獲取各目錄頁內的相簿標題, 網址
def get_CategoryFinalPage(content):
    album_dict = {}
    title_list = []
    page_list = []
    
    # sql = "SELECT `category_name`, `category_url` FROM `jpmnb_category` WHERE `category_url` like '%/plus/search%';"
    sql = "SELECT `category_name`, `category_url` FROM `jpmnb_category`;"
    result = db.query(sql).fetchall()
    for item in result:
        title = item['category_name']
        title_list.append(title)
        category_url = item['category_url']
        content = get_htmlCode(category_url)
        if '/plus/search' in category_url:
            finalPage = get_finalPage1(content)
        else:
            finalPage = get_finalPage(content)
        # print(finalPage1)
        # print(f'{title} 的最終頁是： {finalPage}')      
        page_list.append(finalPage)
    album_dict = dict(zip(title_list, page_list))
    return album_dict