from pymobiledevice3.lockdown import create_using_usbmux, LockdownClient
from pymobiledevice3.services.mobilebackup2 import Mobilebackup2Service
from typing import Callable, Dict, Optional
from time import sleep
from queue import Queue
from pprint import pprint
from subprocess import run
from multiprocessing import Process
from functools import partial

from threading import Lock, Event
from contextlib import contextmanager

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib, Gio

DEBUG = True

# TODO make these more useful
# based on https://github.com/gdm-settings/gdm-settings/blob/c90ad295a6bc975fb05cb4e72e3d6041e012721d/gdms/utils.py#L144
class InvalidGioTaskError (Exception): pass
class AlreadyRunningError (Exception): pass

from gi.repository import Gio, GObject

class BackgroundTask (GObject.Object):
    __gtype_name__ = 'BackgroundTask'

    def __init__ (self, function, finish_callback, task_data, **kwargs):
        super().__init__(**kwargs)

        self.function = function
        self.finish_callback = finish_callback
        self._current: Optional[Gio.Task] = None
        self.task_data = task_data
        self.cancellable: Optional[Gio.Cancellable] = None

    def start(self):
        if self._current:
            AlreadyRunningError('Task is already running')

        finish_callback = lambda self, *_: self.finish_callback()

        task = Gio.Task.new(self, None, finish_callback, None)
        task.run_in_thread(self._thread_cb)

        self._current = task

    @staticmethod
    def _thread_cb (task: Gio.Task, self: BackgroundTask, task_data: Dict, cancellable: Gio.Cancellable):
        try:
            self.cancellable = cancellable
            retval = self.function(**task_data)
            task.return_value(retval)
        except Exception as e:
            task.return_value(e)

    def finish (self):
        task = self._current
        self._current = None

        if not Gio.Task.is_valid(task, self):
            raise InvalidGioTaskError()

        value = task.propagate_value().value

        if isinstance(value, Exception):
            raise value

        return value


class BackerUpper:
    
    msg_q: Queue
    step = 0

    phone_serial = None
    #These are defaults
    backup_location = './device_backup/'
    restic_local_repo = '/srv/restic/iphone/backups'
    restic_remote_repo = ''
    lockdown: Optional[LockdownClient] = None
    backup_service: Optional[Mobilebackup2Service] = None
    
    
    def __init__(self):
        self.msg_q = Queue()
        self.lock = Lock()


    def pair(self, error_callback):
        if DEBUG:
            GLib.idle_add(error_callback, 'No devices to pair with! :( ')
            return
        else:
            with nonblocking(self.lock, error_callback):
                self.lockdown = create_using_usbmux()
                pprint(self.lockdown.short_info)
                self.backup_service = Mobilebackup2Service(self.lockdown)

    # A slightly cursed idea - instead of running the backup directly, spawn a ~process~ and monitor it
    # so that if necessary you can kill it.
    def create_phone_backup(self, progress_callback: Callable[[int], None], error_callback: Callable[[str], None], kill_flag: Event):
        if DEBUG:
            pass
        if not self.backup_service:
            GLib.idle_add(error_callback, "No devices paired!")
            return

        with nonblocking(self.lock, error_callback):
            #TODO: progress_callback recieves progress percentage - maybe update a progress bar on the frontend?
            p = Process(target=self.backup_service.backup, kwargs={"backup_directory": self.backup_location, "progress_callback": progress_callback})
            while p.is_alive() and not kill_flag.isSet():
                sleep(.5)
            if kill_flag.isSet():
                p.kill()

    def restic_local_backup(self):
        self._restic_backup(self.restic_local_repo)
    
    def restic_remote_backup(self):
        self._restic_backup(self.restic_remote_repo)
        pass


    def _restic_backup(self, repo=None):
        if not repo:
            repo = self.restic_local_repo
        run(f"restic -r {repo} backup --verbose (self.backup_location)", shell=True, capture_output=True)


    def b(self):
        
        while new_msg := self.msg_q.get():
            {
                'create_backup': partial(self.create_phone_backup, progress_callback=print),
                'restic_local': self.restic_local_backup,
                'restic_local': self.restic_remote_backup,
                '': exit
            }[new_msg]()


if __name__ == "__main__":
    pass

