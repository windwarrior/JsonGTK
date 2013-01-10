from gi.repository import Gtk
from models import JSONRequest

class JSONResultPage(Gtk.Box):
    def __init__(self, jsonrequest):
        Gtk.Widget.__init__(self)
        self.jsonrequest = jsonrequest
        self.jsonrequest.attach(self)

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)

        self.treestore = Gtk.TreeStore()
        self.treeview = Gtk.TreeView(self.treestore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Result", renderer, text=0)
        self.treeview.append_column(column)

        self.scrolledwindow.add(self.treeview)

        self.errorlabel = Gtk.Label("Error while processing request")
  
        self.jsonrequest.do_json_request()

        self.spinner = Gtk.Spinner()

        self.add(self.scrolledwindow)
        self.add(self.errorlabel)
        self.add(self.spinner)
        
        self.spinner.start()
        
 
        self.errorlabel.hide()
        self.scrolledwindow.hide()
        self.spinner.show()


    def request_update(self):
        self.jsonrequest.do_json_request()
        
    def update(self, notifier):
        if notifier.error:
            #Show an error
            self.errorlabel.set_text(notifier.error)

            #Remove all other childs
            self.scrolledwindow.hide()
            self.errorlabel.show()
            
        else:
            #Show the treeview
            newTreeStore = Gtk.TreeStore(str)
            self.build(None, newTreeStore, notifier.result)
            self.treeview.set_model(newTreeStore)
            
            #Remove all other childs

            self.errorlabel.hide()
            self.scrolledwindow.show()
            
    """
    Deze methode past een van zijn parameters aan, zonder return => niet net
    """
    def build(self, parent, treestore, item_tree):
        if isinstance(item_tree, dict):
            for key, value in item_tree.iteritems():
                child_tree = treestore.append(parent, ["%s (%s)" % (str(key), type(value).__name__)])                
                self.build(child_tree, treestore, value)

        elif isinstance(item_tree, list):
            for i in range(len(item_tree)) :
                child_tree = treestore.append(parent, ["[%d] (%s)" % (i, type(item_tree[i]).__name__)])            
                self.build(child_tree, treestore, item_tree[i])

        else:
            treestore.append(parent, [unicode(item_tree)])
