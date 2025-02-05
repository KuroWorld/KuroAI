# Use Node.js LTS version
FROM node:18-alpine

# Add labels for better maintainability
LABEL maintainer="KuroAI Team"
LABEL description="Frontend development environment for KuroAI"

# Set working directory
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy package files first for dependency caching
COPY package.json pnpm-lock.yaml ./

# Install dependencies using pnpm
RUN pnpm install

# Copy the rest of the source code
COPY . .

# Set environment variables
ENV NODE_ENV=development
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Expose the development port
EXPOSE 3000

# Start Next.js in development mode
CMD ["pnpm", "run", "dev"]
