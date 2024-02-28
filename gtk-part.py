import gi
import sys

from collections.abc import Callable
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, GObject


builder = Gtk.Builder()
builder.add_from_file("blueprint.xml")

@GObject.Signal(arg_types=(Callable, ))
def dialog_response(self, set_buffer):

    dialog = Gtk.FileDialog()

    def select_finish(dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            set_buffer(folder.get_path())

        except Gtk.DialogError:
            pass

    dialog.select_folder(None, None, select_finish)

def on_activate(app):
    win= builder.get_object("window1")
    win.present()
    button = builder.get_object("folder-find-button")
    file_text = builder.get_object("file-text")
    button.connect('clicked', dialog_response, file_text.set_text)
    provider = Gtk.CssProvider()

    provider.load_from_path("./css-part.css")
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    win.set_application(app)


app = Adw.Application()
app.connect('activate', on_activate)
exit_status= app.run(sys.argv)
sys.exit(exit_status)
#
window.show_all()
