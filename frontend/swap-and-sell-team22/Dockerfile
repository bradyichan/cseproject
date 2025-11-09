# Commands
# docker build -t team22frontend .  
# docker run -d -p 5173:5173 team22frontend
FROM node:20
WORKDIR /app
COPY package.json .
RUN npm i
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "dev"]