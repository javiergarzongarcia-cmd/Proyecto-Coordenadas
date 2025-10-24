FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 5173
ENV VITE_API_URL=${VITE_API_URL}
CMD ["npm", "run", "dev", "--", "--host"]
