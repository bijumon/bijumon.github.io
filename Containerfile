FROM node:26-alpine

WORKDIR /site

# Install deps first so this layer is cached unless package.json changes
COPY package.json package-lock.json* ./
RUN npm install

# Bring in the rest of the project (overridden by the bind mount at runtime,
# but useful if the image is ever run standalone without volumes)
COPY . .
