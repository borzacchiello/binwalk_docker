FROM ubuntu:22.10

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
    build-essential \
    sudo \
    nano \
    wget \
    curl \
    git \
    python3 \
    python3-pip \
    python-is-python3 \
    mtd-utils \
    gzip \
    bzip2 \
    tar \
    arj \
    lhasa \
    p7zip \
    p7zip-full \
    cabextract \
    cramfsswap \
    squashfs-tools \
    sleuthkit \
    default-jdk \
    lzop \
    srecord \
    zlib1g-dev \
    liblzma-dev \
    liblzo2-dev \
    python3-lzo \
    python3-opengl \
    python3-numpy \
    python3-scipy

RUN pip install \
    nose \
    coverage \
    pycryptodome \
    capstone \
    cstruct

# Install cramfsprogs
RUN \
    cd /opt && \
    git clone https://github.com/davidribyrne/cramfs --depth 1 && \
    cd cramfs && \
    make && \
    cp cramfsck mkcramfs /usr/local/bin/

# Install sasquatch to extract non-standard SquashFS images
RUN \
    cd /opt && \
    git clone https://github.com/devttys0/sasquatch --depth 1 && \
    cd sasquatch && \
    wget https://downloads.sourceforge.net/project/squashfs/squashfs/squashfs4.3/squashfs4.3.tar.gz && \
    tar -zxvf squashfs4.3.tar.gz && \
    cd squashfs4.3 && \
    patch -p0 < ../patches/patch0.txt && \
    cd squashfs-tools && \
    sed -i 's/-Wall//g' Makefile && \
    sed -i 's/int verbose;/extern int verbose;/g' error.h && \
    sed -i '1 i\int verbose;' unsquashfs.c && \
    make && \
    make install

# Install jefferson to extract JFFS2 file systems
RUN \
    cd /opt && \
    git clone https://github.com/sviehb/jefferson --depth 1 && \
    cd jefferson && \
    python setup.py install

# Install ubi_reader to extract UBIFS file systems
RUN \
    cd /opt && \
    git clone https://github.com/jrspruitt/ubi_reader --depth 1 && \
    cd ubi_reader && \
    python setup.py install

# Install yaffshiv to extract YAFFS file systems
RUN \
    cd /opt && \
    git clone https://github.com/devttys0/yaffshiv --depth 1 && \
    cd yaffshiv && \
    python setup.py install

# Install binwalk
RUN \
    cd /opt && \
    git clone https://github.com/ReFirmLabs/binwalk.git --depth 1 && \
    cd binwalk && \
    python setup.py install

# Cleanup
RUN apt clean
RUN rm -rf /var/lib/apt/lists/*

# Create User
RUN groupadd --gid 1000 ubuntu \
    && useradd --uid 1000 --gid ubuntu --shell /bin/bash --create-home ubuntu
RUN echo "ubuntu ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu && \
    chmod 0440 /etc/sudoers.d/ubuntu

USER    ubuntu
WORKDIR /home/ubuntu
