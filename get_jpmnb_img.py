from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup
from db.jpmnbDB import DB
import json
import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, filename='get_jpmnb_img.log', filemode='w', format=FORMAT)

db = DB()


def all_pic_url(url, total_page) -> list:
    """
    Args:
        url (string): 相簿網址
        total_page (int): 該相簿裡面有幾頁
    Returns:
        拿到目錄的頁數網址list
    """
    new_url = url.split(".html")
    all_pic_url = []
    for page in range(int(total_page)):
        if page == 0:
            pic_url = f'{new_url[0]}.html'
            all_pic_url.append(pic_url)
            continue
        pic_url = f'{new_url[0]}_{page}.html'
        all_pic_url.append(pic_url)
    return all_pic_url


def get_picture(url):
    """
    Args:
        url (string): 拿到相簿內的分頁網址
    Returns:
        拿到該分頁內所以的圖片網址並回傳json
    """

    title = "https://www.jpmnb.net"
    r = requests.get(url)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup)
    a = []
    r1 = soup.find_all('img')
    for x in r1:
        r2 = x.get('src')
        if 'img' not in r2:
            a.append(r2)
    total_pic_url = []
    for x in range(0, len(a)):
        img_url = title + a[x]
        total_pic_url.append(img_url)
        # total_pic_url[f"{x}"] = img_url
    metadata_json = json.dumps(total_pic_url)
    return metadata_json


def get_finalPage(x):
    """
    Args:
        x (string): 相簿網址
    Returns:
        拿到該相簿的總頁數
    """
    r = requests.get(x)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, 'html.parser')
    # 最終頁
    tail_page = 0
    pageUrl_list = []
    pageNum_list = []
    # 找到該目錄所有的頁數
    totalPages = soup.find('div', class_='pagination1').find_all('a')
    for page_num in totalPages:
        pageUrl_list.append(page_num.get('href'))
        pageNum_list.append(page_num.text)
    if pageNum_list[-2] is not None:
        return pageNum_list[-2]


def fill_in_mysql(album_id, img_url, img_page):
    """
    Args:
        album_id (string): 相簿id
        img_url (string): 相簿內該分頁所有圖片的網址
        img_page (int): 當前相簿的頁碼
    Returns:
        insert 進資料庫
    """
    sql_get_data: str = f"INSERT INTO `jpmnb_img` (`album_id`, `img_url`,`status`, `img_page`) VALUES ({album_id},'{img_url}',0, {img_page});"
    db.query(sql_get_data)
    print("success", img_url)



def get_data_mysql() -> dict:
    """從jpmnb_album資料庫中拿到資料"""
    sql_get_data: str = f"SELECT `album_id`,`album_url` FROM jpmnb_album  where status = 0 or status = 1 "
    results = db.query(sql_get_data).fetchall()
    return results


if __name__ == '__main__':
    # 用 while true 的原因為了解決
    while True:
        try:
            all_data = get_data_mysql()
            for data in all_data:
                album_id = data['album_id']
                album_url = data['album_url']
                total_page = get_finalPage(album_url)
                total_img_url = all_pic_url(album_url, total_page)
                # print(total_img_url)
                count = 0
                for img_url in total_img_url:
                    pic_json = get_picture(img_url)
                    count += 1
                    updated_at = '{0:%Y-%m-%d %H:%M:%S.%f}'.format(
                        datetime.now(timezone.utc) + timedelta(hours=8))  # 更新時間
                    sql = f"UPDATE `jpmnb_album` SET `status` = 1,`updated_at` = '{updated_at}' WHERE `album_url` = '{album_url}'"
                    db.query(sql)
                    fill_in_mysql(album_id, pic_json, count)
                sql = f"UPDATE `jpmnb_album` SET `status` = 2 WHERE `album_url` = '{album_url}'"
                db.query(sql)
            db.close()
        except Exception as err:
            logging.info(f'轉入img資料庫{err}, 失敗, 請再確認')