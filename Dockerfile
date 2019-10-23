# Anaconda3 base image
FROM continuumio/anaconda3

# Update?, install tmux and sudo
RUN apt-get update \
    && apt-get install -y tmux nano 

# Pip installs
RUN pip install dvc

# add a user called ubuntu for all subsequent layers
RUN adduser --disabled-password --gecos '' ubuntu \
    && adduser ubuntu sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 

USER ubuntu
WORKDIR /home/ubuntu

# Install j_utils
ADD https://api.github.com/repos/jmhsi/j_utils/git/refs/heads/master j_utils_version.json
RUN git clone https://github.com/jmhsi/j_utils.git

# Run below uses github api to make sure docker build doesn't use cached version of git cloned repo
ADD https://api.github.com/repos/jmhsi/lendingclub/git/refs/heads/master lendingclub_version.json

# Clone the lendingclub repo
RUN git clone https://github.com/jmhsi/lendingclub.git \
    && cd lendingclub \
    && git pull

# Expose port for jupyter notebook
EXPOSE 3224 

ADD .bashrc /home/ubuntu/

#CMD ["jupyter", "notebook", "--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]
#CMD ['/bin/bash', "cd]
#ADD hello.py /home/ubuntu/
