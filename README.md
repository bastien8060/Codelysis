# Codelysis

## Installation (x84_64)

Codelysis has a few dependencies needed in order to run. Codelysis depends on docker for example, as well as Python and many other Python modules. Codelysis was only designed to be hosted on a Linux platform, and will not work on Windows without a VM or Windows' WSL. 

On Linux - Ubuntu and Debian, you can install the dependencies like so:

```sh
$ sudo apt update && sudo apt install snapd
$ sudo snap install docker
$ pip3 install -r requirements.txt
```

This will make sure Docker gets installed. The command may varie between distros (On Archlinux, Docker is available through the AUR). Now time to clone the repository:
```sh
$ git clone https://github.com/bastien8060/Codelysis
```
You should now be up and running, except for a few details. You may need to set-up your system in order to run Docker images without a priviledged account which is recommended for security reasons. To set it up:

```sh
$ sudo usermod -a -G docker ${USER}
$ sudo chgrp docker /var/run/docker.sock
```
After this you might need to sign in and out (or just re-login):
```sh
$ su -s ${USER}
```

Lastly you might want to pre-install the docker image, in order for the first request to be quick, otherwise, it will be slow:

```sh
$ docker pull codelysis/linuxalpine
```

## Usage

You can now run `$ python3 ./main.py` to start the program and everything should work. If any problems, please open a GitHub issue.

Codelysis uses Google's Search API, which isn't totally free. To use this project, you will need to add an API key in the file `apiconfigs.py` to use this without limit. By kindness, I added an API keys (100 requests/day in total) from Google. You can also add an API from scaleserp.com which is supported. If no working keys were found, it will fallback to scraping Google Search results, which can get your ip banned by Google. 

Refer to this [wiki](https://github.com/bastien8060/Codelysis/wiki/Create-a-Google-Search-Api-key) to create a free Google Api Key.
