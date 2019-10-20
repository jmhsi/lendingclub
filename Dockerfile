FROM continuumio/anaconda3

#RUN apt-get update
#RUN apt-get -y install sudo
#RUN apt-get -y install python

RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN mkdir /home/ubuntu/lendingclub

#RUN sudo apt-get update 
USER ubuntu

#ADD hello.py /home/ubuntu/
#ADD .bashrc /home/ubuntu/
