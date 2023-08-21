from urllib.parse import urlparse

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