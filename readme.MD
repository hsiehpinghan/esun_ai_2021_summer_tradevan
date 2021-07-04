# 本文說明，本專案係參加玉山-2021 ＡI人工智慧手寫中文字辨識公開挑戰賽「API最佳服務獎」之說明文件，我們是參賽隊伍「AI-Yodass』。我們是一支產學合作的隊伍。

* [設計緣起](#設計緣起)
* [發現問題](#發現問題)
* [系統目標](#系統目標)
* [API服務架構](#API服務架構)
* [實測結果](#實測結果)
* [參賽結果](#參賽結果)
* [硬體資源](#硬體資源)
* [架構圖](#架構圖)
* [循序圖](#循序圖)
* [打包方式](#打包方式)
* [啟動方式](#啟動方式)
* [測試程式](#測試程式)

# 設計緣起

玉山-2021ＡI人工智慧手寫中文字辨識公開挑戰賽參賽期間，我們一直不斷地優化AI模型的精準度，導致模型愈來愈大，推論的時間也拉長，五月的測試賽原本本團隊都保持在第七名的成績，但在6月8日的加場測試賽時，我們團隊的成績竟然因為模型過大，導致推論時間過長，比賽成績還因此跌出前十名以外，因此我們開始研究如何提高api系統服務的效能與吞吐量？

# 發現問題

五月連續三天的測試賽，本團隊使用單一模型上線參賽，當時前三天成績一直穩定保持在第七名。
到了6/8的加場測試賽前一天，本團隊開始使用重新訓練的 ensemble 模型，本團隊測試流程先將這個模型放在 GCP 上運行，經測試後回應時間介於0.65~0.85秒之間，因此認為這個模型應該沒有太大問題。

但是在6/8測試賽時因為有少部份的request回應時間會大於1秒，玉山主辦單位會重送這些 request ，造成 request 量變多，回應時間變慢，所以愈來愈多 timeout 案例發生，最後在6/8日該場加測賽結束後，統計結果我們收到2000多筆逾時結果。
因此如何在提高模型精準度之後，亦能顧及api 服務效能，以提高服務吞吐量及響應成功率？成為我們進入正式決賽前要嚴肅面對與解決的關鍵問題。

# 系統目標

因此我們以以下四個重點目標進行系統設計：  
1. 吞吐量彈性：比賽要求需能同時處理3~10個 request，並在一秒內 response 。因此系統需可以以設定參數的方式，在開發環境與正式環境調整 request 的處理效率。  
2. 回應成功率：因為即使 request timeout ， server 端已完成推論，因此在下次 request 時， server 應直接 response 已計算完的結果不需重算，以確保回應成功率。  
3. 佈署便利性：團隊成員的開發環境在 linux 及 windows 都有，而且比賽伺服器預定是筆電但需有雲端伺服器當備案，所以系統架構必須同時可以在這些環境開發及佈署；此外每日比賽完後需重新 fine tune 模型及更版，所以也必需能方便且快速地重新佈署模型。  
4. 經濟性：因為 GPU 要價不斐，所以僅在模型訓練期間使用 Colab GPU ，在比賽期間使用 CPU 進行推論； Cluster 的解決方案(ex. k8s)因為需開多台機器花費較大，所以採用單一台機器做為解決方案。  

# API服務架構

經過團隊的努力下，不斷地進行壓測與單元測試，我們設計採用 Docker 容器技術並以 Docker-Compose 進行容器編排以構建多層次架構服務組態，由 Nginx 容器負責 Round Robin Load Balance 給5台 Flask 推論服務器，而這5台推論服務器將推論的結果 Cache 到 Redis 服務器，如果收到同樣的 Request ，任意一台推論服務器都可以將之前計算的結果 Response 給用戶端。

# 實測結果

1. 可在服務啟動時下指令決定啟動 Flask 推論服務器的數量，以調整 request 處理效率。(ex. 本機開發階段只啟動1台 Flask 推論服務器以提升開發效率；正式環境啟動5台 Flask 推論服務器以符合比賽要求)
2. 壓測1萬個 request ，且每秒同時發送5個 requests的情況下，response 都能維持在0.85秒左右回應。
3. 在本機開發與正式環境佈署都使用同一套指令與流程進行測試及佈署；且每日 fine tune 完模型後，可在10分鐘內重新打包成 docker image 及佈署上線。
4. 即使是使用 ensemble 5 個 EfficientNetB0 的大模型，只使用 CPU 及單機伺服器，也可以符合主辨單位的要求。

# 參賽結果

在6/15-6/18的正式賽，我們正式使用了 Load Balance (Nginx)+5台的 Container App 架構上線參賽。 然後我們正式賽四天各單日成績取得了第一天(6/15)第3名、第二天(6/16)第4名、第三天(6/17)第5名、第四天(6/18)第1名的優異成績，最後經大會結算榮獲亞軍的榮譽。

# 硬體資源

我們使用以下規格的筆電架設我們的服務：  
* 作業系統: Ubuntu 20.04
* CPU: 6 core / 12 thread
* RAM: 32 GB
* HD: PCI-SSD

# 架構圖

![](assets/系統架構.png)

1. Nginx Load Balance Server: 接收 request，並以 Round Robin 方式 Load Balance 給5台 Flask Inference Server。
2. Flask Inference Server: 收到 Nginx Load Balance Server 轉發的 request 後，先以 esun_uuid 查詢 Redis Cache Server 是否已有資料，如果有則讀取 Cache 中的資料回傳，沒有才呼叫模型進行推論。
3. Redis Cache Server: 以 esun_uuit 為 key 值存放 Flask Inference Server 的推論結果。

# 循序圖

![](assets/循序圖.png)

1. esun 客戶端發送 request。
2. api 記錄 log 後向 service 查詢推論結果。
3. service 先查詢 cache 中是否有之前算過的答案，如果有則直接回傳；如果沒有則呼叫 domain 。
4. domain 將 request 中的 base64 字串轉換成圖檔，並 resize 成模型輸入的大小 (224×224×3)後，輸入模型取得預測的文字，如果在玉山800字的字集中則直接回傳答案，否則回傳 isnull。
5. sevice 取得預測的文字，並將推論結果儲存至 cache 後將結果回傳。

# 打包方式
首先下載本專案  

    git clone https://github.com/hsiehpinghan/esun_ai_2021_summer_tradevan.git
## Nginx Load Balance Server Image 打包方式
    cd esun_ai_2021_summer_tradevan/nginx
    build -t hsiehpinghan/load_balance:1.0.0 .
    docker push hsiehpinghan/load_balance:1.0.0
## Flask Inference Server Image 打包方式
將 https://drive.google.com/drive/folders/1Fa_qgc-xE3_sbrMy04bLzANyvUor4kk-?usp=sharing 中的模型放到 esun_ai_2021_summer_tradevan/model 資料夾下並執行以下指令：

    cd esun_ai_2021_summer_tradevan
    build -t hsiehpinghan/esun_ai_2021_summer_tradevan:6.0.0 .
    docker push hsiehpinghan/esun_ai_2021_summer_tradevan:6.0.0
# 啟動方式
## 開發環境
執行以下指令: (只啟動1台 Flask 推論服務器節省資源)

    cd esun_ai_2021_summer_tradevan
    docker-compose up -d --scale esun_ai_2021_summer_tradevan=1 
## 正式環境
執行以下指令: (同時啟動5台 Flask 推論服務器提升 request 處理效率)

    cd esun_ai_2021_summer_tradevan
    docker-compose up -d --scale esun_ai_2021_summer_tradevan=5 
# 測試程式
|          測試項目           |         測試程式                                                           |
| --------------------------- | -------------------------------------------------------------------------- |
| 模型推論測試                | esun_ai_2021_summer_tradevan/tests/esun/domain/test_image_entity.py        |
| cache 測試                  | esun_ai_2021_summer_tradevan/tests/esun/application/test_image_service.py  |
| 壓力測試                    | esun_ai_2021_summer_tradevan/tests/esun/interfaces/rest/test_api.py        |
