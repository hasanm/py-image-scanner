import gi

import cv2 as cv2
import numpy as np

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository.GdkPixbuf import InterpType
from gi.repository.GdkPixbuf import PixbufRotation
from gi.repository import GLib


def cv_to_pixbuf(img):
    img_rgb =  cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print ("Loading image: " , img.shape)
    print("Depth : ", img.dtype.itemsize, img.strides)
    height, width,depth = img.shape
    r_s, c_s, d_s = img.strides
    pixbuf = Pixbuf.new_from_data(img_rgb.tobytes(),
                                  GdkPixbuf.Colorspace.RGB,
                                  False,
                                  img.dtype.itemsize * 8,
                                  width,
                                  height,
                                  r_s)
    return pixbuf


def scale_pixbuf(pixbuf_in, ratio): 
    pixbuf_scaled = pixbuf_in.scale_simple(pixbuf_in.get_width()/ratio, 
                                           pixbuf_in.get_height()/ratio,
                                           InterpType.HYPER)
    return pixbuf_scaled


class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Hello World")



        main_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        top_panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.content_panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        main_panel.pack_start(top_panel, False, False, 0)
        main_panel.pack_start(self.content_panel, False, False, 0)


        button = Gtk.Button(label="Load")
        button.connect("clicked", self.on_load)
        top_panel.pack_start(button, False, False, 0)

        button = Gtk.Button(label="Copy")
        button.connect("clicked", self.on_copy)
        top_panel.pack_start(button, False, False, 0)

        button = Gtk.Button(label="Rotate")
        button.connect("clicked", self.on_rotate)
        top_panel.pack_start(button, False, False, 0)

        button = Gtk.Button(label="Cut")
        button.connect("clicked", self.on_button_clicked)
        top_panel.pack_start(button, False, False, 0)

        button = Gtk.Button(label="CV")
        button.connect("clicked", self.on_cv)
        top_panel.pack_start(button, False, False, 0)        

        button = Gtk.Button(label="Save")
        button.connect("clicked", self.on_save)
        top_panel.pack_start(button, False, False, 0)        

        self.frame_left = Gtk.Frame(label="Left")
        self.content_panel.pack_start(self.frame_left, False, False, 0)

        frame = Gtk.Frame(label = "Right")
        self.content_panel.pack_start(frame, False, False, 0)

        self.overlay = Gtk.Overlay()
        frame.add(self.overlay)
        event_box = Gtk.EventBox()
        self.overlay.add_overlay(event_box)

        self.drawing_area = Gtk.DrawingArea()
        event_box.add(self.drawing_area)


        self.add(main_panel)
        

    def on_button_clicked(self, widget):
        print("Hello World")

    def on_load(self, widget):
        self.ratio = 5
        # self.pixbuf_source = Pixbuf.new_from_file("IMG_1.JPG")
        
        self.img = cv2.imread('IMG_1.JPG',1)
        self.pixbuf_source = cv_to_pixbuf(self.img)
        self.pixbuf_scaled = scale_pixbuf(self.pixbuf_source, self.ratio)

        image = Gtk.Image.new_from_pixbuf(self.pixbuf_scaled)

        if self.frame_left.get_child() is not None:
            self.frame_left.remove(self.frame_left.get_child())
        self.frame_left.add(image)

        self.content_panel.show_all()


    def update_image(self):
        image = Gtk.Image.new_from_pixbuf(self.pixbuf_copy)

        if self.overlay.get_child() is not None:
            self.overlay.remove(self.overlay.get_child())
        self.overlay.add(image)

        self.content_panel.show_all()                


    def on_copy(self, widget):
        self.pixbuf_copy = self.pixbuf_scaled.copy()
        self.update_image()


    def on_rotate(self, widget):
        self.pixbuf_copy   = self.pixbuf_copy.rotate_simple(PixbufRotation.CLOCKWISE)
        self.pixbuf_source = self.pixbuf_source.rotate_simple(PixbufRotation.CLOCKWISE)
        self.update_image()

    def on_save(self, widget):
        if self.pixbuf_source is not None:
            self.pixbuf_source.savev("output.jpg", "jpeg", [] , [] )


    def on_cv(self, widget):
        rgb_planes = cv2.split(self.img)

        result_planes = []
        result_norm_planes = []

        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_planes.append(diff_img)
            result_norm_planes.append(norm_img)

        result = cv2.merge(result_planes)
        result_norm = cv2.merge(result_norm_planes)

        self.img = result
        
        self.pixbuf_source = cv_to_pixbuf(self.img)
        self.pixbuf_scaled = scale_pixbuf(self.pixbuf_source, self.ratio)
        self.pixbuf_copy = self.pixbuf_scaled.copy()        
        self.update_image()

        
        



win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.set_border_width(10)
win.set_default_size(1024, 768)
win.show_all()
Gtk.main()
