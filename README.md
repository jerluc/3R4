3R4
===

Super secret game

# Development

### Developing the 3R4 shell

The project is like any other setuptools/distutils Python project. Just
run:

```bash
python setup.py install
```

or

```bash
pip install --editable .
```

to install the development build.

### Developing the Docker image

I've included a few helper scripts that should allow you to develop
against the Docker image with ease:

```bash
# Rebuilds the Docker image
./build.sh

# Runs the Docker image (basically just an SSH server with the 3R4 shell
# installed)
./run.sh

# SSHes into the running Docker container (by default, using the
# 'guest' user; this can be changed by using a different user name as
# the script argument)
./login.sh

# Shuts down the running container and cleans up the image fork
./stop.sh
```

# Usage

For now, you can only enter the shell if running locally:

```bash
3R4
```

To run the Docker container, use the instructions above
