FROM node:16.15.0
WORKDIR /src

RUN apt update \
    && yarn install
RUN yarn global add vercel
RUN npm install -g @vue/cli@latest
# ENV VERCEL_ORG_ID=team_7Dr649Q9NghDlO7lNF9Cnggu
# ENV VERCEL_PROJECT_ID=prj_6u7NrCJqkIqN3jeoRuoLKZQzFQaw
# RUN vercel pull --yes --debug --environment=development --token=wohADBwgcdCz4Zuf3y1R9I6P
# RUN vercel pull --yes --debug --environment=preview --token=wohADBwgcdCz4Zuf3y1R9I6P
# RUN vercel build --debug --token=wohADBwgcdCz4Zuf3y1R9I6P

# 作ってみたはいいけど vercel devでコケるので一旦使わない。今はyarn devを実行する感じに。
# CMD [ "./vercel_serve_for_docker_cmd.sh" ]

EXPOSE 5173
