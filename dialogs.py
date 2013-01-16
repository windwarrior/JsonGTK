from gi.repository import Gtk, GLib
import ast

class RequestDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Add a new JSONRPC method", parent,
            Gtk.DialogFlags.MODAL, buttons=(
            Gtk.STOCK_EXECUTE, Gtk.ResponseType.OK,
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        
        box = self.get_content_area()

        grid = Gtk.Grid()
        grid.set_column_spacing(20)        
        grid.set_row_spacing(10)

        self.server_label = Gtk.Label("Server: ")
        self.server_entry = Gtk.Entry()

        self.method_label = Gtk.Label("Method: ")
        self.method_entry = Gtk.Entry()

        grid.attach(self.server_label, 0, 0, 1, 1)
        grid.attach_next_to(self.server_entry, self.server_label,  Gtk.PositionType.RIGHT, 2, 1)
        
        grid.attach(self.method_label, 0, 1, 1, 1)
        grid.attach_next_to(self.method_entry, self.method_label,  Gtk.PositionType.RIGHT, 2, 1)

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)
        self.scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        self.listmodel = Gtk.ListStore(str, str)
      
        self.view = Gtk.TreeView(model = self.listmodel)
        cell1 = Gtk.CellRendererText()
        col1 = Gtk.TreeViewColumn("Type", cell1, text=0)
        self.view.append_column(col1)

        cell2 = Gtk.CellRendererText()
        col2 = Gtk.TreeViewColumn("Value", cell2, text=1)
        self.view.append_column(col2)

        self.scrolledwindow.add(self.view)
        grid.attach(self.scrolledwindow, 0, 2, 3, 3)

        self.lit_label = Gtk.Label("Literal variable: ")
        self.lit_entry = Gtk.Entry()
        self.lit_button = Gtk.Button(label="Add")

        self.lit_button.connect("clicked", self.on_lit_button_clicked)
        grid.attach(self.lit_label, 0, 5, 1, 1)
        grid.attach_next_to(self.lit_entry, self.lit_label, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.lit_button, self.lit_entry, Gtk.PositionType.RIGHT, 1, 1)

        box.add(grid)

        self.show_all()

    def on_lit_button_clicked(self, widget):
        lit_val = self.lit_entry.get_text()

        try:
            parsed = ast.literal_eval(lit_val)

            self.listmodel.append([type(parsed).__name__, lit_val])
        except:
            pass

        self.lit_entry.set_text("")
