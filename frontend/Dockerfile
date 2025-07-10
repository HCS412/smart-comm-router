# Use official Node.js image as base
FROM node:16

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy frontend code
COPY . .

# Expose port for React development server
EXPOSE 3000

# Run React development server
CMD ["npm", "start"]
