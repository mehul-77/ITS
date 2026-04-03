FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy frontend code
COPY frontend/ .

# Expose port
EXPOSE 3000

# Run dev server
CMD ["npm", "run", "dev"]
