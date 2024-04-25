from urllib.parse import urlparse
from pyston import PystonClient, File


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


async def mathematic(string):
    calculation = f"""
import sympy

print(sympy.sympify({string}))
    """
    calculator = File(calculation, filename="calculator.py")
    sandbox = PystonClient()
    output = await sandbox.execute("python", [calculator])
    return output
