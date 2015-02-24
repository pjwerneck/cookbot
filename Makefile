
all:
	gcc -shared -O3 -fPIC -Wl,-soname,_grabber -o cookbot/_grabber.so cookbot/_grabber.c -lX11