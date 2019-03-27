## Openstask Note

```sh
#cloud-config 
password: meditech2018 
chpasswd: { expire: False } 
ssh_pwauth: True
```

Ubuntu 14.04

```sh
#cloud-config
# For Ubuntu-14.04 cloudimage
apt_sources:
- source: "cloud-archive:mitaka"
packages:
- trove-guestagent
- mysql-server-5.5
write_files:
- path: /etc/sudoers.d/trove
  content: |
    Defaults:trove !requiretty
    trove ALL=(ALL) NOPASSWD:ALL
runcmd:
- stop trove-guestagent
- cat /etc/trove/trove-guestagent.conf /etc/trove/conf.d/guest_info.conf >/etc/trove/trove.conf
- start trove-guestagent
```

### Ubuntu 16.04 add swap file

```sh
#!/bin/bash
echo -e "meditech2019\nmeditech2019" | passwd  root
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
cp /etc/fstab /etc/fstab.bak
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sysctl vm.swappiness=10
echo vm.swappiness=10 >> /etc/sysctl.conf
sysctl vm.vfs_cache_pressure=50
echo vm.vfs_cache_pressure=50 >> /etc/sysctl.conf
```