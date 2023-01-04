import os
import requests
from glob import glob

from config import Config


tg_send_msg_url = "https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
default_notify_queue_dir = "tg_notify"
queued_file_name_pref = "queued_"

class TelegramAPI:

    def __init__(self, bot_token):
        self.__token = bot_token

    def send_chat(self, chat_id, message):
        resp = requests.get(
            tg_send_msg_url.format(
                token=self.__token,
                chat_id=chat_id,
                message=message,
            ),
            timeout=10,
        ).json()
        if resp is None:
            return False, "no response"
        if resp['ok']:
            return True, "OK"
        else:
            return False, resp['description']


class TelegramNotifier:

    def __init__(self, logger):
        cfg = Config()
        self.__logger = logger
        self.__tg_api = TelegramAPI(cfg.tg_bot_token)
        self.__chat_id = cfg.tg_chat_id
        self.__workdir = cfg.workdir
        os.makedirs(os.path.join(self.__workdir, default_notify_queue_dir), exist_ok=True)

    def notify(self, message):
        try:
            self.__try_notify(message)
        except:
            self.__logger.exception("telegram notify exception")

    def __try_notify(self, message):
        next_queued = 0
        queued_path_prefix = os.path.join(self.__workdir, default_notify_queue_dir, queued_file_name_pref)
        queued = glob(queued_path_prefix + "*")
        queued_idx = [int(filename.removeprefix(queued_path_prefix)) for filename in queued]
        if len(queued_idx) > 0:
            next_queued = max(queued_idx) + 1
        with open(queued_path_prefix + str(next_queued), 'w+') as file:
            file.write(message)
        self.__try_send_queue()

    def __try_send_queue(self):
        queued_path_prefix = os.path.join(self.__workdir, default_notify_queue_dir, queued_file_name_pref)
        queued = glob(queued_path_prefix + "*")
        for filepath in sorted(queued):
            with open(filepath, 'r') as file:
                msg = file.read()
                self.__try_send_message(msg)
            os.remove(filepath)

    def __try_send_message(self, message):
        success, resp = self.__tg_api.send_chat(self.__chat_id, message)
        if not success:
            raise RuntimeError("bad response from telegram API: {}".format(resp))
