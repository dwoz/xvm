'''
Utility methods for working with the ext2 family of filesystems
'''
import os
import subprocess

DEBUGFS='/usr/local/Cellar/e2fsprogs/1.42.13/sbin/debugfs'

def parse_ls_line(line):
    inode, line = line.strip().split(b' ', 1)
    perms, line = line.strip().split(b' ', 1)
    kind, line = line.strip().split(b' ', 1)
    p1, line = line.strip().split(b' ', 1)
    p2, line = line.strip().split(b' ', 1)
    size, line = line.strip().split(b' ', 1)
    date, line = line.strip().split(b' ', 1)
    time, x = line.strip().split(b' ', 1)
    filename = x.strip()
    return inode, perms, kind, p1, p2, size, date, time, filename


def extract_file(disk, extract_file, to_file, exc=DEBUGFS):
    extract_dir = os.path.dirname(extract_file)
    extract_filename = os.path.basename(extract_file)
    output = subprocess.check_output(
        "echo 'ls -l {}' |{} -f - {}".format(extract_dir, exc, disk),
        shell=True, stderr=subprocess.PIPE
    )
    cleanout = output.strip()
    lines = cleanout.split(b'\n')[1:]
    for l in lines:
        inode, perms, kind, p1, p2, size, date, time, filename = parse_ls_line(l)
        if filename.decode() == extract_filename:
            int_inode = int(inode.decode())
            subprocess.check_output(
                "echo 'dump <{}> {}' |{} -f - {}".format(int_inode, to_file, exc, disk),
                shell=True, stderr=subprocess.PIPE
            )
            return
    raise Exception("File not found")

def attach_image(image):
    output = subprocess.check_output('hdiutil attach -imagekey diskimage-class=CRawDiskImage -nomount  {}'.format(image), shell=True)
    lines = output.decode().strip().split('\n')
    partitions = []
    for l in lines:
        partitions.append([x.strip() for x in l.split('\t')])
    return partitions

def detach_image(device):
    subprocess.check_output('hdiutil detach {}'.format(device), shell=True)
