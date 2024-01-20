FROM node:18

WORKDIR /code/
COPY package*.json .
RUN npm install
COPY ./src ./src
COPY ./public ./public
EXPOSE 3000

CMD ["npm", "start"]
