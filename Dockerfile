FROM python:alpine3.7
RUN apk add --no-cache \
        --virtual=.build-dependencies \
        g++ gfortran file binutils \
        musl-dev python3-dev openblas-dev && \
    apk add libstdc++ openblas && \
    \
    ln -s locale.h /usr/include/xlocale.h && \
    \
    pip3 install numpy && \
    pip3 install boto3
ADD . /try
ENTRYPOINT [ "python3", "/try/s3Try.py"]

