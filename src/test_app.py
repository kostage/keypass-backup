import os
from mock import patch, call
import tempfile
import datetime
import time
import logging

import app
import tgnotify


config_template = '''
watched_dir: {}
workdir: {}
gdrive_shapshot_folder_id: {}
tg_bot_token: {}
tg_chat_id: {}
'''

class AppTestFixture:

    def __init__(self):
        self.watched_dir = tempfile.TemporaryDirectory()
        self.workdir = tempfile.TemporaryDirectory()
        self.workdir_name = self.workdir.name
        self.watched_dir_name = self.watched_dir.name
        config_file_path = os.path.join(self.workdir_name, 'config.yaml')
        gdrive_shapshot_folder_id = 'gdrv_folder_id'
        with open(config_file_path, 'w+') as config_file:
            config_file.write(
                config_template.format(
                    self.watched_dir_name,
                    self.workdir_name,
                    gdrive_shapshot_folder_id,
                    'token',
                    'id',
                )
            )

    def addfile(self, filename):
        with open(os.path.join(self.watched_dir_name, filename), 'w+'):
            pass

    def modifyfile(self, filename):
        time.sleep(0.01) # sleep few ms to change modified timestamp
        with open(os.path.join(self.watched_dir_name, filename), 'w+') as f:
            f.write('text')

    def delfile(self, filename):
        os.remove(os.path.join(self.watched_dir_name, filename))

    @property
    def config_filename(self):
        return 'config.yaml'


test_fixt = AppTestFixture()

@patch('app.GDrive')
@patch("config.default_workdir", test_fixt.workdir_name)
def test_app(mock_gdrive):

    ### empty watched dir
    mc = mock_gdrive.return_value
    application = app.App()
    application.run()
    assert not mc.create_folder.called, 'create_folder should not have been called'
    assert not mc.create_file.called, 'create_file should not have been called'
    mock_gdrive.reset_mock()


    ### add file
    test_fixt.addfile('file1')
    mc.create_folder.return_value = 'folder_id'
    mc.create_file.return_value = 'file_id'
    application = app.App()
    application.run()
    mc.create_folder.assert_called_with('gdrv_folder_id', 'snapshot_' + datetime.datetime.now().strftime('%Y-%m-%d'))
    create_file_calls = [
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file1'))
    ]
    mc.create_file.assert_has_calls(create_file_calls, any_order=True)
    mock_gdrive.reset_mock()


    ### add 2 more files
    test_fixt.addfile('file2')
    test_fixt.addfile('file3')
    mc.create_folder.return_value = 'folder_id'
    mc.create_file.return_value = 'file_id'
    application = app.App()
    application.run()
    mc.create_folder.assert_called_with('gdrv_folder_id', 'snapshot_' + datetime.datetime.now().strftime('%Y-%m-%d'))

    create_file_calls = [
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file1')),
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file2')),
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file3'))
    ]
    mc.create_file.assert_has_calls(create_file_calls, any_order=True)
    mock_gdrive.reset_mock()


    ### no changes - no snapshot
    application = app.App()
    application.run()
    assert not mc.create_folder.called, 'create_folder should not have been called'
    assert not mc.create_file.called, 'create_file should not have been called'
    mock_gdrive.reset_mock()


    ### modify file - full snapshot again
    test_fixt.modifyfile('file2')
    application = app.App()
    application.run()
    mc.create_folder.assert_called_with('gdrv_folder_id', 'snapshot_' + datetime.datetime.now().strftime('%Y-%m-%d'))

    create_file_calls = [
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file1')),
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file2')),
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file3'))
    ]
    mc.create_file.assert_has_calls(create_file_calls, any_order=True)
    mock_gdrive.reset_mock()


    ### remove file
    test_fixt.delfile('file3')
    mc.create_folder.return_value = 'folder_id'
    mc.create_file.return_value = 'file_id'
    application = app.App()
    application.run()
    mc.create_folder.assert_called_with('gdrv_folder_id', 'snapshot_' + datetime.datetime.now().strftime('%Y-%m-%d'))

    create_file_calls = [
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file1')),
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file2'))
    ]
    mc.create_file.assert_has_calls(create_file_calls, any_order=True)
    mock_gdrive.reset_mock()


    ### remove 1 more
    test_fixt.delfile('file1')
    mc.create_folder.return_value = 'folder_id'
    mc.create_file.return_value = 'file_id'
    application = app.App()
    application.run()
    mc.create_folder.assert_called_with('gdrv_folder_id', 'snapshot_' + datetime.datetime.now().strftime('%Y-%m-%d'))

    create_file_calls = [
        call('folder_id', os.path.join(test_fixt.watched_dir_name, 'file2'))
    ]
    mc.create_file.assert_has_calls(create_file_calls, any_order=True)
    mock_gdrive.reset_mock()


    ### remove last - no empty snapshot
    test_fixt.delfile('file2')
    mc.create_folder.return_value = 'folder_id'
    mc.create_file.return_value = 'file_id'
    application = app.App()
    application.run()
    assert not mc.create_folder.called, 'create_folder should not have been called'
    assert not mc.create_file.called, 'create_file should not have been called'
    mock_gdrive.reset_mock()


@patch('tgnotify.TelegramAPI')
@patch("config.default_workdir", test_fixt.workdir_name)
def test_tg(mock_tgapi):

    ### empty queue
    tgapi = mock_tgapi.return_value
    notifier = tgnotify.TelegramNotifier(logging.getLogger(__name__))
    tg_send_chat_calls = [
        call('id', 'message')
    ]
    def side_effect(id, msg):
        return True, 'OK'
    tgapi.send_chat.side_effect = side_effect

    notifier.notify('message')
    tgapi.send_chat.assert_has_calls(tg_send_chat_calls, any_order=True)
    tgapi.reset_mock()


    ### failed to send 3 messages in a row
    tgapi = mock_tgapi.return_value
    tg_send_chat_calls = [
        call('id', 'message1'),
        call('id', 'message1'),
        call('id', 'message1'),
    ]
    def side_effect(id, msg):
        return False, 'internal error'
    tgapi.send_chat.side_effect = side_effect

    notifier = tgnotify.TelegramNotifier(logging.getLogger(__name__))
    notifier.notify('message1')
    notifier.notify('message2')
    notifier.notify('message3')

    tgapi.send_chat.assert_has_calls(tg_send_chat_calls, any_order=True)
    tgapi.reset_mock()
    print('after fials', os.listdir(test_fixt.workdir.name + "/tg_notify"))


    ### partially sent
    tgapi = mock_tgapi.return_value
    tg_send_chat_calls = [
        call('id', 'message1'),
        call('id', 'message2'),
        call('id', 'message3'),
    ]
    def side_effect(id, msg):
        if msg == 'message3':
            return False, 'internal error'
        else:
            return True, 'OK'

    tgapi.send_chat.side_effect = side_effect

    notifier = tgnotify.TelegramNotifier(logging.getLogger(__name__))
    notifier.notify('message4')
    tgapi.send_chat.assert_has_calls(tg_send_chat_calls, any_order=True)
    tgapi.reset_mock()

    
    ### send the rest
    tgapi = mock_tgapi.return_value
    tg_send_chat_calls = [
        call('id', 'message3'),
        call('id', 'message4'),
        call('id', 'message5'),
    ]
    def side_effect(id, msg):
        return True, 'OK'

    tgapi.send_chat.side_effect = side_effect

    notifier = tgnotify.TelegramNotifier(logging.getLogger(__name__))
    notifier.notify('message5')
    tgapi.send_chat.assert_has_calls(tg_send_chat_calls, any_order=True)
    tgapi.reset_mock()


    ### empty queue
    tgapi = mock_tgapi.return_value
    notifier = tgnotify.TelegramNotifier(logging.getLogger(__name__))
    tg_send_chat_calls = [
        call('id', 'message')
    ]
    def side_effect(id, msg):
        return True, 'OK'
    tgapi.send_chat.side_effect = side_effect

    notifier.notify('message')
    tgapi.send_chat.assert_has_calls(tg_send_chat_calls, any_order=True)
    tgapi.reset_mock()
