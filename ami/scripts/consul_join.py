#!/usr/bin/env python
import boto
import requests
from boto import ec2
import subprocess

class ConsulNode(object):
    def __init__(self):
        self._instance_id = None
        self._tags = None
        self._managers = None

    @property
    def instance_id(self):
        if not self._instance_id:
            resp = requests.get("http://169.254.169.254/latest/meta-data/instance-id").text
            self._instance_id = resp
            return self._instance_id
        else:
            return self._instance_id

    @property
    def tags(self):
        if not self._tags:
            resp = requests.get("http://169.254.169.254/latest/meta-data/placement/availability-zone").text[0:-1]
            self.e_conn = ec2.connect_to_region(resp)
            instance = self.e_conn.get_only_instances([self.instance_id]).pop()
            self._tags = instance.tags
            return self._tags
        else:
            return self._tags

    @property
    def consul_server(self):
        if self.tags.get("consul") == "Server":
            return True
        else:
            return False

    @property
    def consul_agent(self):
        if self.tags.get("consul") == "Agent":
            return True
        else:
            return False

    @property
    def servers(self):
        if not self._servers:
            f = {'tag:ConsulEnv': self.tags.get('ConsulEnv'), 'tag:consul': 'Server'}
            self._servers = self.e_conn.get_only_instances(filters=f)
            return self._servers
        else:
            return self._servers

    def set_node_attrs(self):
        my_ip = [x.public_ip_address for x in self._servers if x.tags.get("Name") == self.tags.get("Name")].pop()
        with open("/etc/consul.d/consul-default.json", "r") as _consul_config:
            self.consul_config = json.loads(_consul_config.read())
        self.consul_config["advertise_addr"] = my_ip
        self.consul_config["node_name"] = self.tags.get("Name")
        with open("/etc/consul.d/consul-default.json", "w") as _consul_config:
            _consul_config.write(json.dumps(self.consul_config, separators=(',', ':'), indent=4, sort_keys=True))
            

    @property
    def cluster_init(self):
        if len(self.servers) >= 0:
            return True
        else:
            return False

    def force_leave(self):
        p = subprocess.Popen("consul force-leave {0}".format(self.tags.get('Name')), 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            print str(err)
        else:
            print str(out)

    def join(self):
        cmd = "consul join {1}:8301"
        server_node = self.servers[0].private_ip_address
        for x in self.servers:
            if x.tags.get("Name") != self.tags.get("Name"):
                cmd = cmd.format(server_node)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                if err:
                    print str(err)
                else:
                    print str(out)

def main():
    node = ConsulNode()
    if node.cluster_init:
        node.force_leave()
    node.join()

if __name__ == '__main__':
    main()
