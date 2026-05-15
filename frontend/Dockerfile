# Step 1: Build the Vue application
FROM node:18-slim AS build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
# You can pass VITE_API_BASE_URL during build if needed
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Step 2: Serve the application with Nginx
FROM nginx:stable-alpine AS production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html
# Copy custom nginx config if you have one, or use default
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
