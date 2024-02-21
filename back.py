from pymobiledevice3.lockdown import create_using_usbmux, LockdownClient
from pymobiledevice3.services.mobilebackup2 import Mobilebackup2Service
from typing import Optional
from time import sleep
from queue import Queue
from pprint import pprint
from subprocess import run
from functools import partial

class BackerUpper:
    
    msg_q: Queue
    step = 0

    phone_serial = None
    backup_location = './device_backup/'
    restic_local_repo = '/srv/restic/iphone/backups'
    restic_remote_repo = ''
    lockdown: Optional[LockdownClient] = None
    backup_service: Mobilebackup2Service 
    
    
    def __init__(self):
        self.msg_q = Queue()

    def pair(self):
        self.lockdown = create_using_usbmux()
        pprint(self.lockdown.short_info)
        self.backup_service = Mobilebackup2Service(self.lockdown)


    def create_phone_backup(self, progress_callback):
        #TODO: progress_callback recieves progress percentage - maybe update a progress bar on the frontend?
        self.backup_service.backup(backup_directory=self.backup_location, progress_callback=progress_callback)

    def restic_local_backup(self):
        self._restic_backup(self.restic_local_repo)
    
    def restic_remote_backup(self):
        #self._restic_backup(self.restic_remote_repo)
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

