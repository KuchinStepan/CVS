from cvs_dialogs import *


class CloneVersionSystem:
    def __init__(self):
        self.running = False
        self.main_folder = None
        self.commands = {
            'stop': self.stop,
            '0': self.stop
        }

    def stop(self):
        self.running = False

    def run(self):
        print('Добро пожаловать в систему контроля версий CVS')
        self.running = True
        self.main_folder = read_main_folder()
        while self.running:
            command = input()

