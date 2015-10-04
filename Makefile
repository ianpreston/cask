CC=gcc
CSTD=c99
CCFLAGS=-Wall -Werror -pedantic

BUILD_DIR=build
CLONE_TARGET=$(BUILD_DIR)/cask-clone
CLONE_SRC=$(wildcard src/cask-clone/*.c)

$(CLONE_TARGET): $(BUILD_DIR) $(CLONE_SRC)
	$(CC) --std=$(CSTD) -o $(CLONE_TARGET) $(CLONE_SRC) $(CCFLAGS)

libcask:
	python setup.py install

install: $(CLONE_TARGET) libcask
	cp $(CLONE_TARGET) /usr/local/bin

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	rm -fr $(BUILD_DIR)

.PHONY: libcask install clean
