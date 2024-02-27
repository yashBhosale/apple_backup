import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk
import sys

@Gtk.Template(filename="./blueprint.xml")
class Window1(Adw.ApplicationWindow):
    __gtype_name__ = "window1"

    @Gtk.Template.Callback()
    def dialog_response(parent, data):
        print(parent, data)
        data("hello")
        return 

        dialog = Gtk.FileDialog()

        def select_finish(dialog, result):
            try:
                folder = dialog.select_folder_finish(result)
                data(folder.get_path())

            except Gtk.DialogError:
                pass

        dialog.select_folder(None, None, select_finish)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(Gtk.Template.Child())
    

def on_activate(app):
    win = Window1()
    win.present()
    provider = Gtk.CssProvider()

    provider.load_from_path("./css-part.css")
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    win.set_application(app)


app = Adw.Application()
app.connect('activate', on_activate)
exit_status= app.run(sys.argv)
sys.exit(exit_status)

