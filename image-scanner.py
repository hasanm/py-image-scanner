import gi
import os
import shutil
from pathlib import Path

import cv2 as cv2
import numpy as np

from matplotlib import pyplot as plt

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository.GdkPixbuf import InterpType
from gi.repository.GdkPixbuf import PixbufRotation
from gi.repository import GLib


def get_image_files():
    files = list(filter(lambda f: f.upper().endswith("JPG"),  [f for f in os.listdir('.') if os.path.isfile(f)]))
    files.sort()

    return files


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


def scale_pixbuf(pixbuf_in, ratio): 
    pixbuf_scaled = pixbuf_in.scale_simple(pixbuf_in.get_width()/ratio, 
                                           pixbuf_in.get_height()/ratio,
                                           InterpType.HYPER)
    return pixbuf_scaled


def adjust_gamma(image, gamma=1.0):
        # build a lookup table mapping the pixel values [0, 255] to
        # their adjusted gamma values
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
                for i in np.arange(0, 256)]).astype("uint8")

        # apply gamma correction using the lookup table
        return cv2.LUT(image, table)


class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Hello World")

        self.image_files = get_image_files()
        self.l = len(self.image_files)
        self.current_index = -1
        self.current_image = None


        self.tmp_dir = "./tmp_output"
        self.current_format = "jpeg"
        self.dirpath = Path(self.tmp_dir)
        if self.dirpath.exists() and self.dirpath.is_dir():
            shutil.rmtree(self.dirpath)
        self.dirpath.mkdir()        

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
        button.connect("clicked", self.on_cut)
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

        event_box.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        event_box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)        

        event_box.connect("button-press-event", self.on_pressed)
        event_box.connect("motion-notify-event", self.on_tracking)
        self.tracking = False
        self.starting_x = 0
        self.starting_y = 0
        self.ending_x = 0
        self.ending_y = 0


        self.drawing_area.connect("draw", self.on_draw)
        
        self.add(main_panel)

    def on_pressed(self, widget, event):
        self.tracking = not self.tracking        
        if self.tracking:
            self.starting_x = event.x
            self.starting_y = event.y
            self.ending_x = event.x
            self.ending_y = event.y

        print (event.x, event.y)
        self.drawing_area.queue_draw()


    def on_tracking(self, widget, event):
        if self.tracking:
            self.ending_x = event.x
            self.ending_y = event.y
            self.drawing_area.queue_draw()

    def on_draw(self, widget, context):
        context.set_source_rgba(0.0, 0.7, 0.0, 0.2)
        context.set_line_width(10)
        context.move_to(self.starting_x, self.starting_y)
        context.line_to(self.ending_x, self.ending_y)
        context.stroke()

    def on_cut(self, widget):
        src_x = int(min(self.starting_x, self.ending_x))
        src_y = int(min(self.starting_y, self.ending_y))

        width = int(abs (self.ending_x - self.starting_x))
        height = int(abs(self.ending_y - self.starting_y))

        end_x = src_x + width
        end_y = src_y + height

        # self.pixbuf_copy = Pixbuf.new_subpixbuf(self.pixbuf_copy,
        #                                                 src_x, src_y,
        #                                                 width, height)

        self.img = self.img[src_y:src_y+height,
                            src_x:src_x+width]

        orig_x = int(src_x / self.ratio)
        orig_y = int(src_y / self.ratio)

        orig_end_x = int(end_x / self.ratio)
        orig_end_y = int(end_y / self.ratio)

        self.img_src = self.img_src [orig_y:orig_end_y,
                                      orig_x: orig_end_x]

        self.pixbuf_copy = cv_to_pixbuf(self.img)        


        self.starting_x = 0
        self.starting_y = 0
        self.ending_x = 0
        self.ending_y = 0
        self.tracking = False
        self.update_image()


    def on_button_clicked(self, widget):
        print("Hello World")


    def on_load(self, widget):
        self.current_index = (self.current_index + 1) % self.l
        self.current_image = self.image_files[self.current_index]
        self.ratio = .20
        
        self.img_src = cv2.imread(self.current_image,1)

        self.img = cv_resize(self.img_src, self.ratio)
        
        self.pixbuf_source = cv_to_pixbuf(self.img)
        # self.pixbuf_scaled = scale_pixbuf(self.pixbuf_source, self.ratio)

        image = Gtk.Image.new_from_pixbuf(self.pixbuf_source)

        if self.frame_left.get_child() is not None:
            self.frame_left.remove(self.frame_left.get_child())
        self.frame_left.add(image)

        self.do_copy()

        self.content_panel.show_all()

    def do_copy(self):
        print ("Copying")
        self.img = cv_resize(self.img_src, self.ratio)
        self.pixbuf_copy = cv_to_pixbuf(self.img)
        self.update_image()

    def on_copy(self, widget):
        self.do_copy()

    def update_image(self):
        image = Gtk.Image.new_from_pixbuf(self.pixbuf_copy)

        if self.overlay.get_child() is not None:
            self.overlay.remove(self.overlay.get_child())
        self.overlay.add(image)

        self.content_panel.show_all()


    def on_rotate(self, widget):
        self.pixbuf_copy   = self.pixbuf_copy.rotate_simple(PixbufRotation.CLOCKWISE)
        self.pixbuf_source = self.pixbuf_source.rotate_simple(PixbufRotation.CLOCKWISE)
        self.update_image()

    def on_save(self, widget):
        # if self.pixbuf_copy is not None:
        #     self.pixbuf_copy.savev(self.dirpath.joinpath(self.current_image), self.current_format, [] , [] )

        if self.img_src is not None:
            img = cv2.cvtColor(self.img_src, cv2.COLOR_BGR2GRAY)
            # img = self.img_src
            # img = cv_resize(self.img_src, .50)
            ## Gamma Correction
            img = adjust_gamma(img, 0.2)

            cv2.imwrite(str(self.dirpath.joinpath(self.current_image)), img)

    def on_cv(self, widget):
        self.img = normalize(self.img)
        self.img_src = normalize(self.img_src)

        self.pixbuf_copy = cv_to_pixbuf(self.img)
        self.update_image()


def normalize(img):
    rgb_planes = cv2.split(img)

    result_norm_planes = []

    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

        result_norm_planes.append(norm_img)

    result_norm = cv2.merge(result_norm_planes)
    return result_norm
        
        



win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.set_border_width(10)
win.set_default_size(1024, 768)
win.show_all()
Gtk.main()
