# Anaconda3 base image
FROM continuumio/anaconda3

# Copied from nvidia docker to get gpus working ___________________________________
# get Cuda working https://gitlab.com/nvidia/container-images/cuda/blob/master/dist/ubuntu18.04/10.1/base/Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
gnupg2 curl ca-certificates && \
    curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64 /" > /etc/apt/sources.list.d/cuda.list && \
    echo "deb https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-get purge --autoremove -y curl && \
rm -rf /var/lib/apt/lists/*

ENV CUDA_VERSION 10.1.243

ENV CUDA_PKG_VERSION 10-1=$CUDA_VERSION-1

# For libraries in the cuda-compat-* package: https://docs.nvidia.com/cuda/eula/index.html#attachment-a
RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-cudart-$CUDA_PKG_VERSION \
    cuda-compat-10-1 && \
    ln -s cuda-10.1 /usr/local/cuda && \
    rm -rf /var/lib/apt/lists/*

# Required for nvidia-docker v1
RUN echo "/usr/local/nvidia/lib" >> /etc/ld.so.conf.d/nvidia.conf && \
    echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf

ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64

# nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_REQUIRE_CUDA "cuda>=10.1 brand=tesla,driver>=384,driver<385 brand=tesla,driver>=396,driver<397 brand=tesla,driver>=410,driver<411"

# Justin added for actual project ________________________________________________
# Update?, install tmux nano gcc
RUN apt-get update && \
    apt-get install -y tmux nano gcc 

# Pip installs from requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt 

# add a user called ubuntu for all subsequent layers
RUN adduser --disabled-password --gecos '' ubuntu && \
    adduser ubuntu sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 

USER ubuntu
WORKDIR /home/ubuntu
COPY .bashrc /home/ubuntu/

# Install j_utils
ADD https://api.github.com/repos/jmhsi/j_utils/git/refs/heads/master j_utils_version.json
RUN git clone https://github.com/jmhsi/j_utils.git && \
    cd j_utils && \ 
    pip install --user -e .

# Run below uses github api to make sure docker build doesn't use cached version of git cloned repo
ADD https://api.github.com/repos/jmhsi/lendingclub/git/refs/heads/master lendingclub_version.json

# Clone the lendingclub repo and cythonize inside csv_preparation, move cython to csv_prep dir
RUN git clone https://github.com/jmhsi/lendingclub.git && \
    cd lendingclub && \
    git pull && \
    pip install --user -e . && \
    cd lendingclub/csv_preparation && \
    python setup.py build_ext && \
    echo $(pwd) && \
    echo $(ls build/lib.linux-x86_64-3.7/lendingclub/csv_preparation) && \
    mv build/lib.linux-x86_64-3.7/lendingclub/csv_preparation/rem_to_be_paid.cpython-37m-x86_64-linux-gnu.so .

# Expose port for jupyter notebook
EXPOSE 3224 


#CMD ["jupyter", "notebook", "--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]
#CMD ['/bin/bash', "cd]
#ADD hello.py /home/ubuntu/
