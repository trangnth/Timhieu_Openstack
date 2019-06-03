# Hướng dẫn cài đặt và cấu hình 

**Chú ý**: Bài này sẽ hướng dẫn cài đặt và cấu hình gnocchi và ceilometer trên OpenStack bản Stein 

[1. Gnocchi](#gnocchi)

[2. Ceilometer](#ceilometer)


<a name="gnocchi"></a>
## 1. Gnocchi

Tạo user cho Gnocchi

```sh
openstack user create --domain default --project service --password trang1234 gnocchi 
openstack role add --project service --user gnocchi admin
openstack service create --name gnocchi --description "Metric Service" metric 
export controller=192.168.40.71
openstack endpoint create --region RegionOne metric public http://$controller:8041
openstack endpoint create --region RegionOne metric internal http://$controller:8041 
openstack endpoint create --region RegionOne metric admin http://$controller:8041 
mysql -u root -ptrang1234
create database gnocchi; 
grant all privileges on gnocchi.* to gnocchi@'localhost' identified by 'trang1234'; 
grant all privileges on gnocchi.* to gnocchi@'%' identified by 'trang1234'; 
flush privileges; 
exit
```

Cài đặt gnocchi service:

    yum --enablerepo=centos-openstack-stein,epel -y install openstack-gnocchi-api openstack-gnocchi-metricd python-gnocchiclient

Copy file cấu hình:

    mv /etc/gnocchi/gnocchi.conf /etc/gnocchi/gnocchi.conf.org 

Chỉnh sửa file `/etc/gnocchi/gnocchi.conf`

```sh
# create new
[DEFAULT]
log_dir = /var/log/gnocchi

[api]
auth_mode = keystone

[database]
backend = sqlalchemy

# MariaDB connection info
[indexer]
url = mysql+pymysql://gnocchi:trang1234@192.168.40.71/gnocchi

[storage]
driver = file
file_basepath = /var/lib/gnocchi

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://192.168.40.71:5000
auth_url = http://192.168.40.71:5000
memcached_servers = 192.168.40.71:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = gnocchi
password = trang1234
service_token_roles_required = true
```

Sửa file `/etc/httpd/conf.d/10-gnocchi_wsgi.conf`

```sh
# create new
Listen 8041
<VirtualHost *:8041>
  <Directory /usr/bin>
    AllowOverride None
    Require all granted
  </Directory>

  CustomLog /var/log/httpd/gnocchi_wsgi_access.log combined
  ErrorLog /var/log/httpd/gnocchi_wsgi_error.log
  SetEnvIf X-Forwarded-Proto https HTTPS=1
  WSGIApplicationGroup %{GLOBAL}
  WSGIDaemonProcess gnocchi display-name=gnocchi_wsgi user=gnocchi group=gnocchi processes=6 threads=6
  WSGIProcessGroup gnocchi
  WSGIScriptAlias / /usr/bin/gnocchi-api
</VirtualHost>
```

Khởi động service:

```sh
chmod 640 /etc/gnocchi/gnocchi.conf 
chgrp gnocchi /etc/gnocchi/gnocchi.conf 
su -s /bin/bash gnocchi -c "gnocchi-upgrade" 
systemctl start openstack-gnocchi-metricd 
systemctl enable openstack-gnocchi-metricd 
systemctl restart httpd 
export OS_AUTH_TYPE=password 
gnocchi resource list
```

Output không có error thì không lỗi gì.


<a name="ceilometer"></a>
## 2. Ceilometer

### 2.1 Trên Controller

Tạo user:

```sh
openstack user create --domain default --project service --password trang1234 ceilometer 
openstack role add --project service --user ceilometer admin
openstack service create --name ceilometer --description "OpenStack Telemetry Service" metering
```

Cài đặt:

```sh
yum --enablerepo=centos-openstack-stein,epel -y install openstack-ceilometer-central openstack-ceilometer-notification python-ceilometerclient
```

Sao lưu file cấu hình

    mv /etc/ceilometer/ceilometer.conf /etc/ceilometer/ceilometer.conf.org 

Chỉnh sửa file cấu hình `/etc/ceilometer/ceilometer.conf`

```sh
# create new
[DEFAULT]
# RabbitMQ connection info
transport_url = rabbit://openstack:trang1234@192.168.40.71

[api]
auth_mode = keystone

[dispatcher_gnocchi]
filter_service_activity = False

# Keystone auth info (with gnocchi)
[keystone_authtoken]
www_authenticate_uri = http://192.168.40.71:5000
auth_url = http://192.168.40.71:5000
memcached_servers = 192.168.40.71:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = gnocchi
password = trang1234

# Keystone auth info (with ceilometer)
[service_credentials]
auth_url = http://192.168.40.71:5000
memcached_servers = 192.168.40.71:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = ceilometer
password = trang1234
```

Khởi động service:

```sh
chmod 640 /etc/ceilometer/ceilometer.conf 
chgrp ceilometer /etc/ceilometer/ceilometer.conf 
su -s /bin/bash ceilometer -c "ceilometer-upgrade --skip-metering-database" 
systemctl start openstack-ceilometer-central openstack-ceilometer-notification 
systemctl enable openstack-ceilometer-central openstack-ceilometer-notification 
```



### 2.2 Trên Compute

Cài đặt service:

    yum --enablerepo=centos-openstack-stein,epel -y install openstack-ceilometer-compute

Sao lưu file cấu hình:

    mv /etc/ceilometer/ceilometer.conf /etc/ceilometer/ceilometer.conf.org 

Chỉnh sửa file cấu hình `/etc/ceilometer/ceilometer.conf`

```sh
[DEFAULT]
# RabbitMQ connection info
transport_url = rabbit://openstack:trang1234@192.168.40.71

[service_credentials]
auth_url = http://192.168.40.71:5000
memcached_servers = 192.168.40.71:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = ceilometer
password = trang1234
```

Khởi động dịch vụ:

```sh
chmod 640 /etc/ceilometer/ceilometer.conf 
chgrp ceilometer /etc/ceilometer/ceilometer.conf 
systemctl start openstack-ceilometer-compute 
systemctl enable openstack-ceilometer-compute 
```

## 3. Cấu hình Nova Compute sử dung Ceilometer

Chỉnh sửa file cấu hình `vi /etc/nova/nova.conf`

```sh
# add follows into [DEFAULT] section
instance_usage_audit = True
instance_usage_audit_period = hour
notify_on_state_change = vm_and_task_state
# add to the end
[oslo_messaging_notifications]
driver = messagingv2
```

Khởi động lại dịch vụ

    systemctl restart openstack-nova-compute 

**Check resources**

Liệt kê các resources:

```sh
[root@trang-40-71 ~(openstack)]$ openstack metric resource list -c id -c type -c original_resource_id
+--------------------------------------+----------------------------+-----------------------------------------------------------------------+
| id                                   | type                       | original_resource_id                                                  |
+--------------------------------------+----------------------------+-----------------------------------------------------------------------+
| 1722cb01-f5ee-51f9-b740-5eabae84e6ce | instance_network_interface | instance-00000017-8e99315c-dd44-47b6-be9d-bcaded1f7777-tap1b62ca75-a5 |
| fc25651a-42ec-50de-ab6d-53a78e673f7e | instance_disk              | 227a1235-b968-45ff-ac22-8f767a88dcb1-vda                              |
| deaa432a-cb57-5859-97a6-e1b27f7e1ab9 | instance_network_interface | instance-00000016-227a1235-b968-45ff-ac22-8f767a88dcb1-tapfdadadd2-98 |
| ee0cfddd-1b6a-5b77-8d8f-2bbb48a673ee | instance_disk              | 8e99315c-dd44-47b6-be9d-bcaded1f7777-vda                              |
| 26794e5c-ab88-5d5c-966d-64fd49900169 | instance_network_interface | instance-00000019-d4c31e31-a22b-4c31-8448-8575338acff1-tapaa8699e3-5d |
| c106724b-e9cd-5f0c-8805-f02ae4014153 | instance_disk              | d4c31e31-a22b-4c31-8448-8575338acff1-vda                              |
| d4c31e31-a22b-4c31-8448-8575338acff1 | instance                   | d4c31e31-a22b-4c31-8448-8575338acff1                                  |
| 8e99315c-dd44-47b6-be9d-bcaded1f7777 | instance                   | 8e99315c-dd44-47b6-be9d-bcaded1f7777                                  |
| 227a1235-b968-45ff-ac22-8f767a88dcb1 | instance                   | 227a1235-b968-45ff-ac22-8f767a88dcb1                                  |
+--------------------------------------+----------------------------+-----------------------------------------------------------------------+

[root@trang-40-71 ~(openstack)]$ openstack metric resource show 227a1235-b968-45ff-ac22-8f767a88dcb1 
+-----------------------+-------------------------------------------------------------------+
| Field                 | Value                                                             |
+-----------------------+-------------------------------------------------------------------+
| created_by_project_id | ec8e8a9ebc554743aadb551a64466c98                                  |
| created_by_user_id    | e3404957dd1849b288efb0b1fa96efbf                                  |
| creator               | e3404957dd1849b288efb0b1fa96efbf:ec8e8a9ebc554743aadb551a64466c98 |
| ended_at              | None                                                              |
| id                    | 227a1235-b968-45ff-ac22-8f767a88dcb1                              |
| metrics               | cpu: 775e5382-3711-4716-9e21-7962ab560519                         |
|                       | disk.ephemeral.size: 7e7b1cb8-b69b-43f9-af3c-6e2f65cdc424         |
|                       | disk.root.size: 2321a03f-fcfc-4643-88ec-71161e56b813              |
|                       | memory.usage: 679917e0-e3b1-4f30-8638-b9dc0de9a0c4                |
|                       | memory: 2acc8f1c-a163-47b5-97e8-91d0b1c2273d                      |
|                       | vcpus: abc538fd-697e-48dc-9a0b-7195452f5a60                       |
| original_resource_id  | 227a1235-b968-45ff-ac22-8f767a88dcb1                              |
| project_id            | ad159bee793b4235990125e45cea9037                                  |
| revision_end          | None                                                              |
| revision_start        | 2019-05-22T10:29:07.061665+00:00                                  |
| started_at            | 2019-05-22T10:21:08.167060+00:00                                  |
| type                  | instance                                                          |
| user_id               | 04714ff2e0904d9d9fa3341f1ca9e97a                                  |
+-----------------------+-------------------------------------------------------------------+

# CPU
[root@trang-40-71 ~(openstack)]$ openstack metric measures show 775e5382-3711-4716-9e21-7962ab560519
+---------------------------+-------------+---------------+
| timestamp                 | granularity |         value |
+---------------------------+-------------+---------------+
| 2019-05-22T17:20:00+07:00 |       300.0 | 64160000000.0 |
| 2019-05-22T17:25:00+07:00 |       300.0 | 67280000000.0 |
| 2019-05-22T17:30:00+07:00 |       300.0 | 70550000000.0 |
| 2019-05-22T17:35:00+07:00 |       300.0 | 73820000000.0 |
+---------------------------+-------------+---------------+

# memory.usage

[root@trang-40-71 ~(openstack)]$ openstack metric measures show 679917e0-e3b1-4f30-8638-b9dc0de9a0c4
+---------------------------+-------------+-------+
| timestamp                 | granularity | value |
+---------------------------+-------------+-------+
| 2019-05-22T17:20:00+07:00 |       300.0 | 210.0 |
| 2019-05-22T17:25:00+07:00 |       300.0 | 210.0 |
| 2019-05-22T17:30:00+07:00 |       300.0 | 210.0 |
| 2019-05-22T17:35:00+07:00 |       300.0 | 210.0 |
+---------------------------+-------------+-------+
```

## 4. Cấu hình Glance sử dụng Ceilometer

Sửa file cấu hình `/etc/glance/glance-api.conf`

```sh
# add to the end
[oslo_messaging_notifications]
driver = messagingv2
# RabbitMQ connection info
transport_url = rabbit://openstack:trang1234@192.168.40.71
```

Khởi động lại dịch vụ:

    systemctl restart openstack-glance-api 

**Check các resources**

Tạo một image, sau đó kiểm tra

```sh
openstack image create "cirros-test" --file /opt/cirros-0.4.0-x86_64-disk.img --disk-format qcow2 --container-format bare --public
[root@trang-40-71 ~(openstack)]$ openstack metric resource list -c id -c type
+--------------------------------------+----------------------------+
| id                                   | type                       |
+--------------------------------------+----------------------------+
| 1722cb01-f5ee-51f9-b740-5eabae84e6ce | instance_network_interface |
| fc25651a-42ec-50de-ab6d-53a78e673f7e | instance_disk              |
| deaa432a-cb57-5859-97a6-e1b27f7e1ab9 | instance_network_interface |
| ee0cfddd-1b6a-5b77-8d8f-2bbb48a673ee | instance_disk              |
| 26794e5c-ab88-5d5c-966d-64fd49900169 | instance_network_interface |
| c106724b-e9cd-5f0c-8805-f02ae4014153 | instance_disk              |
| d4c31e31-a22b-4c31-8448-8575338acff1 | instance                   |
| 8e99315c-dd44-47b6-be9d-bcaded1f7777 | instance                   |
| 227a1235-b968-45ff-ac22-8f767a88dcb1 | instance                   |
| eeeb41c0-e613-4cd7-83ce-db6b6b1bce13 | image                      |
+--------------------------------------+----------------------------+

[root@trang-40-71 ~(openstack)]$ openstack metric resource show eeeb41c0-e613-4cd7-83ce-db6b6b1bce13
+-----------------------+-------------------------------------------------------------------+
| Field                 | Value                                                             |
+-----------------------+-------------------------------------------------------------------+
| created_by_project_id | ec8e8a9ebc554743aadb551a64466c98                                  |
| created_by_user_id    | e3404957dd1849b288efb0b1fa96efbf                                  |
| creator               | e3404957dd1849b288efb0b1fa96efbf:ec8e8a9ebc554743aadb551a64466c98 |
| ended_at              | None                                                              |
| id                    | eeeb41c0-e613-4cd7-83ce-db6b6b1bce13                              |
| metrics               | image.size: 7c27d347-d96a-4ecf-b2a2-169ed783c451                  |
| original_resource_id  | eeeb41c0-e613-4cd7-83ce-db6b6b1bce13                              |
| project_id            | ad159bee793b4235990125e45cea9037                                  |
| revision_end          | None                                                              |
| revision_start        | 2019-05-22T10:55:36.373039+00:00                                  |
| started_at            | 2019-05-22T10:55:36.373016+00:00                                  |
| type                  | image                                                             |
| user_id               | None                                                              |
+-----------------------+-------------------------------------------------------------------+

# image.size
[root@trang-40-71 ~(openstack)]$ openstack metric measures show  7c27d347-d96a-4ecf-b2a2-169ed783c451
+---------------------------+-------------+------------+
| timestamp                 | granularity |      value |
+---------------------------+-------------+------------+
| 2019-05-22T17:55:00+07:00 |       300.0 | 12716032.0 |
+---------------------------+-------------+------------+
```

## 5. Tích hợp với Grafana

### 5.1 Cài đặt grafana

**Chú ý**: Hiện tại các phiên bản đang được sử dụng là:

* Openstack Stein
* Grafana v6.1.6


Đầu tiên cần add repo:
```sh
cat > /etc/yum.repos.d/grafana.repo <<'EOF'
[grafana]
name=grafana
baseurl=https://packagecloud.io/grafana/stable/el/7/$basearch
gpgkey=https://packagecloud.io/gpg.key https://grafanarel.s3.amazonaws.com/RPM-GPG-KEY-grafana
enabled=0
gpgcheck=1
EOF
```

Install Grafana:

```sh
yum install epel-release -y
yum --enablerepo=grafana -y install grafana initscripts fontconfig
``

Khởi động dịch vụ:

```sh
systemctl start grafana-server 
systemctl enable grafana-server
```

Nếu firewall đang bật:

```sh
firewall-cmd --add-port=3000/tcp --permanent 
firewall-cmd --reload
```

### 5.2 Cấu hình Grafana add datasource gnocchi

Cài đặt plugin:

```sh
sudo grafana-cli plugins install gnocchixyz-gnocchi-datasource
```

**Trên controller**

* Sửa file  `/etc/gnocchi/gnocchi.conf`:
    ```
    [cors]
    allowed_origin = http://192.168.40.129:3000
    ```
* Sửa file `/etc/keystone/keystone.conf`

    ```
    [cors]
    allowed_origin = http://192.168.40.129:3000
    allow_methods = GET,PUT,POST,DELETE,PATCH
    allow_headers = X-Auth-Token,X-Openstack-Request-Id,X-Subject-Token,X-Project-Id,X-Project-Name,X-Project-Domain-Id,X-Project-Domain-Name,X-Domain-Id,X-Domain-Name
    ```
* Khởi động lại dịch vụ:
    ```
    systemctl restart httpd
    systemctl restart openstack-gnocchi-*
    ```


Truy cập vào địa chỉ web của grafana (ví dụ: 192.168.68.110:3000) add data source như sau:

<img src="../../img/100.png">

<img src="../../img/101.png">

<img src="../../img/102.png">

<img src="../../img/103.png">

<img src="../../img/104.png">

Ví dụ một database:

<img src="../../img/107.png">


## Cài đặt và cấu hình cho bản Rocky

### Controller

Tạo user:
```sh
openstack user create --domain default --project service --password trang1234 gnocchi
openstack role add --project service --user gnocchi admin
openstack service create --name gnocchi --description "Metric Service" metric 
export controller=192.168.40.71
openstack endpoint create --region RegionOne metric public http://192.168.40.71:8041
openstack endpoint create --region RegionOne metric internal http://192.168.40.71:8041
openstack endpoint create --region RegionOne metric admin http://192.168.40.71:8041

mysql -u root -ptrang1234
CREATE DATABASE gnocchi;
GRANT ALL PRIVILEGES ON gnocchi.* TO 'gnocchi'@'localhost' IDENTIFIED BY 'trang1234';
GRANT ALL PRIVILEGES ON gnocchi.* TO 'gnocchi'@'%' IDENTIFIED BY 'trang1234';
flush privileges;
exit
yum --enablerepo=centos-openstack-rocky,epel -y install openstack-gnocchi-api openstack-gnocchi-metricd python2-gnocchiclient
mv /etc/gnocchi/gnocchi.conf > /etc/gnocchi/gnocchi.conf.org 
cat <<EOF > /etc/gnocchi/gnocchi.conf
[DEFAULT]
log_dir = /var/log/gnocchi

[api]
auth_mode = keystone

[database]
backend = sqlalchemy

# MariaDB connection info
[indexer]
url = mysql+pymysql://gnocchi:trang1234@192.168.40.71/gnocchi

[storage]
driver = file
file_basepath = /var/lib/gnocchi

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://192.168.40.71:5000
auth_url = http://192.168.40.71:5000
memcached_servers = 192.168.40.71:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = gnocchi
password = trang1234
service_token_roles_required = true
EOF
cat <<EOF > /etc/httpd/conf.d/10-gnocchi_wsgi.conf
# create new
Listen 8041
<VirtualHost *:8041>
  <Directory /usr/bin>
    AllowOverride None
    Require all granted
  </Directory>

  CustomLog /var/log/httpd/gnocchi_wsgi_access.log combined
  ErrorLog /var/log/httpd/gnocchi_wsgi_error.log
  SetEnvIf X-Forwarded-Proto https HTTPS=1
  WSGIApplicationGroup %{GLOBAL}
  WSGIDaemonProcess gnocchi display-name=gnocchi_wsgi user=gnocchi group=gnocchi processes=6 threads=6
  WSGIProcessGroup gnocchi
  WSGIScriptAlias / /usr/bin/gnocchi-api
</VirtualHost>
EOF
chmod 640 /etc/gnocchi/gnocchi.conf 
chgrp gnocchi /etc/gnocchi/gnocchi.conf
su -s /bin/bash gnocchi -c "gnocchi-upgrade" 
#gnocchi-upgrade
systemctl enable openstack-gnocchi-metricd.service
systemctl start openstack-gnocchi-metricd.service
systemctl restart httpd
echo export OS_AUTH_TYPE=password >> /root/keystonerc
source /root/keystonerc
gnocchi resource list

openstack user create --domain default --project service --password trang1234 ceilometer
openstack role add --project service --user ceilometer admin
openstack service create --name ceilometer --description "OpenStack Telemetry Service" metering
yum --enablerepo=centos-openstack-rocky,epel -y install openstack-ceilometer-central openstack-ceilometer-notification python2-ceilometerclient
cp /etc/ceilometer/pipeline.yaml /etc/ceilometer/pipeline.yaml.org
mv /etc/ceilometer/ceilometer.conf /etc/ceilometer/ceilometer.conf.org 
cat <<EOF > /etc/ceilometer/ceilometer.conf
# create new
[DEFAULT]
# RabbitMQ connection info
transport_url = rabbit://openstack:trang1234@192.168.40.71

[api]
auth_mode = keystone

[dispatcher_gnocchi]
filter_service_activity = False

# Keystone auth info (with gnocchi)
[keystone_authtoken]
www_authenticate_uri = http://192.168.40.71:5000
auth_url = http://192.168.40.71:5000
memcached_servers = 192.168.40.71:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = gnocchi
password = trang1234

# Keystone auth info (with ceilometer)
[service_credentials]
auth_url = http://192.168.40.71:5000
memcached_servers = 192.168.40.71:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = ceilometer
password = trang1234
EOF
chmod 640 /etc/ceilometer/ceilometer.conf 
chgrp ceilometer /etc/ceilometer/ceilometer.conf 
su -s /bin/bash ceilometer -c "ceilometer-upgrade --skip-metering-database" 
systemctl start openstack-ceilometer-central openstack-ceilometer-notification
systemctl enable openstack-ceilometer-central openstack-ceilometer-notification 
```






**Cấu hình Glance:**

Sửa file `/etc/glance/glance-api.conf` và `/etc/glance/glance-registry.conf`

```sh
# add to the end
[oslo_messaging_notifications]
driver = messagingv2
# RabbitMQ connection info
transport_url = rabbit://openstack:trang1234@192.168.40.71
```

Khởi động lại dịch vụ:

    systemctl restart openstack-glance-api.service openstack-glance-registry.service

**Cấu hình Cinder service**

Chỉnh sửa file `/etc/cinder/cinder.conf` trên tất cả các node mà cinder đang chạy:

```sh
# add to the end
[oslo_messaging_notifications]
driver = messagingv2
transport_url = rabbit://openstack:trang1234@192.168.40.71
```

Khởi động lại dịch vụ:

    systemctl restart openstack-cinder-api openstack-cinder-scheduler 


Tạo một vài volume mới và xem có thể lấy được nhưng thông số gì:

```sh
[root@trang-40-71 ~(openstack)]# openstack metric resource list -c type -c id -c  original_resource_id
+--------------------------------------+----------------------------+-----------------------------------------------------------------------+
| id                                   | type                       | original_resource_id                                                  |
+--------------------------------------+----------------------------+-----------------------------------------------------------------------+
| cbf34a71-3b25-555a-8769-e587fb6ba017 | instance_network_interface | instance-0000004d-90380863-a833-4058-93fc-eac897e6a679-tap35550250-7b |
| 7c503ccb-2947-584a-a48f-1d80443862ed | instance_network_interface | instance-0000004b-a871e8b4-afa4-4f47-a23f-4eab3a183cc5-tap3df9bb7b-94 |
| 38ff9495-18fe-52c5-b70f-e2fc0c79c078 | instance_network_interface | instance-0000004c-5ecdadb9-1dc9-4f9f-81b3-17d1305ab082-tapfc4c0e8e-1c |
| b404efa1-d7af-556f-adf5-60bac719238f | instance_disk              | 5ecdadb9-1dc9-4f9f-81b3-17d1305ab082-vda                              |
| 1089e20a-56ae-56e7-a49e-995b85c5aa0d | instance_network_interface | instance-0000004e-8af04bc7-9de9-4db4-bdcb-2d0fb02cde1d-tap169a3e41-de |
| 8d22949e-eac2-53a8-96ca-75be763a67c0 | instance_disk              | 8af04bc7-9de9-4db4-bdcb-2d0fb02cde1d-vda                              |
| 5143402c-ed50-5e9e-9933-aa7b7eb7e6c6 | instance_disk              | 90380863-a833-4058-93fc-eac897e6a679-vda                              |
| 6ae6c671-f988-55cf-ab6b-9b83035f37e0 | instance_disk              | a871e8b4-afa4-4f47-a23f-4eab3a183cc5-vda                              |
| a871e8b4-afa4-4f47-a23f-4eab3a183cc5 | instance                   | a871e8b4-afa4-4f47-a23f-4eab3a183cc5                                  |
| 90380863-a833-4058-93fc-eac897e6a679 | instance                   | 90380863-a833-4058-93fc-eac897e6a679                                  |
| 5ecdadb9-1dc9-4f9f-81b3-17d1305ab082 | instance                   | 5ecdadb9-1dc9-4f9f-81b3-17d1305ab082                                  |
| 8af04bc7-9de9-4db4-bdcb-2d0fb02cde1d | instance                   | 8af04bc7-9de9-4db4-bdcb-2d0fb02cde1d                                  |
| 5dac05c9-0e44-5dca-b0c3-308868c3c872 | volume_provider            | trang-40-74@lvm2                                                      |
| 12383834-8fe3-5070-b2e4-5b3a9d339563 | volume_provider_pool       | trang-40-74@lvm#lvm                                                   |
| 5ac3ce1b-d1a3-56b5-a872-7bd176dabe16 | volume_provider_pool       | trang-40-74@lvm2#lvm2                                                 |
| 47397e38-d8fe-5e2d-af70-f01087530e57 | volume_provider            | trang-40-74@lvm                                                       |
| 601769b0-4499-421e-ab28-6d243ed36247 | volume                     | 601769b0-4499-421e-ab28-6d243ed36247                                  |
| af1f03ef-6089-43ea-80cd-c4cf25eca854 | volume                     | af1f03ef-6089-43ea-80cd-c4cf25eca854                                  |
| 7f3f17cd-ec38-4972-93bd-441bb0394c8d | volume                     | 7f3f17cd-ec38-4972-93bd-441bb0394c8d                                  |
| e0aa2d5c-5c44-4d3b-849b-a708a1207913 | volume                     | e0aa2d5c-5c44-4d3b-849b-a708a1207913                                  |
| da91283e-2ede-57b1-8281-3cfeb7d90039 | volume_provider_pool       | trang-40-74@lvm#LVM                                                   |
| d2dda93c-abb8-446d-a2bf-d3e86dae6a0a | volume                     | d2dda93c-abb8-446d-a2bf-d3e86dae6a0a                                  |
| 2035e513-0a4b-5de3-aba3-649cbfd79604 | volume_provider_pool       | trang-40-74@lvm1#lvm1                                                 |
| bcaf1163-de84-5f77-8b96-003eed6d3829 | volume_provider            | trang-40-74@lvm1                                                      |
| b8f3b99c-4cc9-4b58-9400-cd51d87944de | volume                     | b8f3b99c-4cc9-4b58-9400-cd51d87944de                                  |
+--------------------------------------+----------------------------+-----------------------------------------------------------------------+
[root@trang-40-71 ~(openstack)]# openstack metric resource show b8f3b99c-4cc9-4b58-9400-cd51d87944de
+-----------------------+-------------------------------------------------------------------+
| Field                 | Value                                                             |
+-----------------------+-------------------------------------------------------------------+
| created_by_project_id | 46f7dedbbaf843049cd5a5e72e6dc752                                  |
| created_by_user_id    | 25e98294cc204e3a9f1bd3ba250685ba                                  |
| creator               | 25e98294cc204e3a9f1bd3ba250685ba:46f7dedbbaf843049cd5a5e72e6dc752 |
| ended_at              | None                                                              |
| id                    | b8f3b99c-4cc9-4b58-9400-cd51d87944de                              |
| metrics               | volume.size: d299d832-3f05-454c-8d39-c76a23c8cd09                 |
| original_resource_id  | b8f3b99c-4cc9-4b58-9400-cd51d87944de                              |
| project_id            | db93189111d44af1b22d43e849de6e34                                  |
| revision_end          | None                                                              |
| revision_start        | 2019-05-29T02:32:59.283243+00:00                                  |
| started_at            | 2019-05-29T02:32:59.283112+00:00                                  |
| type                  | volume                                                            |
| user_id               | 4c9b0a695e294ad3b9615e36f75858e7                                  |
+-----------------------+-------------------------------------------------------------------+
[root@trang-40-71 ~(openstack)]# openstack metric  measures show d299d832-3f05-454c-8d39-c76a23c8cd09
+---------------------------+-------------+-------+
| timestamp                 | granularity | value |
+---------------------------+-------------+-------+
| 2019-05-29T09:30:00+07:00 |       300.0 |   1.0 |
+---------------------------+-------------+-------+
```


**Cấu hình Neutron service**

Chỉnh sửa file `/etc/neutron/neutron.conf`

```sh
[oslo_messaging_notifications]
...
driver = messagingv2
```

Khởi động lại dịch vụ:

    systemctl restart neutron-server.service



### Compute

Cài đặt và cấu hình:

```sh
yum --enablerepo=centos-openstack-rocky,epel -y install openstack-ceilometer-compute
mv /etc/ceilometer/ceilometer.conf /etc/ceilometer/ceilometer.conf.org 
cat <<EOF > /etc/ceilometer/ceilometer.conf
# create new
[DEFAULT]
# RabbitMQ connection info
transport_url = rabbit://openstack:trang1234@192.168.40.71

[service_credentials]
auth_url = http://192.168.40.71:5000
memcached_servers = 192.168.40.71:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = ceilometer
password = trang1234
EOF
chmod 640 /etc/ceilometer/ceilometer.conf 
chgrp ceilometer /etc/ceilometer/ceilometer.conf 
systemctl start openstack-ceilometer-compute 
systemctl enable openstack-ceilometer-compute
echo export OS_AUTH_TYPE=password >> /root/keystonerc
source /root/keystonerc 
```

Chỉnh sửa file `/etc/nova/nova.conf` 

```sh
# add follows into [DEFAULT] section
instance_usage_audit = True
instance_usage_audit_period = hour
notify_on_state_change = vm_and_task_state
# add to the end
[oslo_messaging_notifications]
driver = messagingv2
```

Khởi động lại dịch vụ:

    systemctl restart openstack-nova-compute 


Kết quả:

```sh
[root@trang-40-71 ~(openstack)]# openstack metric resource list -c id -c type
+--------------------------------------+----------------------------+
| id                                   | type                       |
+--------------------------------------+----------------------------+
| cbf34a71-3b25-555a-8769-e587fb6ba017 | instance_network_interface |
| 7c503ccb-2947-584a-a48f-1d80443862ed | instance_network_interface |
| 38ff9495-18fe-52c5-b70f-e2fc0c79c078 | instance_network_interface |
| b404efa1-d7af-556f-adf5-60bac719238f | instance_disk              |
| 1089e20a-56ae-56e7-a49e-995b85c5aa0d | instance_network_interface |
| 8d22949e-eac2-53a8-96ca-75be763a67c0 | instance_disk              |
| 5143402c-ed50-5e9e-9933-aa7b7eb7e6c6 | instance_disk              |
| 6ae6c671-f988-55cf-ab6b-9b83035f37e0 | instance_disk              |
| a871e8b4-afa4-4f47-a23f-4eab3a183cc5 | instance                   |
| 90380863-a833-4058-93fc-eac897e6a679 | instance                   |
| 5ecdadb9-1dc9-4f9f-81b3-17d1305ab082 | instance                   |
| 8af04bc7-9de9-4db4-bdcb-2d0fb02cde1d | instance                   |
| 5dac05c9-0e44-5dca-b0c3-308868c3c872 | volume_provider            |
| 12383834-8fe3-5070-b2e4-5b3a9d339563 | volume_provider_pool       |
| 5ac3ce1b-d1a3-56b5-a872-7bd176dabe16 | volume_provider_pool       |
| 47397e38-d8fe-5e2d-af70-f01087530e57 | volume_provider            |
+--------------------------------------+----------------------------+
[root@trang-40-71 ~(openstack)]# openstack metric resource show 5dac05c9-0e44-5dca-b0c3-308868c3c872
+-----------------------+-----------------------------------------------------------------------------+
| Field                 | Value                                                                       |
+-----------------------+-----------------------------------------------------------------------------+
| created_by_project_id | 46f7dedbbaf843049cd5a5e72e6dc752                                            |
| created_by_user_id    | 25e98294cc204e3a9f1bd3ba250685ba                                            |
| creator               | 25e98294cc204e3a9f1bd3ba250685ba:46f7dedbbaf843049cd5a5e72e6dc752           |
| ended_at              | None                                                                        |
| id                    | 5dac05c9-0e44-5dca-b0c3-308868c3c872                                        |
| metrics               | volume.provider.capacity.allocated: 7a40b377-8dd2-46a2-8140-fb0930fdfd79    |
|                       | volume.provider.capacity.free: c7bb00d7-828c-4921-9a2d-783dbacf01e5         |
|                       | volume.provider.capacity.provisioned: ef0ebb0a-3d2e-4d1b-b553-14ac78078f2d  |
|                       | volume.provider.capacity.total: 28f2963e-31e6-4e52-8ce2-d04aa5c50bb7        |
|                       | volume.provider.capacity.virtual_free: e1be271b-585c-4955-9a1d-cc792106f37e |
| original_resource_id  | trang-40-74@lvm2                                                            |
| project_id            | None                                                                        |
| revision_end          | None                                                                        |
| revision_start        | 2019-05-28T08:59:40.148106+00:00                                            |
| started_at            | 2019-05-28T08:59:40.148060+00:00                                            |
| type                  | volume_provider                                                             |
| user_id               | None                                                                        |
+-----------------------+-----------------------------------------------------------------------------+
[root@trang-40-71 ~(openstack)]# openstack metric resource show 8af04bc7-9de9-4db4-bdcb-2d0fb02cde1d
+-----------------------+-------------------------------------------------------------------+
| Field                 | Value                                                             |
+-----------------------+-------------------------------------------------------------------+
| created_by_project_id | 46f7dedbbaf843049cd5a5e72e6dc752                                  |
| created_by_user_id    | 25e98294cc204e3a9f1bd3ba250685ba                                  |
| creator               | 25e98294cc204e3a9f1bd3ba250685ba:46f7dedbbaf843049cd5a5e72e6dc752 |
| ended_at              | None                                                              |
| id                    | 8af04bc7-9de9-4db4-bdcb-2d0fb02cde1d                              |
| metrics               | cpu.delta: 7e706886-35da-4b15-89d2-3e0ee7aacbe7                   |
|                       | cpu: 913c5f45-c21d-4a76-9b9f-69b88b71d4f6                         |
|                       | cpu_util: 6026e302-7f93-4d18-941d-d2ea5b92f721                    |
|                       | disk.ephemeral.size: c3011f0c-e71b-45ae-9cc2-93464bace854         |
|                       | disk.root.size: 44607249-f070-4e6e-af53-e2330dce1556              |
|                       | memory.usage: ff5502b5-3e80-4bbb-a5a0-1063218b63f2                |
|                       | memory: 1fc3c586-7f50-42b4-a869-84b607350167                      |
|                       | vcpus: 9db1ece4-462b-49c3-8404-e41df664e74a                       |
| original_resource_id  | 8af04bc7-9de9-4db4-bdcb-2d0fb02cde1d                              |
| project_id            | db93189111d44af1b22d43e849de6e34                                  |
| revision_end          | None                                                              |
| revision_start        | 2019-05-28T08:56:18.178457+00:00                                  |
| started_at            | 2019-05-28T08:45:34.720036+00:00                                  |
| type                  | instance                                                          |
| user_id               | 4c9b0a695e294ad3b9615e36f75858e7                                  |
+-----------------------+-------------------------------------------------------------------+
[root@trang-40-71 ~(openstack)]# openstack metric measures show 6026e302-7f93-4d18-941d-d2ea5b92f721
+---------------------------+-------------+--------------+
| timestamp                 | granularity |        value |
+---------------------------+-------------+--------------+
| 2019-05-28T15:50:00+07:00 |       300.0 |  2.346268789 |
| 2019-05-28T15:55:00+07:00 |       300.0 | 2.3907631874 |
| 2019-05-28T16:00:00+07:00 |       300.0 |  2.366121804 |
+---------------------------+-------------+--------------+
```

Một ví dụ được hiển thị trên grafana:

<img src="../../img/108.png">


## Tham khảo

https://grafana.com/plugins/gnocchixyz-gnocchi-datasource