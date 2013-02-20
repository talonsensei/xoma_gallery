""" To use this in a standalone script do """
import sys, xoma_gallery

def prepare_environment():
    """Makes it easy to create standalone scripts that reference Django modules"""    
    sys.path.append(xoma_gallery.__path__[0])
    # set up the environment using the settings module
    from django.core.management import setup_environ
    import settings
    setup_environ(settings)
    
prepare_environment()
