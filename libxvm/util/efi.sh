#!/bin/sh
curl -sSL -o BHYVE_UEFI_20160526.fd  http://people.freebsd.org/~grehan/bhyve_uefi/BHYVE_UEFI_20160526.fd
/Volumes/datavol/src/xhyve/build/xhyve \
	-A \
	-s 0:0,hostbridge \
	-s 31,lpc \
	-l com1,stdio \
	-m 1G \
        -f bootrom,BHYVE_UEFI_20160526.fd,,

