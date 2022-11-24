import os
import yaml


default_workdir = os.path.join(os.getenv('HOME'), '.keypass_backup')
default_config_file_name = 'config.yaml'
default_state_file = 'state.csv'
default_log_file = 'keypass_backup.log'

watched_dir_field = 'watched_dir'
workdir_field = 'workdir'
gdrive_folder_id_field = 'gdrive_shapshot_folder_id'
tg_chat_id_field = 'tg_chat_id'
tg_bot_token_field = 'tg_bot_token'

class Config:

    def __init__(self):
        with open(os.path.join(default_workdir, default_config_file_name), "r") as stream:
            config = yaml.safe_load(stream)
            self.__workdir = default_workdir
            self.__state_file = os.path.join(self.__workdir, default_state_file)
            self.__log_file = os.path.join(self.__workdir, default_log_file)
            self.__watched_dir = config[watched_dir_field]
            if self.__watched_dir == '':
                raise RuntimeError('empty watched dir')
            self.__gdrive_folder_id = config[gdrive_folder_id_field]
            if self.__gdrive_folder_id == '':
                raise RuntimeError('empty gdrive snapshot folder id')
            self.__tg_chat_id = config[tg_chat_id_field]
            self.__tg_bot_token = config[tg_bot_token_field]

    @property
    def workdir(self):
        return self.__workdir

    @property
    def state_file(self):
        return self.__state_file

    @property
    def watched_dir(self):
        return self.__watched_dir

    @property
    def gdrive_folder_id(self):
        return self.__gdrive_folder_id

    @property
    def log_file(self):
        return self.__log_file

    @property
    def tg_chat_id(self):
        return self.__tg_chat_id

    @property
    def tg_bot_token(self):
        return self.__tg_bot_token
