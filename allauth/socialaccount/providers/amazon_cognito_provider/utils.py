def convert_to_python_bool_if_value_is_json_string_bool(s):
    if s == "true":
        return True
    elif s == "false":
        return False

    return s
