CC=gcc
CSTD=c99
CCFLAGS=-Wall -Werror -pedantic

TARGET=cask-clone
SRC=$(wildcard src/cask-clone/*.c)

build: $(TARGET)

$(TARGET): $(SRC)
	$(CC) --std=$(CSTD) -o $(TARGET) $(SRC) $(CCFLAGS)

clean:
	rm $(TARGET)

container: containers/example

containers/example:
	mkdir -p containers/example
	curl -o containers/example/busybox http://busybox.net/downloads/binaries/latest/busybox-i686
	chmod ug+x containers/example/busybox


.PHONY: build container clean
