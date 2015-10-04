CC=gcc
CSTD=c99
CCFLAGS=-Wall -Werror -pedantic

DATA_DIRS=/data/cask/group /data/cask/container /data/cask/pid

BUILD_DIR=build
CLONE_TARGET=$(BUILD_DIR)/cask-clone
CLONE_SRC=$(wildcard src/cask-clone/*.c)

$(CLONE_TARGET): $(BUILD_DIR) $(CLONE_SRC)
	$(CC) --std=$(CSTD) -o $(CLONE_TARGET) $(CLONE_SRC) $(CCFLAGS)

libcask:
	python setup.py install

install: $(CLONE_TARGET) libcask $(DATA_DIRS)
	cp $(CLONE_TARGET) /usr/local/bin

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(DATA_DIRS):
	mkdir -p $(DATA_DIRS)

clean:
	rm -fr $(BUILD_DIR)

.PHONY: libcask install clean
