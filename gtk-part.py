import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
import workbench


def dialog_response(parent, data):
    dialog = Gtk.FileDialog()

    def select_finish(dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            data(folder.get_path())

        except Gtk.DialogError:
            pass

    dialog.select_folder(None, None, select_finish)


button: Gtk.Box = workbench.builder.get_object("folder-find-button")
file_text = workbench.builder.get_object("file-text")

button.connect("clicked", dialog_response, lambda path: file_text.set_text(path))



