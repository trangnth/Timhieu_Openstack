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


### Tạo user login

```sh
openstack project create demo
openstack user create --domain default --project demo --password trang1234 demo
openstack project set project_demo_ID --enable
openstack user set demo --enable
openstack role create demo
openstack role add --user demo --project demo demo
openstack role assignment list --user demo
openstack role show demo
```

### Managing port level security

* Pair port cho MAC address (trường hợp là hiện đang có một cụm OPS vật lý và muốn cài cụm OPS khác trên các máy ảo của cụm này)

```sh
# Danh sách các port của máy ảo trên openstack 
[root@mdt32 ~]# nova interface-list trang-ctl1
+------------+--------------------------------------+--------------------------------------+---------------+-------------------+
| Port State | Port ID                              | Net ID                               | IP addresses  | MAC Addr          |
+------------+--------------------------------------+--------------------------------------+---------------+-------------------+
| ACTIVE     | 9fb1d78a-9201-4fc5-82b4-06822c951ff5 | 935eb361-58a3-4de1-8c4e-2b63157ab9b2 | 192.168.40.81 | fa:16:3e:de:4c:b6 |
| ACTIVE     | ea117a13-0cbb-49e0-9d4b-0243d747821b | 76b621d1-84f8-4986-a06d-b61213c5aea4 | 192.168.50.81 | fa:16:3e:63:d4:f3 |
+------------+--------------------------------------+--------------------------------------+---------------+-------------------+

# Interface trên máy ảo
[root@trang-ctl1 ~(openstack)]$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether fa:16:3e:de:4c:b6 brd ff:ff:ff:ff:ff:ff
    inet 192.168.40.81/24 brd 192.168.40.255 scope global eth0
       valid_lft forever preferred_lft forever
3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master ovs-system state UP group default qlen 1000
    link/ether fa:16:3e:63:d4:f3 brd ff:ff:ff:ff:ff:ff
4: ovs-system: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 2e:48:58:67:dc:b9 brd ff:ff:ff:ff:ff:ff
5: br-int: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether ea:2d:ea:2d:11:40 brd ff:ff:ff:ff:ff:ff
6: br-tun: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether e2:f3:0f:5d:b7:44 brd ff:ff:ff:ff:ff:ff
7: br-provider: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
    link/ether 96:e0:1d:a6:3d:4c brd ff:ff:ff:ff:ff:ff
    inet 192.168.50.81/24 brd 192.168.50.255 scope global br-provider
       valid_lft forever preferred_lft forever

# Allow IP addr pairs cho port rồi
[root@mdt32 ~]# openstack port show ea117a13-0cbb-49e0-9d4b-0243d747821b
+-----------------------+------------------------------------------------------------------------------+
| Field                 | Value                                                                        |
+-----------------------+------------------------------------------------------------------------------+
| admin_state_up        | UP                                                                           |
| allowed_address_pairs | ip_address='0.0.0.0', mac_address='fa:16:3e:63:d4:f3'                        |
| binding_host_id       | mdt32                                                                        |
| binding_profile       |                                                                              |
| binding_vif_details   | datapath_type='system', ovs_hybrid_plug='True', port_filter='True'           |
| binding_vif_type      | ovs                                                                          |
| binding_vnic_type     | normal                                                                       |
| created_at            | 2019-09-12T03:50:52Z                                                         |
| data_plane_status     | None                                                                         |
| description           |                                                                              |
| device_id             | c8680c1f-f382-46d3-9ce8-cb8a149cc267                                         |
| device_owner          | compute:nova                                                                 |
| dns_assignment        | None                                                                         |
| dns_domain            | None                                                                         |
| dns_name              | None                                                                         |
| extra_dhcp_opts       |                                                                              |
| fixed_ips             | ip_address='192.168.50.81', subnet_id='f83659e5-4cbe-49d8-97ce-1a19313be076' |
| id                    | ea117a13-0cbb-49e0-9d4b-0243d747821b                                         |
| mac_address           | fa:16:3e:63:d4:f3                                                            |
| name                  | trangctl1                                                                    |
| network_id            | 76b621d1-84f8-4986-a06d-b61213c5aea4                                         |
| port_security_enabled | True                                                                         |
| project_id            | 4dbbe3d45e744c63a88fa15a117c60a5                                             |
| qos_policy_id         | None                                                                         |
| revision_number       | 9                                                                            |
| security_group_ids    | 94f446f5-4f67-4dc2-a11c-b2754ccbb6b9                                         |
| status                | ACTIVE                                                                       |
| tags                  |                                                                              |
| trunk_details         | None                                                                         |
| updated_at            | 2019-09-13T03:02:20Z                                                         |
+-----------------------+------------------------------------------------------------------------------+

# Allow MAC addr pairs port br-provider
neutron port-update ea117a13-0cbb-49e0-9d4b-0243d747821b --allowed_address_pairs list=true type=dict mac_address=96:e0:1d:a6:3d:4c,ip_address=192.168.50.81 mac_address=fa:16:3e:63:d4:f3,ip_address=0.0.0.0
```

### Một số các câu lệnh khởi động lại các service 

```sh
systemctl restart httpd

systemctl restart openstack-glance-api openstack-glance-registry 

systemctl restart openstack-nova-api.service \
  openstack-nova-scheduler.service openstack-nova-conductor.service \
  openstack-nova-novncproxy.service

systemctl restart neutron-server.service neutron-openvswitch-agent.service neutron-dhcp-agent.service neutron-metadata-agent.service neutron-l3-agent.service
```

### Quản lý các cell

* Xóa một cell

```sh
su -s /bin/sh -c "nova-manage cell_v2 list_cells" nova
su -s /bin/sh -c "nova-manage cell_v2 delete_cell --force --cell_uuid 0176f49b-5efb-41b9-b029-09b7a829e40e" nova
```

### Mariadb

* Khi thực hiện remote host DB mà gặp lỗi như sau:

```sh
[root@controller3 ~(openstack)]$ mysql -u root -ptrang1234 -h 192.168.40.71
ERROR 1045 (28000): Access denied for user 'root'@'controller3' (using password: YES)
```

Thực hiện phân quyền cho user như sau:

```sh
[root@controller1 ~(openstack)]$ mysql -u root -ptrang1234
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 2508
Server version: 10.1.20-MariaDB MariaDB Server

Copyright (c) 2000, 2016, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> grant all privileges on *.* to root@'%' identified by 'trang1234' with grant option;
Query OK, 0 rows affected (0.05 sec)

MariaDB [(none)]> SELECT USER(), CURRENT_USER();
+----------------+----------------+
| USER()         | CURRENT_USER() |
+----------------+----------------+
| root@localhost | root@localhost |
+----------------+----------------+
1 row in set (0.00 sec)

MariaDB [(none)]> SELECT user, host FROM mysql.user;
+------------------+-------------+
| user             | host        |
+------------------+-------------+
| glance           | %           |
| keystone         | %           |
| neutron          | %           |
| nova             | %           |
| placement        | %           |
| root             | %           |
| root             | 127.0.0.1   |
| root             | ::1         |
| root             | controller1 |
| clustercheckuser | localhost   |
| glance           | localhost   |
| keystone         | localhost   |
| neutron          | localhost   |
| nova             | localhost   |
| placement        | localhost   |
| root             | localhost   |
+------------------+-------------+
16 rows in set (0.00 sec)

MariaDB [(none)]> exit
Bye


[root@controller3 ~(openstack)]$ mysql -u root -ptrang1234 -h 192.168.40.71
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 2298
Server version: 10.1.20-MariaDB MariaDB Server

Copyright (c) 2000, 2016, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> exit
Bye
```

### Xem quotas

Xem thông tin của một project

```sh
openstack project list
PROJECT_ID=$(openstack project show -f value -c id admin)
openstack quota show --default $PROJECT_ID
```

Ví dụ:

```sh
[root@mdt32 ~]# openstack quota show --default $PROJECT_ID
+----------------------+-------+
| Field                | Value |
+----------------------+-------+
| backup-gigabytes     | 1000  |
| backups              | 10    |
| cores                | 20    |
| fixed-ips            | -1    |
| floating-ips         | 50    |
| gigabytes            | 1000  |
| groups               | 10    |
| health_monitors      | None  |
| injected-file-size   | 10240 |
| injected-files       | 5     |
| injected-path-size   | 255   |
| instances            | 10    |
| key-pairs            | 100   |
| l7_policies          | None  |
| listeners            | None  |
| load_balancers       | None  |
| location             | None  |
| name                 | None  |
| networks             | 100   |
| per-volume-gigabytes | -1    |
| pools                | None  |
| ports                | 500   |
| project              | None  |
| project_name         | admin |
| properties           | 128   |
| ram                  | 51200 |
| rbac_policies        | 10    |
| routers              | 10    |
| secgroup-rules       | 100   |
| secgroups            | 10    |
| server-group-members | 10    |
| server-groups        | 10    |
| snapshots            | 10    |
| subnet_pools         | -1    |
| subnets              | 100   |
| volumes              | 10    |
+----------------------+-------+
```
