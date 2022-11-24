import os
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth


class GDrive:

    def __init__(self):
        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(self.gauth)

    def create_folder(self, parent_id, folder_name):
        file_metadata = {
            'title': folder_name,
            'parents': [{'id': parent_id}],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.drive.CreateFile(file_metadata)
        folder.Upload()
        return folder['id']

    def create_file(self, parent_id, file_name):
        file_metadata = {
            'title': os.path.basename(file_name),
            'parents': [{'id': parent_id}],
        }
        file = self.drive.CreateFile(file_metadata)
        file.SetContentFile(file_name)
        file.Upload()
        return file['id']
