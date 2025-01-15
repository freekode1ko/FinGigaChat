# Frontend Build Stage
FROM node:18-alpine AS frontend-build

WORKDIR /code

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# Nginx Stage
FROM nginx:latest

COPY --from=frontend-build /code/dist /usr/share/nginx/html
