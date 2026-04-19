def is_float(x):
    try:
        float(x)
        return True
    except Exception:
        return False
