FROM python:3.7-slim-stretch

# update apk repo
#RUN echo "http://dl-4.alpinelinux.org/alpine/v3.7/main" >> /etc/apk/repositories && \
#    echo "http://dl-4.alpinelinux.org/alpine/v3.7/community" >> /etc/apk/repositories

# install chromedriver
#RUN apk update
#RUN apk add chromium chromium-chromedriver
RUN apt-get update
RUN apt-get -y install wget
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
#RUN echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y install google-chrome-stable

# install python modules
RUN pip install -r requirements.txt