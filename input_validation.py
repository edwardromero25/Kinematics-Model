import re

def validate_float(value):
    return re.fullmatch(r"-?\d*\.?\d*", value) is not None

def validate_positive_float(value):
    return re.fullmatch(r"\d*\.?\d*", value) is not None