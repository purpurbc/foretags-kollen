import ast

def str_to_list(s):
    if s is None or str(s).strip() == "":
        return []
    try:
        v = ast.literal_eval(str(s))
        return v if isinstance(v, list) else [v]
    except Exception:
        return []