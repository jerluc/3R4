#!/bin/bash

docker build --force-rm -t era .

# TODO: Is this really okay in all cases?
# It's supposed to remove all "dangling" images
docker rmi $(docker images -f "dangling=true" -q)
