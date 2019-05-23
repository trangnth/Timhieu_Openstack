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

CentOS 7

```sh
#cloud-config 
password: meditech2018 
chpasswd: { expire: False } 
ssh_pwauth: True

packages:
  - httpd

runcmd:
  - [ systemctl, start, httpd.service ]
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


### Xóa toàn bộ network cũ:

Xóa subnet:

	openstack subnet delete $(openstack subnet list -f value -c ID)

Xóa port:

	openstack port delete $(openstack port list -c ID -f value)

Xóa router:

	openstack router delete <ID_router>

Xóa network:

	openstack network delete $(openstack network list -f value -c ID)



## Get token

```sh
[root@trang-40-71 ~(openstack)]# curl -i   -H "Content-Type: application/json"   -d '
{ "auth": {
    "identity": {
      "methods": ["password"],
      "password": {
        "user": {
          "name": "admin",
          "domain": { "id": "default" },
          "password": "trang1234"
        }
      }
    }
  }
}'   "http://192.168.40.71:5000/v3/auth/tokens" ; echo
```

Kết quả trả về:

```sh
HTTP/1.1 201 Created
Date: Fri, 17 May 2019 03:17:04 GMT
Server: Apache/2.4.6 (CentOS) mod_wsgi/3.4 Python/2.7.5
X-Subject-Token: gAAAAABc3iew9w5UkpOTlgT6a3K72srZ_2A4GKrMsUuJ9egd42RwJ03D8gvMW7nkw-hW8I41n3mgEm2JxgZmULqbNE1j25WW11H80u8ujBVOic0JD8S6tnPkaWm2zpiQqXoCHDEeRjlgTo1enH7ZSLaHr9NDPedQXg
Vary: X-Auth-Token
x-openstack-request-id: req-0bdc3cce-ad4c-48a2-ab9b-a7e54c4784c4
Content-Length: 312
Content-Type: application/json

{"token": {"issued_at": "2019-05-17T03:17:04.000000Z", "audit_ids": ["RE_raWvxQ8SeukRkp-aibg"], "methods": ["password"], "expires_at": "2019-05-17T04:17:04.000000Z", "user": {"password_expires_at": null, "domain": {"id": "default", "name": "Default"}, "id": "4c9b0a695e294ad3b9615e36f75858e7", "name": "admin"}}}
```
