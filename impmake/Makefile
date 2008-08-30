all: impmake.exe

impmake.exe: impmake.o disphelper.o
	gcc -s -o impmake impmake.o disphelper.o -lole32 -loleaut32 -luuid

impmake.o: src/impmake.c src/version.h disphelper.o
	gcc -O2 -Wall -c -o impmake.o src/impmake.c

disphelper.o: src/disphelper.c src/disphelper.h
	gcc -O2 -w    -c -o disphelper.o src/disphelper.c

clean:
	rm -f *.o *.exe

distclean:
	rm -f *.o *.exe src/version.h
