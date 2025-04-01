# Local環境でのセットアップ(M1チップ想定)
## 事前準備
1. docker(docker-desktop)をインストールしておく
2. app/source/ にある「.env.example」を「.env」にコピー   
この際、以下の値は本番環境の「.env」からとってくること
    - "ENCRYPTION_KEY"
    - "SENDGRID_API_KEY"  
      
    なお、本番環境の「.env」をそのまま使うことはできないので注意。  
    これは、いくつかの設定（例えば、"ALLOWED_HOSTS"の値）がローカル運用には不適切なため。

    さらに、ローカルで使用する場合は、"TYPE"の値を"live-server"から変更する
    - TYPE=staging_server  

    これによって、データ収集タイミングを、本番環境（live-server）とずらすことができて、API呼び出しの集中を回避することができる。

## Command（appコンテナのShellにアタッチ）
```shell
docker-compose exec app bash
```

## dumpデータの作成：
本番環境で、appコンテナのShellにアタッチした上で、ダンプコマンドを実行する
（過去のダンプデータは、取得後にDB構造が変更された場合があると使えないので、本番環境から最新のダンプを取得するのが望ましい）
```shell
python manage.py custom_dumpdata --output custom_dumpdata_20240110.json
```
出力するdumpファイル名は適宜指定  
なお、「dumpdata.sh」には、出力ファイル名「dump.json」固定で、上記コマンドが記載されている

## dumpデータのロード
1. app/source/.env の"TYPE"の値を、一時的に"staging_server"から変更する
    - TYPE=develop  
    （"live_server", "staging_server"以外なら何でも良い）
     
2. ローカルのihi-backend-techリポジトリのapp/source配下にロード対象のdumpファイルを配置する

3. ローカルのihi-backend-techリポジトリのルートで下記コマンドを実行（M1チップを想定）
- DB、コンテナの削除（新規作成の場合は不要）
```shell
sudo rm -rf database/
docker-compose down --rmi all --volumes --remove-orphans
```
- コンテナ作成&実行  
```shell
docker-compose -f docker-compose_macm1.yml --profile admin up --build -d
```

- DB作成  
更新の場合は「makemigrations」が必要な場合がある。
```shell
docker-compose exec app python manage.py makemigrations
```  
新規作成の場合、「migrate」だけでよい
```shell
docker-compose exec app python manage.py migrate
```  

3. DBからデモデータの削除  
ポスグレに入る    
```shell
docker exec -it `(docker ps | grep postgres | awk -F' ' '{print $1}')` psql -U ihi ihi_db
```  
下記のSQLを流してデモデータ削除  
```SQL
delete from ihiapp_device;
delete from ihiapp_gateway;
update users_user set company_id_id = null;
delete from users_company;
delete from users_user;
delete from auth_permission;
delete from django_content_type;
```

4. データをloadする  
まず、appコンテナのShellにアタッチする。
```shell
docker-compose exec app bash
```  
Shell内で、次のコマンドを実行して、データをloadする
```shell
python manage.py loaddata custom_dumpdata_20231130.json
```
superuserを作成しておく
```shell
puthon manage.py createsuperuser
```
Shellを抜ける
```shell
exit
```

5. 後処理  
- 一旦、dockerを停止
```shell
docker-compose down
```
- app/source/.env の"TYPE"の値を、"staging_server"（開発環境）に戻す。（本番環境の場合は"live_server"）  

6. 起動  
オプション「-d」をつけることでバックグラウンド実行する（画面へのログ表示はなくなる）
```shell
docker-compose  -f docker-compose_macm1.yml --profile admin up -d
```

7. 終了  
```shell
docker-compose down
```

# redoc出力方法
0. python manage.py spectacular --file schema.json --format openapi-json
1. python convert_to_yaml_from_json.py
2. npm run docs:build　(docker外にて)
