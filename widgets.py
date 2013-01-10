from gi.repository import Gtk, GLib

class CloseLabel(Gtk.Box):
    def __init__(self, name, notebook, respage):
        Gtk.Widget.__init__(self)
        self.name = name
        self.notebook = notebook
        self.respage = respage

        self.label = Gtk.Label(name)
        self.closebutton = Gtk.Button()
        self.closebutton.set_relief(Gtk.ReliefStyle.NONE)
        self.closebutton.set_focus_on_click(False)
        image = Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
        self.closebutton.add(image)
        self.closebutton.connect("clicked", self.close)
        self.add(self.label)
        self.add(self.closebutton)

        self.show_all()

    def close(self, widget):
        pagenum = self.notebook.page_num(self.respage)
        self.notebook.remove_page(pagenum)
