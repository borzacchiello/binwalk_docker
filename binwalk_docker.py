#!/usr/bin/env python3

import subprocess
import tempfile
import shutil
import sys
import os

def run(target, *args):
    odir = os.path.dirname(target)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = "/dev/shm"
        ifile = os.path.join(tmp_dir, os.path.basename(target))
        shutil.copy2(target, ifile)

        docker_ifile = os.path.join("/tmp", os.path.basename(target))

        # run binwalk
        cmd  = ["docker", "run", "-v", f"{tmp_dir}:/tmp/", "--rm", "-w", "/tmp", "binwalk"]
        cmd += ["binwalk"] + list(args) + [docker_ifile]
        print("running:", " ".join(cmd))
        subprocess.check_call(cmd)

        # change ownership of result
        cmd  = ["docker", "run", "-v", f"{tmp_dir}:/tmp/", "--rm", "binwalk"]
        cmd += ["chown", "-R", "{u}:{u}".format(u=str(os.getuid())), "/tmp"]
        print("running:", " ".join(cmd))
        subprocess.check_call(cmd)

        # copy the result
        for filename in os.listdir(tmp_dir):
            f = os.path.join(tmp_dir, filename)
            if f == ifile:
                continue

            if os.path.isfile(f):
                shutil.copy2(f, os.path.join(odir, filename))
            else:
                shutil.copytree(f, os.path.join(odir, filename))

if __name__ == "__main__":
    args = sys.argv[1:]
    target = args[-1]

    if not os.path.exists(target) and os.path.isfile(target):
        print(f"!Err: invalid input file {target}")
        exit(1)

    args = args[:-1]
    run(target, *args)
