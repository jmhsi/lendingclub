# Anaconda3 base image
FROM continuumio/anaconda3

# Update?, install tmux
RUN apt-get update \
    && apt-get install -y tmux

# Pip installs
RUN pip install dvc

# add a user called ubuntu for all subsequent layers
RUN adduser --disabled-password --gecos '' ubuntu \
    && adduser ubuntu sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 

USER ubuntu
WORKDIR /home/ubuntu

#RUN which python

# Clone the lendingclub repo
RUN git clone --branch master https://github.com/jmhsi/lendingclub.git \
    && cd lendingclub \
    && git pull

# Expose port for jupyter notebook
EXPOSE 3224 

ADD .bashrc /home/ubuntu/

#CMD ["jupyter", "notebook", "--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]
#CMD ['/bin/bash', "cd]
#ADD hello.py /home/ubuntu/
