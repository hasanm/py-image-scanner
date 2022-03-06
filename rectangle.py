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

    up_key = Gdk.KEY_i
    down_key = Gdk.KEY_k
    left_key = Gdk.KEY_j
    right_key = Gdk.KEY_l

    increase_key = Gdk.KEY_u
    decrease_key = Gdk.KEY_o
    
    def __init__(self):
        super().__init__(title="Hello World")
        self.current_image = None
        self.img_src = None
        self.img = None
        self.pixbuf = None
        self.image = None
        self.tracking = False
        self.x = 0
        self.y = 0
        
        self.ratio = 1.0

        self.width = 100

        self.draw_width = 100
        self.draw_height = 100

        root_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        top_panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.content_panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        root_panel.pack_start(top_panel, False, False, 0)
        root_panel.pack_start(self.content_panel, False, False, 0)

        button = Gtk.Button(label="Load")
        button.connect("clicked", self.on_load)
        top_panel.pack_start(button, False, False, 0)

        self.frame = Gtk.Frame(label="Image")
        self.content_panel.add(self.frame)
        self.overlay = Gtk.Overlay()        
        self.frame.add(self.overlay)
        self.event_box = Gtk.EventBox()
        self.overlay.add_overlay(self.event_box)

        self.drawing_area = Gtk.DrawingArea()
        self.event_box.add(self.drawing_area)
        self.drawing_area.connect("draw", self.on_draw)

        self.event_box.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.event_box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        self.event_box.connect("motion-notify-event", self.on_tracking)
        self.event_box.connect("button-press-event", self.on_pressed)


        self.connect("key-press-event",self.on_key_press_event)        

        self.add(root_panel)


    def on_key_press_event(self, widget, event):
        print("Key press on widget: ", widget)
        print("          Modifiers: ", event.state)
        print("      Key val, name: ", event.keyval, Gdk.keyval_name(event.keyval))


        if event.keyval == self.up_key:
            self.go_up()
            return True
        elif event.keyval == self.left_key:
            self.go_left()
            return True
        elif event.keyval == self.right_key:
            self.go_right()
            return True
        elif event.keyval == self.down_key:
            self.go_down()
            return True
        elif event.keyval == self.increase_key:
            self.go_increase()
            return True
        elif event.keyval == self.decrease_key:
            self.go_decrease()
            return True

        return False


    def go_left(self):
        self.x = self.x - 5
        if self.x < 0 :
            self.x = 0

        self.drawing_area.queue_draw()

    def go_right(self):
        self.x = self.x + 5
        if self.x > self.draw_width + self.width:
            self.x = self.x - 5
        self.drawing_area.queue_draw()        

    def go_up(self):
        self.y = self.y - 5
        if self.y < 0:
            self.y = 0
        self.drawing_area.queue_draw()            

    def go_down(self):
        self.y = self.y + 5
        if self.y  > self.draw_height + self.width:
            self.y = self.y - 5
        self.drawing_area.queue_draw()

    def go_increase(self):
        self.width = self.width + 5
        self.drawing_area.queue_draw()        

    def go_decrease(self):
        self.width = self.width - 5
        if self.width < 0 :
            self.width = 0
        self.drawing_area.queue_draw()            


    def on_tracking(self, widget, event):
        return False


    def on_pressed(self, widget, event):
        self.tracking = not self.tracking
        print (event.x, event.y)
        self.x = event.x
        self.y = event.y
        self.drawing_area.queue_draw()        

    def on_draw(self, widget, context):

        rect = widget.get_allocation()

        self.draw_height = rect.height
        self.draw_width = rect.width        

        context.new_path()

        context.move_to(self.x, self.y)
        context.rel_line_to(self.width, 0)
        context.rel_line_to(0, self.width)
        context.rel_line_to(-self.width, 0)
        context.close_path()

        context.new_sub_path()
        context.move_to(0, 0)
        context.rel_line_to(0, rect.height)
        context.rel_line_to(rect.width, 0)
        context.rel_line_to(0, -rect.height)
        context.close_path()
                
        context.clip()

        context.set_source_rgba(.2, 0.2, 0.0, 0.2);
        context.paint()        

        return False

    def update_image(self):
        self.image = Gtk.Image.new_from_pixbuf(self.pixbuf)

        if self.overlay.get_child() is not None:
            self.overlay.remove(self.overlay.get_child())
        self.overlay.add(self.image)

        self.drawing_area.queue_draw()
        self.content_panel.show_all()
        

    def on_load(self, widget):
        self.current_image = "IMG_1.JPG"
        self.img_src = cv2.imread(self.current_image,1)
        self.ratio = .20

        self.img = cv_resize(self.img_src, self.ratio)
        self.pixbuf = cv_to_pixbuf(self.img)

        self.update_image()

        


win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.set_border_width(10)
win.set_default_size(1024, 768)
win.show_all()
Gtk.main()
