# Docker Notes

Some helpful docker commands

## Run a container 

Docker containers can be run by running the basic command:

```sh
docker run <image>:<tag>
```

If no tag is specified it will use `latest` by default.

You can also run an image and over ride any `CMD` or `ENTRYPOINT` that the image supplies and run your own command instead.
Using `bash` or `sh` is very convenient for debugging containers that have problems (this is also called `exec`ing into the container, see below)
To do this, supply `-it` after `run` for interactive mode and add the command you want to run at the end of the run command.

```sh
docker run -it <image>:<tag> sh
```

Other useful run flags:

- `-u` Specify the user the container will run as, useful to run as root if needed.
- `-e` Sets an environment variable for the container
- `-v` Volume mount something into the container

## Getting Into An Existing Container

If a container is running, you can "exec" into it to look around and run things by using the `docker exec` command.
It works similar to running docker with interactive mode (`-it`) but it only works on running containers.

First, figure out what containers are running.
To do this run `docker ps`, you will get a response that looks like this


| CONTAINER ID 	| IMAGE         	| COMMAND                	| CREATED           	| STATUS           	| PORTS                                               	| NAMES        	|
|--------------	|---------------	|------------------------	|-------------------	|------------------	|-----------------------------------------------------	|--------------	|
| 7af7e1469cc1 	| <image>:<tag> 	| "container-entrypoin…" 	| About an hour ago 	| Up About an hour 	| 3000/tcp, 0.0.0.0:5000->5000/tcp, :::5000->5000/tcp 	| flask-server 	|

From here we can take the container ID and get into the container

```sh
docker exec -it 7af7e1469cc1 sh
```

This will drop the terminal into the running container and run `sh` as the shell.


