import gtk
import shelve

class Icons(object):
    
    def __init__(self, cb):
        self.cb = cb
        icon_file = self.cb.opts.get('files','data_icons')
        self.d = shelve.open(icon_file, 'r')
        self.cs = gtk.gdk.COLORSPACE_RGB
    
    def get(self, name, *args):
        if name not in  self.d:
            name = 'new'
        d, a = self.d[name]
        pb = gtk.gdk.pixbuf_new_from_data(d, self.cs, *a)
        return pb

    def get_image(self, name, *size):
        im = gtk.Image()
        im.set_from_pixbuf(self.get(name))
        return im

    def get_button(self, name, *asize):
        ic = self.get_image(name)
        but = gtk.ToolButton(icon_widget=ic)
        return but

