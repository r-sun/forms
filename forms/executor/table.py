#  Copyright 2022-2023 The FormS Authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pandas as pd
from abc import ABC, abstractmethod
from forms.runtime.remoteobject import RemoteObject


class Table(ABC):
    @abstractmethod
    def get_num_of_rows(self) -> int:
        pass

    @abstractmethod
    def get_num_of_columns(self) -> int:
        pass

    @abstractmethod
    def get_table_content(self):
        pass

    @abstractmethod
    def gen_table_for_execution(self):
        pass


class DFTable(Table):
    def __init__(self, df: pd.DataFrame = None, remote_object: RemoteObject = None):
        assert df is not None or remote_object is not None
        self.df = df
        self.remote_object = remote_object

    def get_num_of_rows(self) -> int:
        return self.get_table_content().shape[0]

    def get_num_of_columns(self) -> int:
        return self.get_table_content().shape[1]

    def get_table_content(self) -> pd.DataFrame:
        if self.df is None:
            self.df = self.remote_object.get_content()
        return self.df

    def gen_table_for_execution(self) -> Table:
        return DFTable(None, remote_object=self.remote_object)


class RelTable(Table):
    def get_num_of_rows(self) -> int:
        return -1

    def get_num_of_columns(self) -> int:
        pass

    def get_table_content(self):
        pass

    def gen_table_for_execution(self) -> Table:
        pass
