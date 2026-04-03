FROM node:20-alpine

WORKDIR /app

COPY package.json /app/package.json
COPY apps/web/package.json /app/apps/web/package.json

RUN npm install

COPY apps/web /app/apps/web

WORKDIR /app/apps/web

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]

