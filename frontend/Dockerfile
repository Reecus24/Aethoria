FROM node:20-alpine

WORKDIR /app

# Install serve globally
RUN yarn global add serve

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source
COPY . .

# Build for production
ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
RUN yarn build

# Expose port
EXPOSE 3000

# Serve build
CMD ["serve", "-s", "build", "-l", "3000"]
