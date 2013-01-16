from gi.repository import Gtk, GLib
from dialogs import RequestDialog
from widgets import CloseLabel
from models import JSONRequest
from pages import JSONResultPage
import ast

GLib.threads_init()

class TreeWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="JSON browser")
        self.set_default_size(640, 480)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox.add(self.create_toolbox())

        self.notebook = Gtk.Notebook()
        self.notabslabel = Gtk.Label("Use execute to run a JSONRPC command")
        self.vbox.add(self.notabslabel)
        self.add(self.vbox)        

    def create_toolbox(self):
        toolbar = Gtk.Toolbar()
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR);
        execbutton = Gtk.ToolButton.new_from_stock(Gtk.STOCK_EXECUTE)
        execbutton.set_is_important(True)
        execbutton.connect("clicked", self.on_dialog)

        reloadbutton = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REFRESH)
        reloadbutton.set_is_important(True)
        reloadbutton.connect("clicked", self.on_refresh)

        toolbar.insert(execbutton, 0)
        toolbar.insert(reloadbutton, 1)

        return toolbar


    def on_dialog(self, widget):
        dialog = RequestDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            server = dialog.server_entry.get_text()
            method = dialog.method_entry.get_text()
            arguments = []
            for argrow in dialog.listmodel:
                arguments.append(ast.literal_eval(argrow[1]))

            jsonobj = JSONRequest(server, method, arguments)
            respage = JSONResultPage(jsonobj)

            if not (self.notabslabel.get_parent() == None):
                self.vbox.remove(self.notabslabel)                
            if (self.notebook.get_parent() == None):
                self.vbox.add(self.notebook)      
          
            label = jsonobj.method + "("

            for i in range(len(jsonobj.arguments)):
                label = label + str(jsonobj.arguments[i])
                if i < len(jsonobj.arguments) - 1:
                    label = label + ", "
            label += ")"

            index = self.notebook.append_page(respage, CloseLabel(label, self.notebook, respage))

            self.show_all()
            #TODO uglyuglyugly but has to do now
            respage.errorlabel.hide()
            respage.scrolledwindow.hide()
            

        dialog.destroy()

    def on_refresh(self, widget):
        page = self.notebook.get_current_page()  
        if page >= 0:
            wg = self.notebook.get_nth_page(page)      
            wg.request_update()

win = TreeWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
