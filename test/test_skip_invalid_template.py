from jinja2 import DebugUndefined, Environment
import json
import pytest

import hiyapyco
from hiyapyco import HiYaPyCoImplementationException

y1 = """
---
test: test
yaml: from str 1
h:
    y1: 66
    y2: xyz
l:
    - l1
    - l2
"""
y2 = """
---
yaml: from str 2
h:
    y1: {}
    y3: DEF
l:
    - lll
"""


@pytest.mark.parametrize("skip, raise_exc, template, result", [
    (True, False, "invalid-{{template}", "invalid-{{template}"),
    (True, False, "docker-syntax-{{.Task.Id}}", "docker-syntax-{{.Task.Id}}"),
    (False, HiYaPyCoImplementationException, "invalid-{{template}", "invalid-{{template}"),
    (False, HiYaPyCoImplementationException, "docker-syntax-{{.Task.Id}}", "docker-syntax-{{.Task.Id}}"),
    (False, False, "test", "test"),
    (False, False, "test-{{test}}", "test-test"),
    (False, False, "'{{test}}'", "test"),
])
def test_skip(skip, raise_exc, template, result):
    def call_load():
        return hiyapyco.load(
            y1,
            y2.format(template),
            method=hiyapyco.METHOD_MERGE,
            failonmissingfiles=True,
            skip_invalid_templates=skip,
            interpolate=True
        )

    if raise_exc:
        with pytest.raises(raise_exc):
            call_load()
    else:
        conf = call_load()
        assert json.loads(json.dumps(conf)) == {'test': 'test', 'h': {'y1': result, 'y2': 'xyz', 'y3': 'DEF'},
                                                'l': ['l1', 'l2', 'lll'], 'yaml': 'from str 2'}


y3 = """
test: {}
"""


@pytest.mark.parametrize("skip, raise_exc, template, jinjaenv", [
    (True, False, "replace-base", None),
    (True, False, "docker-syntax-{{.Task.Id}}", None),
    (False, HiYaPyCoImplementationException, "docker-syntax-{{.Task.Id}}", None),
    (False, False, "replace-base", None),
    (False, False, "replace-base", DebugUndefined)
])
def test_skip_yaml_file(skip, raise_exc, template, jinjaenv):
    def call_load():
        if jinjaenv:
            hiyapyco.jinja2env = Environment(undefined=DebugUndefined)
        return hiyapyco.load(
            "./test/base.yaml",
            y3.format(template),
            method=hiyapyco.METHOD_MERGE,
            failonmissingfiles=True,
            skip_invalid_templates=skip,
            interpolate=True
        )

    if raise_exc:
        with pytest.raises(raise_exc):
            call_load()
    else:
        conf = call_load()
        assert json.loads(json.dumps(conf)) == {'array': ['base1', 'base2'],
                                                'common_key': {'common_subkey_deep': 'one', 'missing_key_base': 'val2'},
                                                'deeplist': [{'d1': {'d1k1': 'v1', 'd1k2': 'v2'}},
                                                             {'d2': {'d2k1': 'x1', 'd2k2': 'x2'}},
                                                             {'d31': {'a': 'A', 'b': 'B', 'c': 'C'},
                                                              'd32': {'a': 'A2', 'b': 'B2'}}],
                                                'deepmap': {'l1k1': {'l2k1': 'xyz', 'l2k2': 'abc'},
                                                            'l1k2': {'l2k1': 'bli', 'l2k2': 'bla', 'l2k3': 'blub'}},
                                                'hash': {'k1': 'b1', 'k2': 'b2'},
                                                'int': 1,
                                                'missing_key': 'one',
                                                'singel': 'base',
                                                'test': template}
