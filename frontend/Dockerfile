FROM node:22-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

ENV NODE_ENV=development
ENV PORT=3005

EXPOSE 3005

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3005"]
