FROM node:20-slim
RUN npm install -g jest
WORKDIR /sandbox
