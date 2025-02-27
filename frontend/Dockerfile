FROM node:latest

WORKDIR /app

COPY /frontend .

RUN npm install typescript --save-dev

RUN npm install

# Typecheck app
RUN npx tsc -b

CMD ["npm", "start", "--", "--host", "0.0.0.0"]
