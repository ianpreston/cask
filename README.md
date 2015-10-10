# cask

Cask is a Linux container system, like Docker and LXC. Cask creates lightweight isolated environments in which to run programs. Programs running in a container have their own isolated filesystem, network, etc. Cask containers are not VMs, though -- they share the host's kernel.

Under the hood, Cask works like Docker's native driver: by using `clone()` to create a new set of [kernel namespaces](http://man7.org/linux/man-pages/man7/namespaces.7.html).

**Never use containers to run untrusted code!** If you wouldn't run it on the host, don't run it in Cask.

## Getting Started

Create a new container with a default filesystem:

    $ sudo cask create --default example

Then start it up:

    $ sudo cask start example

Once the container is running, you can open a shell into it like so:

    $ sudo cask shell example

For additional usage details, see the help text:

    $ cask --help

## Installation

First, install Cask's dependencies. On a recent Ubuntu, dependencies can be installed like so:
 
    $ sudo apt-get install python2.7 python-setuptools build-essential curl

Clone the latest stable release of Cask:

    $ git clone https://github.com/ianpreston/cask
    $ cd cask

Build and install all of the components:

    $ make
    $ sudo make install
    $ sudo make network

