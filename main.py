from pkg.getData import get_htmlCode, get_CategoryFinalPage
from pkg.message import message
from bs4 import BeautifulSoup
from db.jpmnbDB import DB
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing import Pool
import time

db = DB()
# 讀取首頁html_code
# with open('html_source.txt', 'r', encoding='utf-8') as file:
#     content = file.read()

# 獲取目錄分頁的網址, 並回傳list
def get_AllCategoryUrl(album_dict):
    try:
        # album_dict = get_CategoryFinalPage(content) # 目錄名稱：總頁數 ex: {'XiuRen秀人网': '284'}
        # print(album_dict)
        sql = "SELECT `category_id`, `category_name`, `category_url` from `jpmnb_category`"
        result = db.query(sql).fetchall() # type = list
        if result != None:
            # 逐筆載入
            pageUrl_list = []
            for per_page in result: 
                first_page = per_page['category_url'] # 首頁網址
                category_name = per_page['category_name']
                final_page = int(album_dict[f'{category_name}']) # 最終頁的頁碼
                for page in range(1, final_page+1):
                    pageUrl = first_page if page == 1 else first_page + f'index{page}.html'
                    # print(pageUrl)
                    pageUrl_list.append(pageUrl)
                        
            return pageUrl_list
    except Exception as err:
        message(f'get data faild ,err: {err}')
        
# 主程式
def main(url):
    try:
        # for categroyUrl in pageUrl_list:
        indexUrl = url.split('index')[0]
        # print(indexUrl)
        sql = "SELECT `category_id` from `jpmnb_category` WHERE `category_url` = '{}'".format(indexUrl)
        result = db.query(sql).fetchone()
        category_id = result['category_id']
        
        content = get_htmlCode(url)
        head_urlList = url.split('/')
        head_url = head_urlList[0] + '//' + head_urlList[2]
        status = 0 # 尚未下載
        soup = BeautifulSoup(content, 'html.parser')

        allAlbum = soup.find_all('article', class_='excerpt excerpt-c5')
        for per_album in allAlbum:
            title = per_album.find('a', class_='thumbnail').get('title')
            album_url = head_url + per_album.find('a', class_='thumbnail').get('href')
            cover_img = head_url + per_album.find('a').find('img').get('src')
            updated_at = '{0:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.now(timezone.utc) + timedelta(hours=8)) # 更新時間
            sql = "INSERT INTO `jpmnb_album` (`category_id`, `album_name`, `album_url`, `cover_img`, `updated_at`, `status`) \
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}') ON DUPLICATE KEY UPDATE `album_name` = '{}';\
                ".format(category_id, title, album_url,cover_img,updated_at, status, title)
            # print(f'目錄id：{category_id}, 標題：{title}, 封面圖鏈結：{cover_img}, 寫真鏈結：{album_url}')
            db.query(sql)
            message(f'insert {title}, {album_url}, {status} success!!')
        db.close()  
    except Exception as err:
        message(f'insert data faild ,err: {err}')

# 多線程
def threading():
    # 主網址
    url = 'https://www.jpmnb.net/'
    # url = 'https://www.jpmnb.net/Xrqj/XiuRen/'
    # main(url)
    content = get_htmlCode(url)
    album_dict = get_CategoryFinalPage(content)

    pageUrl_list = get_AllCategoryUrl(album_dict)
    start_4=time.time()
    pool = Pool(processes=4)
    pool.map(main, pageUrl_list)
    end_4= time.time()
    print('4個進程',end_4-start_4)
    pool.terminate() # terminate() 通常在主程序的可並行化部分完成時調用。
    pool.join() # 調用 join() 以等待工作進程終止。
    
if __name__=='__main__':    
    scheduler = BlockingScheduler(timezone="Asia/Taipei")
    # 設定每週一到日上午9:30分自動爬取並更新資料庫
    scheduler.add_job(threading, 'cron', day_of_week='0-6', hour=9, minute=30)
    scheduler.start()
