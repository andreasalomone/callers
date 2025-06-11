# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application's source code from the host to the container
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# The command to start the app in development mode
CMD ["npm", "run", "dev"] 