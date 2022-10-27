from db.jpmnbDB import DB
import os
import requests
import json
from multiprocessing import Pool
import time
import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, filename='download_data.log', filemode='w', format=FORMAT)
db = DB()


def get_jpmnb_img_mysql(album_id) -> dict:
    """
    Accepts:
        album_id : 相簿id
    Returns:
        回傳該相簿內所有圖片的
        select `album_id`,`img_url`,`img_id` from jpmnb_img where `album_id` = {album_id} and `status`= 0 order by  img_id;
    """
    sql_get_data: str = f"select `album_id`,`img_url`,`img_id`, `img_page` from jpmnb_img where `album_id` = {album_id} and `status`= 0 order by  img_id;"
    # 執行SQL語句
    results = db.query(sql_get_data).fetchall()
    return results


def get_jpmnb_album_mysql() -> dict:
    """
    Returns:
        回傳要抓取的相簿資料, album status = 2 or 3
    """
    sql_get_data: str = f"select `album_id`,`album_url`,`cover_img` from `jpmnb_album` where `status` = 2 or `status` = 3 ;"
    # 執行SQL語句
    results = db.query(sql_get_data).fetchall()
    return results


def change_jpmnb_album_mysql(status, album_url):
    """
    Args:
        status (int): 相簿的狀態, 0=未下載, 1=insert資料庫中, 2=insert資料庫完成, 3=圖片下載中, 4=圖片下載完成
        album_url (string): 相簿網址
    Returns:
        依據參數修改相簿狀態
    """
    sql_change_data: str = f"update jpmnb_album  set `status` = {status} where `album_url` = '{album_url}';"
    # 執行SQL語句
    db.query(sql_change_data)


# 下載相簿圖片到資料夾, 資料夾名稱設動為相簿id (相簿id是唯一鍵)
def download_file(img_id, album_id, imgUrl_list, album_url, img_page):
    """
    Args:
        img_id (int): 圖片id
        album_id (int): 相簿id
        imgUrl_list (list): 當前頁面所有的圖片網址
        album_url (string): 相簿網址
        img_page (int): 圖片頁碼
    Returns:
        修改圖片狀態並下載圖片到指定位址
    """
    # print(short_url)
    count = 1
    sql = f'UPDATE `jpmnb_img` SET `status` = 1 WHERE `img_id` = {img_id}'
    db.query(sql)

    for img_url in imgUrl_list:

        img_name = f"{img_page}_{count}"
        change_jpmnb_album_mysql(3, album_url)
        r = requests.get(img_url)
        if os.path.isfile(f"jpmnb_net/{album_id}/{img_name}") != True:
            with open(f"jpmnb_net/{album_id}/{img_name}.jpg", 'wb') as f:
                # 將圖片下載下來
                f.write(r.content)
        count += 1
    print("載完", imgUrl_list)
    sql = f'UPDATE `jpmnb_img` SET `status` = 2 WHERE `img_id` = {img_id}'
    db.query(sql)


# 下載相簿封面圖片到資料夾
def download_cover_img(name, cover_img):
    """
    Args:
        name (int): 相簿id
        cover_img (string): 封面圖面網址
    Returns:
        下載封面圖片到指定位址
    """
    r = requests.get(cover_img)
    # print(f'jpmnb_net/{name}/{pic_number}.jpg')
    if os.path.isdir(f"jpmnb_net/{name}") != True:
        os.mkdir(f"jpmnb_net/{name}")
    if os.path.isfile(f"jpmnb_net/{name}/cover_img.jpg") != True:
        with open(f"jpmnb_net/{name}/cover_img.jpg", 'wb') as f:
            # 將圖片下載下來
            f.write(r.content)


# 下載json檔案
def download_json(name):
    """
    Args:
        name (int): 相簿id
    Returns:
        下載json檔到指定位址
    """
    sql = f"SELECT `album_id`, `album_name`, `album_url`, `cover_img` FROM `jpmnb_album` WHERE `album_id` = {name};"
    result = db.query(sql).fetchone()  # dict
    # album_id = result['album_id']
    # print(result)
    try:
        if os.path.isfile(f"jpmnb_net/{name}/{name}.json") != True:
            with open(f"jpmnb_net/{name}/{name}.json", 'w', encoding='utf-8') as file:
                json_dumps_str = json.dumps(result, ensure_ascii=False, indent=4)
                print(json_dumps_str, file=file)
            print(f'寫入相簿id_{name}的json檔成功')
    except Exception as err:
        print(f'寫入相簿id_{name}的json檔失敗, 錯誤碼: {err}')


if __name__ == "__main__":
    while True:
        try:
            all_cover_img = get_jpmnb_album_mysql()
            # print(all_cover_img)
            for cover_img in all_cover_img:
                # 下載封面圖片
                download_cover_img(cover_img['album_id'], cover_img['cover_img'])
    
                # 下載json
                download_json(cover_img['album_id'])
                all_url = get_jpmnb_img_mysql(cover_img['album_id'])
                # print(all_url)
                total_urlArgs_list = []
                for url in all_url:
                    imgUrl_list = json.loads(url['img_url'])
                    urlArgs_tuple = (
                    url['img_id'], url['album_id'], imgUrl_list, cover_img['album_url'], url['img_page'])
                    total_urlArgs_list.append(urlArgs_tuple)
                # print(total_urlArgs_list)
                start_4 = time.time()
                pool = Pool(processes=4)
                pool.starmap(download_file, total_urlArgs_list)
                end_4 = time.time()
                print('4個進程', end_4 - start_4)
                pool.terminate()  # terminate() 通常在主程序的可並行化部分完成時調用。
                pool.join()  # 調用 join() 以等待工作進程終止。
                change_jpmnb_album_mysql(4, cover_img['album_url'])
            db.close()
        except Exception as err:
            logging.info(f'下載影片{err}, 失敗, 請再確認')