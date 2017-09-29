FROM alpine:3.6
MAINTAINER jerluc <me@jerluc.com>

### BEGIN packages ###
    RUN apk update

    # App deps
    RUN apk add --no-cache \
        ca-certificates \
        curl \
        wget \
        zip \
        bash \
        python2 \
        python2-dev \
        py2-pip \
        zlib-dev

    # SSH deps
    RUN apk add --no-cache \
        openrc \
        openssh

    # Set up sshd
    RUN rc-update add sshd
    RUN ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key -N ""
    RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ""
### END packages ###


### BEGIN shells ###
    # Setup initial user
    RUN yes "n3w3r4" | adduser -s /bin/esh-login doorstop
### END users ###


### BEGIN esh ###
    ADD . /3R4

    RUN pip install /3R4
    RUN cp /usr/bin/esh* /bin/
    RUN echo "/bin/esh" >> /etc/shells
    RUN echo "/bin/esh-login" >> /etc/shells

    RUN rm -rf /3R4
###


### BEGIN external ###
    # Expose port 22 for sshd
    EXPOSE 22
### END external ###


### BEGIN commands ###
    # Run sshd on start-up
    CMD ["/usr/sbin/sshd", "-D"]
### END commands ###
