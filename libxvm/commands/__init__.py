import os
from .common import argparser
from .create import create
from .start import start

def list_commands(argparser=argparser, show_help=False):
    if show_help:
        argparser.print_help()
        sys.exit(0)
    print("Available commands are:")
    for i in COMMANDS:
        print("  " + i)

def destroy(argparser=argparser):
    vms_dir='/Volumes/datavol/vms'
    argparser.add_argument('name', help='Name of vm')
    ns, argv = argparser.parse_known_args()
    if ns.help:
        argparser.print_help()
        sys.exit(0)
    vmdir = os.path.join(vms_dir, ns.name)
    if os.path.exists(vmdir):
        os.remove()
    else:
        exit_with_failure("vm does not exist")

def list_vms(argparser=argparser):
    vms_dir='/Volumes/datavol/vms'
    ns, argv = argparser.parse_known_args()
    if ns.help:
        argparser.print_help()
        sys.exit(0)
    for root, dirs, files in os.walk(vms_dir):
        break
    for vmdir in dirs:
        fulldir = os.path.join(vms_dir, vmdir)
        if os.path.exists(os.path.join(fulldir, 'config.yaml')):
            print(vmdir)

COMMANDS = {
    'commands': list_commands,
    'list': list_vms,
    'create': create,
    'remove': destroy,
    'up': start,
    'down': start,
}
