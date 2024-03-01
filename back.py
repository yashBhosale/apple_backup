from pymobiledevice3.lockdown import create_using_usbmux, LockdownClient
from pymobiledevice3.services.mobilebackup2 import Mobilebackup2Service
from typing import Optional
from time import sleep
from queue import Queue
from pprint import pprint
from subprocess import run
from multiprocessing import Process
from functools import partial

from threading import Lock
from contextlib import contextmanager

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib

DEBUG = True

@contextmanager
def nonblocking(lock, error_callback):
    if not lock.acquire(False):
        GLib.idle_add(error_callback, "Something else is running!")
        raise RuntimeError

    try:
        yield lock
    except Exception as e:
        error_callback(str(e))
    finally:
        if lock:
            lock.release()

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
    def create_phone_backup(self, progress_callback, error_callback):
        if DEBUG:
            pass
        if not self.backup_service:
            GLib.idle_add(error_callback, "No devices paired!")
            return

        with nonblocking(self.lock, error_callback):
            #TODO: progress_callback recieves progress percentage - maybe update a progress bar on the frontend?
            p = Process(target=self.backup_service.back. kwargs={backup_directory:self.backup_location, progress_callback:progress_callback})
            self.backup_service.backup(backup_directory=self.backup_location, progress_callback=progress_callback)

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

