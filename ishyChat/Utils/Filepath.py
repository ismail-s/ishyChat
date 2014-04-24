import os

def path_to(*args):
    """Takes as input a relative path, eg 'ishyChat/Server/something.json',
    
    or 'ishyChat', 'Server', 'something.json', all as separate arguments (both
    ways are/should be equivalent), and converts it into an absolute path."""
    # Need to work on this-way too hacky!!!!
    base_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.split(base_dir)[0]
    base_dir = os.path.split(base_dir)[0]
    return os.path.join(base_dir, *args)