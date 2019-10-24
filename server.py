import sys
from pds.backend.plugin import init_plugin

def on_starting(server):
    print("starting server")
    sys.stdout.flush()
    init_plugin()
