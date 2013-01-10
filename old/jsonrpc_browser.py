from gi.repository import Gtk, GLib
import threading
import requests
import json
import time
import ast

GLib.threads_init()

class JSONrequest():
    def __init__(self, server, method, arguments):
        self.server = server
        self.method = method
        self.arguments = arguments

    def do_json_request(self):
        payload =  {
            "jsonrpc": "2.0",
            "method": self.method,
            "params": self.arguments,
            "id": 9001,
        }
        result = None

        try:
            r = requests.post(self.server, data=json.dumps(payload))
            result = r.json
        except:
            print "dat ging mis"

        return result
        

class CloseLabel(Gtk.Box):
    def __init__(self, name, notebook, respage):
        Gtk.Widget.__init__(self)
        self.name = name
        self.notebook = notebook
        self.respage = respage

        self.label = Gtk.Label(name)
        self.closebutton = Gtk.Button(stock = Gtk.STOCK_CLOSE)
        self.closebutton.connect("clicked", self.close)
        self.add(self.label)
        self.add(self.closebutton)

        self.show_all()

    def close(self, widget):
        pagenum = self.notebook.page_num(self.respage)
        self.notebook.remove_page(pagenum)


class ResultPage(Gtk.Box):
    def __init__(self, jsonrequest):
        Gtk.Widget.__init__(self)

        self.jsonrequest = jsonrequest

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)

        self.treestore = Gtk.TreeStore()
        self.treeview = Gtk.TreeView(self.treestore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Result", renderer, text=0)
        self.treeview.append_column(column)

        self.scrolledwindow.add(self.treeview)

        self.add(self.scrolledwindow)
        self.update_treeview()
        
    def update_treeview(self):
        print "update %s " % self.jsonrequest.method
        json_thread = threading.Thread(target=self.async_request)
        json_thread.start()

    def async_request(self):
        result = self.jsonrequest.do_json_request()
        if result:
            newTreestore = Gtk.TreeStore(str)
            self.build_tree_dict(None, newTreestore, result)
            self.treeview.set_model(newTreestore)
            self.show_all()

    def build_tree_dict(self, parent, treestore, test_dict):
        for key, value in test_dict.iteritems():
            child = treestore.append(parent, ["%s (%s)" % (str(key), type(value).__name__)])
            
            if isinstance(value, dict):
                self.build_tree_dict(child, treestore, value)
            elif isinstance(value, list):
                self.build_tree_list(child, treestore, value)
            else:
                treestore.append(child, [unicode(value)])

    def build_tree_list(self, parent, treestore, test_list):
        for i in range(len(test_list)) :
            child = treestore.append(parent, ["[%d] (%s)" % (i, type(test_list[i]).__name__)])

            if isinstance(test_list[i], dict):
                self.build_tree_dict(child, treestore, test_list[i])
            elif isinstance(test_list[i], list):
                self.build_tree_list(child, treestore, test_list[i])
            else:
                treestore.append(child, [unicode(test_list[i])])     


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

            self.listmodel.append([type(parsed).__name__, str(parsed)])
        except:
            pass

        self.lit_entry.set_text("")

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


    def do_json_fetch(self, server, method, arguments):
        payload =  {
            "jsonrpc": "2.0",
            "method": method,
            "params": arguments,
            "id": 9001,
        }
    
        r = requests.post(server, data=json.dumps(payload))


    def on_dialog(self, widget):
        dialog = RequestDialog(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            server = dialog.server_entry.get_text()
            method = dialog.method_entry.get_text()
            arguments = []
            for argrow in dialog.listmodel:
                arguments.append(ast.literal_eval(argrow[1]))

            jsonobj = JSONrequest(server, method, arguments)
            respage = ResultPage(jsonobj)

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

            self.notebook.append_page(respage, CloseLabel(label, self.notebook, respage))
            self.show_all()

        dialog.destroy()

    def on_refresh(self, widget):
        page = self.notebook.get_current_page()  
        if page >= 0:
            wg = self.notebook.get_nth_page(page)      
            wg.update_treeview()

            
            
win = TreeWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
