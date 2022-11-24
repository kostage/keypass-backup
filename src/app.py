import datetime

from dirstate import DirState
from gdrive import GDrive
from config import Config
from tgnotify import TelegramNotifier

import logging

class App:
    def __init__(self):
        self.__gdrive = GDrive()
        self.__config = Config()
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            filename=self.__config.log_file,
            filemode='a',
            encoding='utf-8', 
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def run(self):
        new_state = DirState(self.__config.watched_dir)
        old_state = DirState(None)
        old_state.read_from_file(self.__config.state_file)
        logging.info("old_state {}".format(old_state.get_files()))
        logging.info("new_state {}".format(new_state.get_files()))
        if new_state.compare(old_state) and len(new_state.get_files()) != 0:
            self.__create_snapshot(new_state)
            new_state.write_to_file(self.__config.state_file)

    def __create_snapshot(self, new_state):
        folder_id = self.__gdrive.create_folder(
            self.__config.gdrive_folder_id,
            'snapshot_' + datetime.datetime.now().strftime('%Y-%m-%d')
        )
        for file in new_state.get_files():
            self.__gdrive.create_file(folder_id, file)


if __name__ == '__main__':
    app = App()
    notifier = TelegramNotifier(logging.getLogger(__name__))
    try:
        app.run()
        notifier.notify('shapshot created')
    except Exception as e:
        notifier.notify('keypass-backup exception: {}'.format(e))
        logging.exception("create shapshot exception")
