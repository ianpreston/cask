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

.PHONY: build container clean
