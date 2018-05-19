#!/usr/bin/env python
import os
import subprocess, shlex
import json
import sys
from glob import glob

def sanitize_path(path):
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    return path

def main(opt):
    errors = []
    for changed_file in glob("{0}/*.json".format(sanitize_path(opt.packer_dir))):
        print changed_file
        try:
            with open(changed_file, 'r') as packer_build:
                data = json.loads(packer_build.read())
            exit_code = os.system("packer build {0} 2>/tmp/{1}".format(changed_file, os.path.basename(changed_file)))
            if exit_code > 0:
                with open("/tmp/{0}".format(changed_file)) as errors:
                    errors.append(dict(file=changed_file, reason=str(errors.read())))
        except Exception, e:
            if changed_file.endswith(".json"):
                errors.append(dict(file=changed_file, reason=str(e)))
            else:
                continue
    if len(errors):
        for error in errors:
            sys.stderr.write("{0}\n".format(error.get("file")))
            sys.stderr.write("{0}\n".format(error.get("reason")))
            sys.stderr.write("{0}\n".format(error.get("message")))
        sys.stderr.write("Could not parse or build these files...\n")
        #sys.stderr.write("\n".join(json.dumps(errors, separators=(',', ':'), indent=4, sort_keys=True)))
        sys.exit(1)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--packer-dir', dest='packer_dir')
    opt, args = parser.parse_args()
    main(opt)


