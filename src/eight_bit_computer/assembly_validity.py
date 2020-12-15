"""
Validity checks on the processed assembly lines
"""

from .exceptions import AssemblyError

ERROR_TEMPLATE = "Error processing line {line_no} ({line}): {details}"


def check_structure_validity(asm_line_infos):
    """
    Check the processed assembly lines for consistency/correctness.

    Args:
        asm_line_infos (list(dict)): List of dictionaries (conforming to
            :func:`~.get_assembly_line_template`) with information about all
            the lines in the assembly file.
    """
    check_multiple_label_defs(asm_line_infos)
    check_multiple_label_assignment(asm_line_infos)
    check_undefined_label_ref(asm_line_infos)
    check_multiple_variable_def(asm_line_infos)
    check_overlapping_variables(asm_line_infos)
    check_undefined_variable_ref(asm_line_infos)
    check_num_instruction_bytes(asm_line_infos)


def check_multiple_label_defs(asm_line_infos):
    """
    Check if the same label been defined more than once.

    Args:
        asm_line_infos (list(dict)): List of dictionaries (conforming to
            :func:`~.get_assembly_line_template`) with information about all
            the lines in the assembly file.
    Raises:
        AssemblyError: If the same label been defined more than once.
    """

    labels = set()
    label_lines = {}
    for asm_line_info in asm_line_infos:
        if asm_line_info["defines_label"]:
            label = asm_line_info["defined_label"]
            if label in labels:
                details = (
                    "The label: \"{label}\" has already been defined on "
                    "line {prev_line}.".format(
                        line_no=asm_line_info["line_no"],
                        label=label,
                        prev_line=label_lines[label],
                    )
                )
                msg = ERROR_TEMPLATE.format(
                    line_no=asm_line_info["line_no"],
                    line=asm_line_info["raw"],
                    details=details,
                )
                raise AssemblyError(msg)
            else:
                labels.add(label)
                label_lines[label] = asm_line_info["line_no"]


def check_multiple_label_assignment(asm_line_infos):
    """
    Check if a single line been assigned more than one label.

    Args:
        asm_line_infos (list(dict)): List of dictionaries (conforming to
            :func:`~.get_assembly_line_template`) with information about all
            the lines in the assembly file.
    Raises:
        AssemblyError: If a single line been assigned more than one
            label.
    """

    label_queued = False
    last_label = ""
    for asm_line_info in asm_line_infos:
        if label_queued and asm_line_info["defines_label"]:
            details = (
                "There is already a label ({label}) queued for "
                "assignment to the next instruction.".format(
                    label=last_label
                )
            )
            msg = ERROR_TEMPLATE.format(
                line_no=asm_line_info["line_no"],
                line=asm_line_info["raw"],
                details=details,
            )
            raise AssemblyError(msg)

        if asm_line_info["defines_label"]:
            label_queued = True
            last_label = asm_line_info["defined_label"]

        if asm_line_info["has_machine_code"] and label_queued:
            label_queued = False


def check_undefined_label_ref(asm_line_infos):
    """
    Check if an operation is using a label that hasn't been defined.

    Args:
        asm_line_infos (list(dict)): List of dictionaries (conforming to
            :func:`~.get_assembly_line_template`) with information about all
            the lines in the assembly file.
    Raises:
        AssemblyError: If an operation is using a label that hasn't
            been defined.
    """

    # Gather labels
    labels = []
    for asm_line_info in asm_line_infos:
        if asm_line_info["defines_label"]:
            labels.append(asm_line_info["defined_label"])

    for asm_line_info in asm_line_infos:
        if asm_line_info["has_machine_code"]:
            for mc_byte_info in asm_line_info["mc_bytes"]:
                if (mc_byte_info["byte_type"] == "constant"
                        and mc_byte_info["constant_type"] == "label"
                        and mc_byte_info["constant"] not in labels):
                    details = (
                        "This line is referencing a label ({label}) "
                        "that has not been defined.".format(
                            label=mc_byte_info["constant"]
                        )
                    )
                    msg = ERROR_TEMPLATE.format(
                        line_no=asm_line_info["line_no"],
                        line=asm_line_info["raw"],
                        details=details,
                    )
                    raise AssemblyError(msg)


def check_multiple_variable_def(asm_line_infos):
    """
    Has the same variable been defined multiple times.

    Args:
        asm_line_infos (list(dict)): List of dictionaries (conforming to
            :func:`~.get_assembly_line_template`) with information about all
            the lines in the assembly file.
    Raises:
        AssemblyError: If a variable has been defined more than once.
    """
    variables = set()
    variable_lines = {}
    for asm_line_info in asm_line_infos:
        if asm_line_info["defines_variable"]:
            variable = asm_line_info["defined_variable"]
            if variable in variables:
                details = (
                    "The variable: \"{variable}\" has already been defined on "
                    "line {prev_line}.".format(
                        variable=variable,
                        prev_line=variable_lines[variable],
                    )
                )
                msg = ERROR_TEMPLATE.format(
                    line_no=asm_line_info["line_no"],
                    line=asm_line_info["raw"],
                    details=details,
                )
                raise AssemblyError(msg)
            else:
                variables.add(variable)
                variable_lines[variable] = asm_line_info["line_no"]


def check_undefined_variable_ref(asm_line_infos):
    """
    Check instructions don't reference undefined variables

    Args:
        asm_line_infos (list(dict)): List of dictionaries (conforming to
            :func:`~.get_assembly_line_template`) with information about all
            the lines in the assembly file.
    Raises:
        AssemblyError: If a variable is referenced but not defined.
    """

    # Get the names of all the defined variables
    variables = set()
    for asm_line_info in asm_line_infos:
        if asm_line_info["defines_variable"]:
            variables.add(asm_line_info["defined_variable"])


    # Check the variables used in instructions
    for asm_line_info in asm_line_infos:
        if asm_line_info["has_machine_code"]:
            for mc_byte_info in asm_line_info["mc_bytes"]:
                if (mc_byte_info["byte_type"] == "constant"
                        and mc_byte_info["constant_type"] == "variable"
                        and mc_byte_info["constant"] not in variables):
                    details = (
                        "The variable: \"{variable}\" has not been defined".format(
                            variable=mc_byte_info["constant"]
                        )
                    )
                    msg = ERROR_TEMPLATE.format(
                        line_no=asm_line_info["line_no"],
                        line=asm_line_info["raw"],
                        details=details,
                    )
                    raise AssemblyError(msg)



def check_overlapping_variables(asm_line_infos):
    """
    Check none of the defined variables overlap with each other.

    Args:
        asm_line_infos (list(dict)): List of dictionaries (conforming to
            :func:`~.get_assembly_line_template`) with information about
            all the lines in the assembly file.
    Raises:
        AssemblyError: If two variables overlap in position with each
            other.
    """

    mem_pos_to_last_info = {}

    for asm_line_info in asm_line_infos:
        # Check for defined variable
        if asm_line_info["defines_variable"]:
            mem_pos = asm_line_info["defined_variable_location"]
            if mem_pos in mem_pos_to_last_info:
                details = (
                    "The variable: \"{new_variable}\" is defined at the same "
                    "location in memory as \"{old_variable}\" defined on line "
                    "{assembly_line}.".format(
                        new_variable=asm_line_info["defined_variable"],
                        old_variable=mem_pos_to_last_info[mem_pos]["defined_variable"],
                        assembly_line=mem_pos_to_last_info[mem_pos]["line_no"],
                    )
                )
                msg = ERROR_TEMPLATE.format(
                    line_no=asm_line_info["line_no"],
                    line=asm_line_info["raw"],
                    details=details,
                )
                raise AssemblyError(msg)
            else:
                mem_pos_to_last_info[mem_pos] = asm_line_info


def check_num_instruction_bytes(assembly_lines):
    """
    Check there aren't too many instruction_bytes.

    Args:
        asm_line_infos (list(dict)): List of dictionaries (conforming to
            :func:`~.get_assembly_line_template`) with information about all
            the lines in the assembly file.
    Raises:
        AssemblyError: If there are more instruction bytes than will
            fit in program memory.
    """
    bad_line_no = -1
    num_mc_bytes = 0
    for assembly_line in assembly_lines:
        if assembly_line["has_machine_code"]:
            for mc_byte in assembly_line["mc_bytes"]:
                num_mc_bytes += 1
                if num_mc_bytes > 255 and bad_line_no < 0:
                    bad_line_no = assembly_line["line_no"]

    if num_mc_bytes > 255:
        details = (
            "This operation brought the total number of machine "
            "code bytes above 255. The complete assembly code has "
            "resulted in {num_mc_bytes} bytes of machine code.".format(
                num_mc_bytes=num_mc_bytes,
            )
        )
        msg = ERROR_TEMPLATE.format(
            line_no=bad_line_no,
            line=assembly_line["raw"],
            details=details,
        )
        raise AssemblyError(msg)
