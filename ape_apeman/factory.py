# ape_manager class factory may be used to defer APE() initialization


def APE(*args, **kwargs):
    """return a managed ape instance"""
    from ape_apeman.manager import APE

    return APE(*args, **kwargs)
