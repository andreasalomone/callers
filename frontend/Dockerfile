# Stage 1: Builder
# Use an official Node.js runtime as a parent image for the build environment
FROM node:18-alpine AS builder

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies, but skip downloading the Cypress binary
RUN CYPRESS_INSTALL_BINARY=0 npm install

# Copy the rest of the application's source code
COPY . .

# Build the Next.js application for production
RUN npm run build

# Stage 2: Production
# Use a minimal Node.js image for the final production environment
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy the standalone output from the builder stage
# This includes the Next.js server and all necessary node_modules
COPY --from=builder /app/.next/standalone .

# Expose the port the app runs on
EXPOSE 3000

# The command to start the app in production mode
# The server is located at server.js in the standalone output directory
CMD ["node", "server.js"] 