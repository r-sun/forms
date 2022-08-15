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

from forms.executor.pandasexecutor.functionexecutor import *

table = None


@pytest.fixture(autouse=True)
def execute_before_and_after_one_test():
    m = 100
    n = 5
    df = pd.DataFrame(np.ones((m, n)))
    global table
    table = DFTable(df)

    yield


def compute_one_formula(ref: Ref, ref_type: RefType) -> DFTable:
    global table
    root = FunctionExecutionNode(Function.SUM, RefType.RR, RefDirection.DOWN)
    child = RefExecutionNode(ref, table, ref_type, RefDirection.DOWN)
    link_parent_to_children(root, [child])
    child.set_exec_context(ExecutionContext(50, 100))
    return sum_df_executor(root)


# try to mock forms.compute_formula(df, "=SUM(A1:B3)")
def test_execute_sum_simple_formula_rr():
    result = compute_one_formula(Ref(0, 0, 2, 1), RefType.RR)
    real_result = pd.DataFrame(np.full(48, 6.0))
    assert np.array_equal(result.df.iloc[0:48].values, real_result.values)


# try to mock forms.compute_formula(df, "=SUM(A$1:B$3)")
def test_execute_sum_simple_formula_ff():
    result = compute_one_formula(Ref(0, 0, 2, 1), RefType.FF)
    real_result = pd.DataFrame(np.full(50, 6.0))
    assert np.array_equal(result.df.values, real_result.values)


# try to mock forms.compute_formula(df, "=SUM(A$1:B3)")
def test_execute_sum_simple_formula_fr():
    result = compute_one_formula(Ref(0, 0, 2, 1), RefType.FR)
    real_result = pd.DataFrame(np.arange(106, 202, 2))
    assert np.array_equal(result.df.iloc[0:48].values, real_result.values)


# try to mock forms.compute_formula(df, "=SUM(A1:B$100)")
def test_execute_sum_simple_formula_rf():
    result = compute_one_formula(Ref(0, 0, 100, 1), RefType.RF)
    real_result = pd.DataFrame(np.arange(100, 0, -2))
    assert np.array_equal(result.df.values, real_result.values)


# try to mock forms.compute_formula(df, "=SUM($A$1, SUM(A1:B3))")
def test_execute_sum_complex_formula():
    global table
    root = FunctionExecutionNode(Function.SUM, RefType.RR, RefDirection.DOWN)
    parent = FunctionExecutionNode(Function.SUM, RefType.RR, RefDirection.DOWN)
    child1 = RefExecutionNode(Ref(0, 0), table, RefType.FF, RefDirection.DOWN)
    child2 = RefExecutionNode(Ref(0, 0, 2, 1), table, RefType.RR, RefDirection.DOWN)
    parent.children = [child2]
    child1.set_exec_context(ExecutionContext(50, 100))
    child2.set_exec_context(ExecutionContext(50, 100))
    sub_result = sum_df_executor(parent)
    real_result = pd.DataFrame(np.full(48, 6.0))
    assert np.array_equal(sub_result.df.iloc[0:48].values, real_result.values)

    ref_node = create_intermediate_ref_node(sub_result, parent)
    root.children = [child1, ref_node]
    child1.parent = root
    child2.parent = ref_node
    ref_node.set_exec_context(ExecutionContext(0, 50))
    result = sum_df_executor(root)

    real_result = pd.DataFrame(np.full(48, 7.0))
    assert np.array_equal(result.df.iloc[0:48].values, real_result.values)