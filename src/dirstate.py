import os
import pandas as pd

file_column_name = 'Realpath'
modt_column_name = 'Modified'


class DirState:

    def __init__(self, watched_dir):
        if watched_dir == None:
            return
        self.state = self.__get_dir_state(watched_dir)

    def read_from_file(self, state_file_name):
        if not os.path.exists(state_file_name):
            state_data = {file_column_name:[],
                          modt_column_name:[]}
            self.state = pd.DataFrame(state_data)
        else:
            self.state = pd.read_csv(state_file_name)

    def write_to_file(self, state_path):
        self.state.to_csv(state_path, index=False)

    def compare(self, other):
        def to_dict(dataframe):
            return {t.Realpath: t.Modified for t in dataframe.itertuples(index=False)}
        return other is None or to_dict(self.state) != to_dict(other.state)

    def get_files(self):
        return [file for file in self.state[file_column_name]]


    @staticmethod
    def __get_dir_state(watched_dir):
        entries = os.listdir(watched_dir)
        entries = [os.path.join(watched_dir, entry) for entry in entries]
        files = [entry for entry in entries if os.path.isfile(entry)]
        state_data = {file_column_name:[file for file in files],
                      modt_column_name:[
                        pd.to_datetime(
                            os.path.getmtime(file), unit='s'
                        ).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] for file in files]}
        return pd.DataFrame(state_data)
