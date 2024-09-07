from urllib.parse import urlparse
import urllib
import urllib.parse
import requests
import d20
import traceback
import re


def is_link(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def unify(A, B):
    C = list(A)
    for b in B:
        if b not in C:
            C.append(b)
    return C


def mathematic(string):
    try:
        quoted_string = urllib.parse.quote_plus(string)
        calculator = f"https://api.mathjs.org/v4/?expr={quoted_string}"
        response = requests.get(calculator)
        output = response.text
    except Exception:
        output = "Timeout"
    return output


def roll(string, type, repeat: int = 1):
    pattern = r"`([^`]*)`"
    try:
        sub_result = ""
        for i in range(0, repeat):
            if i < repeat - 1:
                sub_result = sub_result + str(d20.roll(string)) + "\n"
            else:
                sub_result = sub_result + str(d20.roll(string))
        if type == "all":
            piv = re.findall(pattern, sub_result)
            secondary_result = [float(i) for i in piv]
            result = [sub_result, sum(secondary_result)]
        elif type == "only_result":
            piv = re.findall(pattern, sub_result)
            secondary_result = [float(i) for i in piv]
            result = sum(secondary_result)
        elif type == "only_string":
            result = sub_result
        else:
            result = "Invalid Argument"
    except traceback:
        traceback.print_exc
        result = "Invalid Argument"

    return result
