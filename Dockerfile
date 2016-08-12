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

    # Set up sshd
    RUN /usr/bin/ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key -N ""
    RUN /usr/bin/ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ""
    # SSH login fix. Otherwise user is kicked off after login
    RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

    # Re-root everything to /tmp
    WORKDIR /tmp

    # Setup 3R4 shell
    WORKDIR 3R4
    ADD . .
    RUN python setup.py install
    RUN echo "/usr/bin/3R4" >> /etc/shells

    # Clean up our temporary datas
    RUN rm -rf /tmp/*

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
    RUN useradd -m -s /usr/bin/3R4 guest
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

