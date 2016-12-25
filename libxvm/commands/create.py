import subprocess
import os
import humanfriendly
from .common import argparser, exit_with_failure

def run(cmd):
    p = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = p.communicate()
    ret = p.wait()
    if ret != 0:
        raise Exception('command failed', cmd)
    return stdout, stderr

def create_disk(vmdir, name, size):
    run("dd if=/dev/zero of='{}/{}' bs={} count=1".format(vmdir, name, size))

def meh():
    ISO='/Volumes/datavol/debian-8.6.0-amd64-netinst.iso'
    VMS='/Volumes/datavol/vms'
    NAME='Test2'

    VMDIR='{}/{}'.format(VMS, NAME)
    HDD='{}/hdd.img'.format(VMDIR)
    CD='{}/cd.img'.format(VMDIR)
    if not os.path.exists(VMDIR):
        os.makedirs(VMDIR)


    run('dd if=/dev/zero bs=2k count=1 of="{}"'.format(CD))
    run("dd if='{}' bs=2k skip=1 >> '{}'".format(ISO, CD))
    out, err = run("hdiutil attach '{}'".format(CD))
    disk=out.split()[0]
    mnt=b' '.join(out.split()[1:]).decode()
    print('disk={} mnt={}'.format(disk, mnt))
    run('cp \'{}/install.amd/vmlinuz\' {}'.format(mnt, VMDIR))
    run('cp \'{}/install.amd/initrd.gz\' {}'.format(mnt, VMDIR))
    #run("dd if=/dev/zero of='{}' bs=2000m count=1".format(HDD))

    KERNEL="{}/vmlinuz".format(VMDIR)
    INITRD="{}/initrd.gz".format(VMDIR)
    CMDLINE="earlyprintk=serial console=ttyS0 acpi=off root=/dev/vda1 ro"
    MEM="-m 1G"
    SMP="" #-c 2"
    NET="-s 2:0,virtio-net"
    IMG_CD=""
    IMG_CD="-s 3,ahci-cd,{}".format(ISO)
    IMG_HDD="-s 4,virtio-blk,'{}'".format('Test.dmg')
    PCI_DEV="-s 0:0,hostbridge -s 31,lpc"
    LPC_DEV="-l com1,stdio"
    ACPI="-A"

    cmd = "sudo /Volumes/datavol/src/xhyve/build/xhyve {} {} {} {} {} {} {} {} -f kexec,{},{},\"{}\"".format(
        ACPI, MEM, SMP, PCI_DEV, LPC_DEV, NET, IMG_CD, IMG_HDD, KERNEL, INITRD, CMDLINE)

    ret = subprocess.call(cmd, shell=True)


def create(argparser=argparser):
    #ISO='/Volumes/datavol/debian-8.6.0-amd64-netinst.iso'
    vms_dir='/Volumes/datavol/vms'
    argparser.add_argument('name', help='Name of vm')
    argparser.add_argument('--memory', help='How much memory (ram) should be assigned by default')
    argparser.add_argument('--disk', action='append', help='Create a disk image of this size')
    ns, argv = argparser.parse_known_args()
    if ns.help:
        argparser.print_help()
        sys.exit(0)
    if not ns.disk:
        exit_with_failure("Please specify at least one disk")
    print('name:\t{}'.format(ns.name))
    for diskconf in ns.disk:
        name, size = diskconf.split(',')
        print('disk:\t{}\t{}'.format(name, size))
    vmdir = '{}/{}'.format(vms_dir, ns.name)
    if not os.path.exists(vmdir):
        os.makedirs(vmdir)
    for diskconf in ns.disk:
        name, human_size = diskconf.split(',')
        size = humanfriendly.parse_size(human_size)
        create_disk(vmdir, name, size)
