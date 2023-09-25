# SSL 憑證模組使用前配置
- 須在註冊好zerossl的帳號
- 使用此模組之前須在主機安裝 acme.sh
- 須在主機這定好dnspod的環境參數
- 需要將模組的路由 /.well-known/acme-challenge/{challenge_route} 引入專案並且對外

## 安裝 acme.sh
```
curl https://get.acme.sh | sh -s email=my@example.com
```
將 my@example.com 替換成 zerossl 註冊的 email

## 設定 dnspod 環境參數
在command line 輸入
```
export DPI_Key="youkey123123youkey"
export DPI_Id="1234"
```