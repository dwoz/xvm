#!/usr/bin/env python
import subprocess
import sys
import os
import yaml
from ..util import iso, ext
from .common import argparser, exit_with_failure

VMS='/Volumes/datavol/vms'


def parse_extract_config(value):
    disk_image, part = value.rsplit(',', 1)
    return disk_image, part


def forkit():
    pid = os.fork()
    if pid > 0:
        os._exit(0)
    os.setsid()
    pid = os.fork()
    if pid > 0:
        os._exit(0)


def kexec_args(config):
    opts = config['kexec']
    args = []
    kernel = opts['kernel']
    initrd = opts['initrd']
    extract_kernel = opts.get('extract_kernel', '')
    if extract_kernel:
        try:
            disk_image, part = parse_extract_config(extract_kernel)
        except:
            exit_with_failure("Invalid extract_kernel parameter")
        parts = ext.attach_image(os.path.join(config['dir'], disk_image))
        mount = parts[int(part)][0]
        ext.extract_file(mount, opts['initrd'], os.path.join(config['dir'], '.initrd'))
        initrd = '.initrd'
        ext.extract_file(mount, opts['kernel'], os.path.join(config['dir'], '.kinit'))
        kernel = '.kinit'
        ext.detach_image(parts[0][0])
    kernel_path = os.path.join(config['dir'], kernel)
    initrd_path = os.path.join(config['dir'], initrd)
    args.append('-f')
    args.append('kexec,{},{},{}'.format(kernel_path, initrd_path, opts['cmdline']))
    return args

def expand_paths(opts, expand_dir):
    try:
        slot, emulation, conf = opts.split(',', 2)
    except ValueError:
        # pass through values which don't have three parts
        return opts
    if emulation in ['virtio-blk', 'ahci-cd', 'ahci-hd']:
        if conf[0] != '/':
            conf = os.path.join(expand_dir, conf)
    return ','.join([slot, emulation, conf])

def command_args(config, nostdio=False, mem_default='1G'):
    args = []
    uuid = config.get('uuid', None)
    if uuid:
        args.extend(['-U', uuid])
    acpi = config.get('acpi', False)
    if acpi:
        args.append('-A')
    for bus in config['pcibus']:
        args.extend(['-s', expand_paths(bus, config['dir'])])
    # Parse the device list and remove stdio if needed.
    devices = [x.strip() for x in config['devices'].split(',') if x.strip()]
    if nostdio:
        devices.remove('stdio')
    args.extend(['-l', ','.join(devices)])
    args.extend(['-m', config.get('memory', mem_default)])
    firmware = config['firmware']
    if firmware not in ['kexec']:
        raise Exception("Kernel type invalid or not implimented", kernel)
    args.extend(kexec_args(config))
    print(args)
    return args


def start(argparser=argparser):
    vms_dir='/Volumes/datavol/vms'
    argparser.add_argument('name', help='Name of vm')
    argparser.add_argument('-d', '--daemon', action='store_true', default=False, help='Daemonize')
    ns, argv = argparser.parse_known_args()
    if ns.help:
        argparser.print_help()
        sys.exit(0)
    # print('name:\t{}'.format(ns.name))
    vmdir = os.path.join(vms_dir, ns.name)
    config_file = os.path.join(vmdir, 'config.yaml')
    if not os.path.exists(config_file):
        exit_with_failure('Config file does not exist')
    with open(config_file) as fp:
        config = yaml.safe_load(fp)
    config['dir'] = vmdir
    cmd = ['/Volumes/datavol/src/xhyve/build/xhyve']
    if ns.daemon:
        cmd.extend(command_args(config, nostdio=True))
        forkit()
        stderr=subprocess.PIPE
        stdout=subprocess.PIPE
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = p.wait()
        print("xhyve finished: {}".format(ret))
        if ret != 0:
            print("xhyve stdout: {}".format(p.stdout.read()))
            print("xhyve stderr: {}".format(p.stderr.read()))
    else:
        cmd.extend(command_args(config))
        p = subprocess.Popen(cmd)
        ret = p.wait()
        print("xhyve finished: {}".format(ret))


if __name__ == '__main__':
    if '-d' in sys.argv:
        forkit()
        bg()
    else:
        fg()
