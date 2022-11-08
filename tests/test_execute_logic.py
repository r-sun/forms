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
import pytest
import numpy as np
import pandas as pd
from typing import Callable

from forms.executor.executionnode import (
    RefExecutionNode,
    FunctionExecutionNode,
    LitExecutionNode,
    create_intermediate_ref_node,
)
from forms.executor.dfexecutor.logicfunctionexecutor import if_executor, equal_executor
from forms.executor.table import DFTable
from forms.executor.utils import ExecutionContext
from forms.utils.reference import Ref, RefType, axis_along_row
from forms.utils.functions import Function
from forms.utils.treenode import link_parent_to_children

table = None


@pytest.fixture(autouse=True)
def execute_before_and_after_one_test():
    m = 100
    n = 5
    df = pd.DataFrame(np.full((m, n), "test"))
    global table
    table = DFTable(df)

    yield


def compute_one_formula(ref: Ref, ref_type: RefType, function: Function, executor: Callable) -> DFTable:
    global table
    root = FunctionExecutionNode(function, Ref(0, 0), RefType.RR, axis_along_row)
    child = RefExecutionNode(ref, table, ref_type, axis_along_row)
    link_parent_to_children(root, [child])
    child.set_exec_context(ExecutionContext(50, 100, axis_along_row))
    return executor(root)


# Simple test of IF(C2="Yes",1,2)
# = is parent of C2 and "Yes"
# IF is parent of =, 1, and 2
def test_execute_if():
    root = FunctionExecutionNode(Function.IF, Ref(0, 0), RefType.RR, axis_along_row)
    parent = FunctionExecutionNode(Function.EQUAL, Ref(0, 0), RefType.RR, axis_along_row)
    child1 = LitExecutionNode("1", RefType.RR, axis_along_row)
    child2 = LitExecutionNode("0", RefType.RR, axis_along_row)
    child3 = RefExecutionNode(Ref(1, 3), table, RefType.FF, axis_along_row)
    child4 = LitExecutionNode("test", RefType.RR, axis_along_row)

    link_parent_to_children(root, [parent, child1, child2])
    link_parent_to_children(parent, [child3, child4])
    root.set_exec_context(ExecutionContext(50, 100, axis_along_row))
    sub_result = equal_executor(parent)
    ref_node = create_intermediate_ref_node(sub_result, parent)
    link_parent_to_children(root, [ref_node, child1, child2])
    result = if_executor(root)

    real_result = pd.DataFrame(np.full(50, "1"))
    assert np.array_equal(result.df.iloc[0:50].values, real_result.values)