# cask

Cask is a Linux container management tool, like Docker. With Cask, you create lightweight "containers" (which are actually just directories). These containers run in their own set of [kernel namespaces](http://man7.org/linux/man-pages/man7/namespaces.7.html), effectively isolated from the rest of the system and from eachother.

Like Docker's native driver, Cask essentially works by calling `clone()` to create a new set of namespaces for your process.

**Cask is not designed for running untrusted code.** If you wouldn't run it as root, don't run it in a Cask container!

## Usage

Start up an existing container:

    $ sudo cask start example

Attach a shell to that container and run a listen server:

    $ sudo cask shell example
    / # nc -l -p 1234

## Installation

Make sure you have all the dependencies installed. You'll need a recent version of python, make, curl, and gcc. On Ubuntu you can install all dependencies like this:

    $ sudo apt-get install python2.7 python-setuptools build-essential curl

First, grab the source from Github. Master branch is considered stable.

    $ git clone https://github.com/ianpreston/cask
    $ cd cask

Build the binary and install. This part usually takes a few hundred milliseconds.

    $ make
    $ sudo make install

## License

(c) 2015 Ian Preston. Available under the [MIT License](https://opensource.org/licenses/MIT).
