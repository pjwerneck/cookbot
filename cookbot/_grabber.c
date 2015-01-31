#include <stdio.h>
#include <X11/X.h>
#include <X11/Xlib.h>

void get_screen(const int, const int, const int, const int, unsigned char *);
void get_screen(const int xx,const int yy,const int W, const int H, /*out*/ unsigned char * data)
{
   Display *display = XOpenDisplay(NULL);
   Window root = DefaultRootWindow(display);

   XFlush(display);

   // for some reason, it's faster to capture the whole screen and
   // crop the window than to capture the window
   XImage *image = XGetImage(display, root, 0, 0, 1920, 1080, AllPlanes, ZPixmap);

   unsigned long red_mask = image->red_mask;
   unsigned long green_mask = image->green_mask;
   unsigned long blue_mask = image->blue_mask;
   int x, y;
   for (x = 0; x < W; x++) {
      for (y = 0; y < H; y++) {
         unsigned long pixel = XGetPixel(image, xx+x, yy+y);
         int ii = (x + W * y) * 3;

         unsigned char blue  = (pixel & blue_mask);
         unsigned char green = (pixel & green_mask) >> 8;
         unsigned char red   = (pixel & red_mask) >> 16;

         data[ii + 2] = blue;
         data[ii + 1] = green;
         data[ii + 0] = red;
      }
   }

   XDestroyImage(image);
   XDestroyWindow(display, root);
   XCloseDisplay(display);
}

