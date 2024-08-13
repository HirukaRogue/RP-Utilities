from urllib.parse import urlparse
import urllib
import urllib.parse
import requests


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
