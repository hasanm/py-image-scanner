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

from image_utils import cv_resize
from image_utils import cv_to_pixbuf

class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Hello World")
        self.current_image = None
        self.img_src = None
        
        self.ratio = 1.0

        root_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        top_panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.content_panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        root_panel.pack_start(top_panel, False, False, 0)
        root_panel.pack_start(self.content_panel, False, False, 0)

        button = Gtk.Button(label="Load")
        button.connect("clicked", self.on_load)
        top_panel.pack_start(button, False, False, 0)

        self.add(root_panel)

    def on_load(self, widget):
        self.current_image = "/home/p-hasan/work/math4310/hw3/out/IMG_1133.JPG"
        self.img_src = cv2.imread(self.current_image,1)
        self.ratio = .20

        self.img = cv_resize(self.img_src, self.ratio)



win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.set_border_width(10)
win.set_default_size(1024, 768)
win.show_all()
Gtk.main()
