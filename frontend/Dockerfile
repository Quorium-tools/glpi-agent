FROM node:22-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ENV NODE_ENV=development
ENV PORT=3003

EXPOSE 3003

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3003"]
