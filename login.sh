#!/bin/bash

USER=${1:-guest}

ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $USER@localhost -p 10022
