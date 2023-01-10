#!/usr/bin/env python3

import subprocess
import tempfile
import shutil
import sys
import os

def run(target, odir, *args):
    with tempfile.TemporaryDirectory() as tmp_dir:
        ifile = os.path.join(tmp_dir, os.path.basename(target))
        shutil.copy2(target, ifile)

        docker_ifile = os.path.join("/tmp", os.path.basename(target))

        # run binwalk
        cmd  = ["docker", "run", "-v", f"{tmp_dir}:/tmp/", "--rm", "-w", "/tmp", "binwalk"]
        cmd += ["binwalk"] + list(args) + [docker_ifile]
        subprocess.check_call(cmd)

        # change ownership of result
        cmd  = ["docker", "run", "-v", f"{tmp_dir}:/tmp/", "--rm", "binwalk"]
        cmd += ["chown", "-R", "{u}:{u}".format(u=str(os.getuid())), "/tmp"]
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

def run_args_only(*args):
    cmd  = ["docker", "run", "--rm", "binwalk"]
    cmd += ["binwalk"] + list(args)
    subprocess.check_call(cmd)

if __name__ == "__main__":
    # TODO: support multiple targets
    # TODO: support command line switches that specify files (e.g., -f)

    args = sys.argv[1:]
    target = args[-1]

    if not os.path.exists(target):
        run_args_only(*args)
        exit(0)

    if not os.path.isfile(target):
        print(f"!Err: invalid input file [not a file] {target}")
        exit(1)

    odir = os.path.realpath(os.getcwd())
    args = args[:-1]
    run(target, odir, *args)
