from copy import deepcopy

import pytest

from eight_bit_computer.language import utils


@pytest.mark.parametrize("test_input,expected", [
    (
        "",
        [
        ],

    ),
    (
        "    ",
        [
        ],

    ),
    (
        " \t   ",
        [
        ],

    ),
    (
        "hello",
        [
            "hello",
        ],

    ),
    (
        "he./llo world",
        [
            "he./llo",
            "world",
        ],

    ),
    (
        "foo\tbar    baz    ",
        [
            "foo",
            "bar",
            "baz",
        ],

    )
])
def test_get_tokens_from_line(test_input, expected):
    assert utils.get_tokens_from_line(test_input) == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        [
        ],
        "",
    ),
    (
        [
            "hello",
        ],
        "\"hello\"",
    ),
    (
        [
            "foo",
            "bar",
        ],
        "\"foo\", \"bar\"",
    ),
    (
        [
            "foo",
            "bar",
            "   ",
        ],
        "\"foo\", \"bar\", \"   \"",
    ),
])
def test_add_quotes_to_strings(test_input, expected):
    assert utils.add_quotes_to_strings(test_input) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("[A]", "A"),
    ("[ACC]", "ACC"),
    ("[$variable]", "$variable"),
    ("[@label]", "@label"),
    ("[#number]", "#number"),
])
def test_extract_memory_position(test_input, expected):
    assert utils.extract_memory_position(test_input) == expected


@pytest.mark.parametrize("test_input,expected", [
    ("[A]", True),
    ("[ACC]", True),
    ("[$variable]", True),
    ("[$variable[10]]", True),
    ("[@label]", True),
    ("[#number]", True),
    ("A", False),
    ("$hello", False),
    ("[oops", False),
    ("oops]", False),
    ("$variable[10]", False),
])
def test_is_memory_index(test_input, expected):
    assert utils.is_memory_index(test_input) == expected


def gen_test_match_and_parse_args_input_0():
    """
    Single module arg
    """

    line_args = ["A"]

    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = False
    op_arg_def["value"] = "A"

    op_args_def.append(op_arg_def)

    expected_match = True
    expected_args = deepcopy(op_args_def)

    return (line_args, op_args_def, expected_match, expected_args)


def gen_test_match_and_parse_args_input_1():
    """
    All kinds
    """

    line_args = ["A", "[B]", "#123", "[#123]"]

    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = False
    op_arg_def["value"] = "A"

    op_args_def.append(op_arg_def)

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = True
    op_arg_def["value"] = "B"

    op_args_def.append(op_arg_def)

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "constant"
    op_arg_def["is_memory_location"] = False
    op_arg_def["value"] = ""

    op_args_def.append(op_arg_def)

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "constant"
    op_arg_def["is_memory_location"] = True
    op_arg_def["value"] = ""

    op_args_def.append(op_arg_def)

    expected_match = True
    expected_args = deepcopy(op_args_def)
    expected_args[2]["value"] = "#123"
    expected_args[3]["value"] = "#123"

    return (line_args, op_args_def, expected_match, expected_args)


def gen_test_match_and_parse_args_input_2():
    """
    Not module memref
    """

    line_args = ["A"]

    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = True
    op_arg_def["value"] = "A"

    op_args_def.append(op_arg_def)

    expected_match = False
    expected_args = []

    return (line_args, op_args_def, expected_match, expected_args)


def gen_test_match_and_parse_args_input_3():
    """
    Not constant memref
    """

    line_args = ["#123"]

    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "constant"
    op_arg_def["is_memory_location"] = True
    op_arg_def["value"] = ""

    op_args_def.append(op_arg_def)

    expected_match = False
    expected_args = []

    return (line_args, op_args_def, expected_match, expected_args)


def gen_test_match_and_parse_args_input_4():
    """
    Arg length mismatch
    """

    line_args = ["A", "B"]

    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = False
    op_arg_def["value"] = "A"

    op_args_def.append(op_arg_def)

    expected_match = False
    expected_args = []

    return (line_args, op_args_def, expected_match, expected_args)


@pytest.mark.parametrize(
    "line_args,op_args_def,expected_match,expected_args",
    [
        gen_test_match_and_parse_args_input_0(),
        gen_test_match_and_parse_args_input_1(),
        gen_test_match_and_parse_args_input_2(),
        gen_test_match_and_parse_args_input_3(),
        gen_test_match_and_parse_args_input_4(),
    ]
)
def test_match_and_parse_args(
    line_args, op_args_def, expected_match, expected_args
):
    match, parsed_args = utils.match_and_parse_args(line_args, op_args_def)
    assert match == expected_match
    assert parsed_args == expected_args


def gen_test_match_and_parse_line_input_0():
    """
    Match second args def
    """

    line = "COPY A B"
    opcode = "COPY"

    op_args_defs = []

    # Def 0
    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = False
    op_arg_def["value"] = "C"

    op_args_def.append(op_arg_def)

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = False
    op_arg_def["value"] = "D"

    op_args_def.append(op_arg_def)

    op_args_defs.append(op_args_def)

    # Def 1
    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = False
    op_arg_def["value"] = "A"

    op_args_def.append(op_arg_def)

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = False
    op_arg_def["value"] = "B"

    op_args_def.append(op_arg_def)

    op_args_defs.append(op_args_def)

    expected_match = True
    expected_args = deepcopy(op_args_defs[1])

    return (line, opcode, op_args_defs, expected_match, expected_args)


def gen_test_match_and_parse_line_input_1():
    """
    No args
    """
    line = "NOOP"
    opcode = "NOOP"

    op_args_defs = []

    expected_match = True
    expected_args = []

    return (line, opcode, op_args_defs, expected_match, expected_args)


def gen_test_match_and_parse_line_input_2():
    """
    Module mem ref
    """

    line = "JUMP [A]"
    opcode = "JUMP"

    op_args_defs = []

    # Def 0
    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "module_name"
    op_arg_def["is_memory_location"] = True
    op_arg_def["value"] = "A"

    op_args_def.append(op_arg_def)

    op_args_defs.append(op_args_def)

    expected_match = True
    expected_args = deepcopy(op_args_defs[0])

    return (line, opcode, op_args_defs, expected_match, expected_args)


def gen_test_match_and_parse_line_input_3():
    """
    constant mem ref
    """

    line = "JUMP [$variable]"
    opcode = "JUMP"

    op_args_defs = []

    # Def 0
    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "constant"
    op_arg_def["is_memory_location"] = True
    op_arg_def["value"] = ""

    op_args_def.append(op_arg_def)

    op_args_defs.append(op_args_def)

    expected_match = True
    expected_args = deepcopy(op_args_defs[0])
    expected_args[0]["value"] = "$variable"

    return (line, opcode, op_args_defs, expected_match, expected_args)


def gen_test_match_and_parse_line_input_4():
    """
    constant
    """

    line = "JUMP @label"
    opcode = "JUMP"

    op_args_defs = []

    # Def 0
    op_args_def = []

    op_arg_def = utils.get_arg_def_template()
    op_arg_def["value_type"] = "constant"
    op_arg_def["is_memory_location"] = False
    op_arg_def["value"] = ""

    op_args_def.append(op_arg_def)

    op_args_defs.append(op_args_def)

    expected_match = True
    expected_args = deepcopy(op_args_defs[0])
    expected_args[0]["value"] = "@label"

    return (line, opcode, op_args_defs, expected_match, expected_args)


@pytest.mark.parametrize(
    "line,opcode,op_args_defs,expected_match,expected_args",
    [
        gen_test_match_and_parse_line_input_0(),
        gen_test_match_and_parse_line_input_1(),
        gen_test_match_and_parse_line_input_2(),
        gen_test_match_and_parse_line_input_3(),
        gen_test_match_and_parse_line_input_4(),

    ]
)
def test_match_and_parse_line(
    line, opcode, op_args_defs, expected_match, expected_args
):
    match, parsed_args = utils.match_and_parse_line(
        line, opcode, op_args_defs
    )
    assert match == expected_match
    assert parsed_args == expected_args



    # ##########
    # # Test 2 #
    # ##########
    # line = "SET A"
    # opcode = "LOAD"

    # op_args_defs = []

    # # Def 0
    # op_args_def = []

    # op_arg_def = utils.get_arg_def_template()
    # op_arg_def["value_type"] = "module_name"
    # op_arg_def["is_memory_location"] = False
    # op_arg_def["value"] = "A"

    # op_args_def.append(op_arg_def)

    # op_arg_def = utils.get_arg_def_template()
    # op_arg_def["value_type"] = "module_name"
    # op_arg_def["is_memory_location"] = False
    # op_arg_def["value"] = "B"

    # op_args_def.append(op_arg_def)

    # op_args_defs.append(op_args_def)

    # expected_match = False
    # expected_args = []

    # tests.append((line, opcode, op_args_defs, expected_match, expected_args))

    # return tests