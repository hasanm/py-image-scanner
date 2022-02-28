import cv2 as cv2
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf

def cv_to_pixbuf(img):
    img_rgb =  cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print ("Loading image: " , img.shape)
    print("Depth : ", img.dtype.itemsize, img.strides)
    height, width,depth = img.shape
    pixbuf = Pixbuf.new_from_data(img_rgb.tobytes(),
                                  GdkPixbuf.Colorspace.RGB,
                                  False,
                                  img.dtype.itemsize * 8,
                                  width,
                                  height,
                                  width * 3)
    return pixbuf

def cv_resize(img, ratio):
    w, h,d  = img.shape
    width = int(w * ratio)
    height = int (h * ratio)
    dim = (height, width)

    print ("ratio " , ratio)
    print ("resizing from " , img.shape, " => " , dim)
    resized = cv2.resize(img, None, fx=ratio, fy=ratio , interpolation = cv2.INTER_AREA)
    return resized
