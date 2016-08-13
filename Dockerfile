FROM gentoo/stage3-amd64:latest
MAINTAINER jerluc <me@jerluc.com>

# Note that I'm fairly sure RUN commands are cached in the order they
# come up, so it makes sense to put the longest-running tasks (which
# change relatively infrequently) higher up in the chain than other
# shorter tasks or tasks that change all the time


### BEGIN packages ###
    # Update Portage + install packages
    RUN emerge-webrsync
    RUN emerge -v vim
    RUN emerge -v openssh
    RUN emerge -v dev-python/pip

    # Set up sshd
    RUN /usr/bin/ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key -N ""
    RUN /usr/bin/ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ""
    # SSH login fix. Otherwise user is kicked off after login
    RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

    # Setup esh/esh-login
    WORKDIR /tmp
    WORKDIR 3R4
    ADD . .
    RUN pip install .
    RUN cp /usr/bin/esh* /bin/
    RUN echo "/bin/esh" >> /etc/shells
    RUN echo "/bin/esh-login" >> /etc/shells

    # Clean up /tmp
    WORKDIR /tmp
    RUN rm -rf *

    # Reset the working directory to the root
    WORKDIR /
### END packages ###


### BEGIN users ###
    # Change root password to something super secret
    RUN echo 'root:n3w3r4' | chpasswd

    # Setup dev user (bash)
    RUN useradd -m -s /bin/bash dev
    RUN echo 'dev:n3w3r4' | chpasswd

    # Setup guest user (3R4)
    RUN useradd -m -s /bin/esh-login guest
    RUN echo 'guest:n3w3r4' | chpasswd
### END users ###


### BEGIN external ###
    # Expose port 22 for sshd
    EXPOSE 22
### END external ###


### BEGIN commands ###
    # Run sshd on start-up
    CMD ["/usr/sbin/sshd", "-D"]
### END commands ###

