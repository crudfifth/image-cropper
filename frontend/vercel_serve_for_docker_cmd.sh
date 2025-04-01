# pullを毎度実行し.vercelを最新に保つため、docker立ち上げのたびに毎度 pull/build/dev を実行する。

# 作ってみたはいいけど vercel devでコケるので一旦使わない。今はyarn devを実行する感じに。

cd /src # 実行はdashboardの１つ上の階層で。
export VERCEL_ORG_ID=team_7Dr649Q9NghDlO7lNF9Cnggu
export VERCEL_PROJECT_ID=prj_6u7NrCJqkIqN3jeoRuoLKZQzFQaw
vercel pull --yes --debug --environment=development --token=wohADBwgcdCz4Zuf3y1R9I6P
vercel pull --yes --debug --environment=preview --token=wohADBwgcdCz4Zuf3y1R9I6P

vercel build --debug --token=wohADBwgcdCz4Zuf3y1R9I6P

vercel dev --debug --listen 5173 --token=wohADBwgcdCz4Zuf3y1R9I6P 