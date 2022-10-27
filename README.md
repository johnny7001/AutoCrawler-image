# 資料庫結構設計  
* 抓取各個分頁的網址尾綴  
table_name = all_category  
column_name = category_id (foreign key), category_name, category_url, updated_at, status  
* 抓取所有分頁內的作品名稱及網址  
table_name = all_album  
column_name = category_id (連結all_category的category_id), album_id, album_name, album_url, album_img (封面圖), updated_at, status  
* 抓取各作品網址內的所有圖片  
table_name = imgs  
column_name = album_id (連結all_album的album_id), imgs_id, imgs_url  


