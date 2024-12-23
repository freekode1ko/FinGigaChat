FROM node:18-alpine AS frontend-build

WORKDIR /code

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build
