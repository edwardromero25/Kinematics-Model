import re

def is_valid_float(value):
    return re.fullmatch(r"-?\d*\.?\d*", value) is not None

def is_valid_positive_float(value):
    return re.fullmatch(r"\d*\.?\d*", value) is not None