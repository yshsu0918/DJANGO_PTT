# DJANGO_PTT

## 目錄

- 目的
- 爬蟲作法
- 更新規則
- 目前問題
- 擬解決辦法
- 更新日誌

## 目的

想要做出能查詢 "特定使用者" 所有留言的功能

eg.

loona
URL: https://www.ptt.cc/bbs/Gossiping/M.1555564095.A.3B8.
推 loona: 南部柯糞真的是喔 04/18 22:51
推 loona: 吃山豬屎的糞咖 04/18 22:52
推 loona: 連台北兜沒住過的 04/18 22:57
推 loona: google智障粉絲 04/18 22:58
推 loona: 郭董跟川普麻吉?? 04/18 22:59
URL: ...

## 爬蟲作法

- views.py -> update(timeinterval)
	1. boards = dfs_find_allboard() 把所有板找出來
	2. 取現在時間，並從各版中找出符合時間範圍的文章 (posttime > nowtime - timeinterval)。
	3. sess = pass_ask18()
	![](https://i.imgur.com/arATj9M.png)
	5. A = comments_in_article(ptturl+post[c],sess) list.append(A)
	6. 每三千筆寫入資料庫一次


## 更新規則

- 每小時更新一次 過去兩小時範圍的內容
- 每天更新一次 過去兩天範圍的內容
- BUG: 如果有人去回很舊的文章怎麼辦? 一周更新一次兩周範圍? 似乎無解

## 目前問題

- 資料庫設計不良，導致查詢使用者推文需要非常久
- 更新和查詢在同一個資料庫，導致在更新的時候不能查詢

## 擬解決辦法

關於索引
![](https://i.imgur.com/fGUmbUB.png)

0. 關server
1. 把原資料庫的資料轉到另外一個資料庫(Beta-db)
2. 刪除資料庫
3. 開server

- views.py 讀Beta-storage
- Beta-db
	- primary key 為 userID
	- 內容為所有留言．


## 更新日誌

| 日期 | 做了什麼 | 時長 |
| -------- | -------- | -------- |
| 20180420 | 上傳github, 解決 permission denied (publickey)   | 1 hr |
| 20180420 | README.md   | 1 hr |
| 20180421 | 研究如何改DB | 1hr |
| 20180421 | 在id上面加index | 1hr |
| 20180421 | bug , database lock, 可能發生在前次更新還沒結束的時候 | 10 min |
| 20180421 | 紀錄所用指令 | 15min |


## SQL


環境是sqlite3

http://www.runoob.com/sqlite/

table 有 search_ptt , search_querywho
以下都已經在bash底下執行 sqlite3 db.sqlite3




| 指令 | 功能 |
| -------- | -------- |
| .tables |查現有表|
| SELECT * FROM search_ptt WHERE id='a000000000' | 查a000000000 所有發文 |
| sqlite3 -csv "SELECT * FROM search_ptt ORDER BY id " > a.csv | 輸出到依據id排順序的 csv檔 |
