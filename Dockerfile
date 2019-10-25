# Anaconda3 base image
FROM continuumio/anaconda3

# Update?, install tmux nano gcc 
RUN apt-get update \
    && apt-get install -y tmux nano gcc 

# Pip installs
RUN pip install dvc pyarrow pause pandas_summary


# add a user called ubuntu for all subsequent layers
RUN adduser --disabled-password --gecos '' ubuntu \
    && adduser ubuntu sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 

USER ubuntu
WORKDIR /home/ubuntu
ADD .bashrc /home/ubuntu/



# Install j_utils
ADD https://api.github.com/repos/jmhsi/j_utils/git/refs/heads/master j_utils_version.json
RUN git clone https://github.com/jmhsi/j_utils.git \
    && cd j_utils \ 
    && pip install --user -e .

# Run below uses github api to make sure docker build doesn't use cached version of git cloned repo
ADD https://api.github.com/repos/jmhsi/lendingclub/git/refs/heads/master lendingclub_version.json

# Clone the lendingclub repo and cythonize inside csv_preparation, move cython to csv_prep dir
RUN git clone https://github.com/jmhsi/lendingclub.git \
#RUN git clone git@github.com:jmhsi/lendingclub.git \
    && cd lendingclub \
    && git pull \
    && pip install --user -e . \
    && cd lendingclub/csv_preparation \
    && python setup.py build_ext \
    && echo $(pwd) \
    && echo $(ls build/lib.linux-x86_64-3.7/lendingclub/csv_preparation) \
    && mv build/lib.linux-x86_64-3.7/lendingclub/csv_preparation/rem_to_be_paid.cpython-37m-x86_64-linux-gnu.so .


# Expose port for jupyter notebook
EXPOSE 3224 


#CMD ["jupyter", "notebook", "--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]
#CMD ['/bin/bash', "cd]
#ADD hello.py /home/ubuntu/
