FROM continuumio/anaconda3

#RUN apt-get update

RUN adduser --disabled-password --gecos '' ubuntu \
    && adduser ubuntu sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 

USER ubuntu

WORKDIR /home/ubuntu

RUN git clone https://github.com/jmhsi/lendingclub.git \
    && cd lendingclub \
    && git pull

CMD ['/bin/bash']
#ADD hello.py /home/ubuntu/
#ADD .bashrc /home/ubuntu/
