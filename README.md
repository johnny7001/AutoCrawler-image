# 基本介紹
抓取  精選美女圖, 邏輯架構也可應用在爬取其他網站, 並且實現自動爬取及更新的功能<br> 
# 作品應用
* Selenium解決js渲染網頁部分, BeautifulSoup解析Html, 抓取整個網站的目錄大綱 
* MySQL資料庫存放數據, 設定狀態欄位, 避免重複爬取資料
* 從資料庫抓取網址並requests下載圖片到指定位址的資料夾
* Multi-threading Pool 實行多執行緒, 加快下載速度
* APSchedule 設定每日排程, 自動爬取並更新資料庫
* Docker打包爬蟲程式, 能直接在linux tmux上開啟多視窗執行爬蟲腳本並監測運行情況   

# 資料庫結構設計  
* 抓取各個分頁的網址尾綴  
table_name = all_category  
column_name = category_id (foreign key), category_name, category_url, updated_at, status  
* 抓取所有分頁內的作品名稱及網址  
table_name = all_album  
column_name = category_id (連結all_category的category_id), album_id, album_name, album_url, album_img (封面圖), updated_at, status  
* 抓取各作品網址內的所有圖片  
table_name = imgs  
column_name = album_id (連結all_album的album_id), imgs_id, imgs_url <br>
![image](https://github.com/johnny7001/AutoCrawler-image/blob/7d6be145536604dc7c6420f3500295937356753e/db%E6%9E%B6%E6%A7%8B%E5%9C%96.jpg)

# 執行步驟

step1: 先用main.py抓取各個分頁的網址尾綴&所有分頁內的作品名稱及網址<br>
step2: get_jpmb_img.py 抓取各作品網址內的所有圖片<br>
step3: download_data.py會下載檔案  


