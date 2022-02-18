import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository.GdkPixbuf import InterpType
from gi.repository.GdkPixbuf import PixbufRotation
from gi.repository import GLib


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
        button.connect("clicked", self.on_button_clicked)
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
        self.pixbuf_source = Pixbuf.new_from_file("IMG_1.JPG")
        
        self.pixbuf_scaled = self.pixbuf_source.scale_simple(self.pixbuf_source.get_width()/self.ratio,
                                                        self.pixbuf_source.get_height()/self.ratio,
                                                        InterpType.HYPER)

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

        
        



win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.set_border_width(10)
win.set_default_size(1024, 768)
win.show_all()
Gtk.main()
