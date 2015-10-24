CC=gcc
CSTD=c99
CCFLAGS=-Wall -Werror -pedantic

DATA_DIRS=/data/cask/group /data/cask/container /data/cask/image /data/cask/pid /data/cask/log

BUILD_DIR=build
CLONE_TARGET=$(BUILD_DIR)/cask-clone
CLONE_SRC=$(wildcard src/cask-clone/*.c)

BRIDGE_NAME=cask0
BRIDGE_NETWORK=10.18.66.0/24

$(CLONE_TARGET): $(BUILD_DIR) $(CLONE_SRC)
	$(CC) --std=$(CSTD) -o $(CLONE_TARGET) $(CLONE_SRC) $(CCFLAGS)

libcask:
	python setup.py install

network:
	ip link add name $(BRIDGE_NAME) type bridge
	ip link set $(BRIDGE_NAME) up
	ip route add $(BRIDGE_NETWORK) dev $(BRIDGE_NAME) proto kernel scope link

install: $(CLONE_TARGET) libcask $(DATA_DIRS)
	cp $(CLONE_TARGET) /usr/local/bin

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(DATA_DIRS):
	mkdir -p $(DATA_DIRS)

clean:
	rm -fr $(BUILD_DIR)

clean-network:
	ip link del cask0

.PHONY: libcask install network clean clean-network
