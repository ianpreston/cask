# cask

Cask is a Linux container management tool, like Docker. With Cask, you create lightweight "containers" (which are actually just directories). These containers run in their own set of [kernel namespaces](http://man7.org/linux/man-pages/man7/namespaces.7.html), effectively isolated from the rest of the system and from eachother.

Like Docker's native driver, Cask essentially works by calling `clone()` to create a new set of namespaces for your process.

**Cask is not designed for running untrusted code.** If you wouldn't run it as root, don't run it in a Cask container!

## Usage

Grab the source and build

    $ git clone https://github.com/ianpreston/cask
    $ cd cask
    $ make

Create an example container with Busybox

    $ make container

Start up the container

    $ sudo ./cask ./containers/example /busybox sh
    /# /busybox hostname


## License

(c) 2015 Ian Preston. Available under the [MIT License](https://opensource.org/licenses/MIT).
