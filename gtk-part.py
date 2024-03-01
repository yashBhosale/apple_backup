import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib

import sys

from collections.abc import Callable
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, GObject

from back import BackerUpper
from threading import Thread
builder = Gtk.Builder()
builder.add_from_file("blueprint.xml")


class BackWindow(Gtk.Application):

    def __init__(self):
        super().__init__(application_id='com.example.BackWindow')
        GLib.set_application_name("hello")
        self.connect('activate', self.on_activate)
        self.backer_upper = BackerUpper()
    
    def dialog_response(self, widget, set_buffer):

        dialog = Gtk.FileDialog()

        def select_finish(dialog, result):
            try:
                folder = dialog.select_folder_finish(result)
                set_buffer(folder.get_path())

            except Gtk.DialogError:
                pass

        dialog.select_folder(None, None, select_finish)

    def attempt_pair(self, widget):
        t = Thread(target=self.backer_upper.pair, args=[self.error_dialog])
        t.run()

    def on_activate(self, app):
        self.win= builder.get_object("window1")
        self.win.present()
        
        folder_find_button = builder.get_object("folder-find-button")
        file_text = builder.get_object("file-text")
        folder_find_button.connect('clicked', self.dialog_response, file_text.set_text)
        
        pair_button = builder.get_object("pair")
        pair_button.connect('clicked', self.attempt_pair)

        provider = Gtk.CssProvider()

        provider.load_from_path("./css-part.css")
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.win.set_application(self)

    def error_dialog(self, err_string):
        x = Gtk.AlertDialog()
        x.transient_for = self.win
        x.set_message(err_string)
        x.choose()
    

app = BackWindow()
exit_status= app.run(sys.argv)
sys.exit(exit_status)
