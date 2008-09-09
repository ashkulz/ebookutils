CC = gcc

all: impbuild.exe

impbuild.exe: impbuild.o disphelper.o
	$(CC) -s -o impbuild.exe impbuild.o disphelper.o -lole32 -loleaut32 -luuid

impbuild.o: src/impbuild.c src/version.h disphelper.o
	$(CC) -O2 -Wall -c -o impbuild.o src/impbuild.c

disphelper.o: src/disphelper.c src/disphelper.h
	$(CC) -O2 -w    -c -o disphelper.o src/disphelper.c

clean:
	rm -f *.o *.exe
