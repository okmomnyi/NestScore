FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY . .

ENV NEXT_PUBLIC_API_BASE_URL=http://164.92.173.167:8001
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
