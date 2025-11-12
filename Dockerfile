#DOCKERFILE!
#These are the commands I used:
#To build:
# docker build -t team22swapandsell .

#To run:
# docker run -p 6767:6767 team22swapandsell

#Use python
FROM python:3.9-slim

#set directory to be backend folder
WORKDIR /backend

#copy requirements
COPY backend/requirements.txt .

#install the necessary packages (for this, Flask, flasgger, and flask_cors)
RUN pip install --no-cache-dir -r requirements.txt

#copy the rest of the files
COPY backend/ ./backend

#expose port this will run on
EXPOSE 6767

#run app!
CMD ["python3", "-m", "backend.main"]