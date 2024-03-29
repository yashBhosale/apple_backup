from back import BackerUpper, BackgroundTask
import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, GLib

builder = Gtk.Builder()
builder.add_from_file("blueprint.xml")


class BackWindow(Gtk.Application):

    def __init__(self):
        super().__init__(application_id='com.example.BackWindow')
        GLib.set_application_name("hello")
        self.connect('activate', self.on_activate)
        self.backer_upper = BackerUpper()
        self.status_window = None
    
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
        print("attempt_pair")
        pair_task = BackgroundTask(self.backer_upper.pair, print, {"error_callback": self.error_dialog})
        pair_task.start()
        self.status_window = Gtk.Window()
        self.status_window.set_visible(True)

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
    
if __name__ == "__main__":
    app = BackWindow()
    exit_status= app.run(sys.argv)
    sys.exit(exit_status)
