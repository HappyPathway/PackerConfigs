#!/usr/bin/env python
import os
import subprocess, shlex
import json
import sys

def main():
	errors = []
    p = subprocess.Popen(shlex.split("git diff --name-only $TRAVIS_COMMIT_RANGE"), 
    	stdout=subprocess.PIPE, 
    	stderr=subprocess.PIPE)
    out, err = p.communicate()
    for changed_file in out.splitlines()
    	try:
    		with open(changed_file, 'r') as packer_build:
    			data = json.loads(packer_build.read())
    		p = subprocess.Popen(shlex.split("packer build {0}".format(changed_file))
    								stdout=subprocess.PIPE,
    								stderr=subprocess.PIPE)
    		out, err = p.communicate()
    		if p.returncode > 0:
    			errors.append(changed_file)
    	except:
    		if changed_file.endswith(".json"):
    			errors.append(changed_file)
    		else:
    			continue
    if len(errors):
    	sys.stderr.write("Could not parse or build these files...\n")
    	sys.stderr.write("\n".join(errors))
    	sys.stderr.write("END\n")
    	sys.exit(1)

  if __name__ == '__main__':
  	main()
    			

