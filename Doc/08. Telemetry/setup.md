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

Truy cập vào địa chỉ web của grafana (ví dụ: 192.168.68.110:3000) add data source như sau:

<img src="../../img/100.png">

<img src="../../img/101.png">

<img src="../../img/102.png">

<img src="../../img/103.png">

<img src="../../img/104.png">

## Cài đặt và cấu hình cho bản Rocky

### Controller

Tạo user:

    openstack user create --domain default --password-prompt ceilometer
-> nhập pass

    openstack role add --project service --user ceilometer admin
    openstack user create --domain default --password-prompt gnocchi
-> nhập pass

```sh
openstack service create --name gnocchi --description "Metric Service" metric
openstack role add --project service --user gnocchi admin
openstack endpoint create --region RegionOne metric public http://192.168.40.71:8041
openstack endpoint create --region RegionOne metric internal http://192.168.40.71:8041
openstack endpoint create --region RegionOne metric admin http://192.168.40.71:8041
yum --enablerepo=centos-openstack-rocky install -y openstack-gnocchi-api openstack-gnocchi-metricd python-gnocchiclient
mysql -u root -ptrang1234
CREATE DATABASE gnocchi;
GRANT ALL PRIVILEGES ON gnocchi.* TO 'gnocchi'@'localhost' IDENTIFIED BY 'trang1234';
GRANT ALL PRIVILEGES ON gnocchi.* TO 'gnocchi'@'%' IDENTIFIED BY 'trang1234';
exit
mv /etc/gnocchi/gnocchi.conf > /etc/gnocchi/gnocchi.conf.org 
cat <<EOF > /etc/gnocchi/gnocchi.conf
[api]
auth_mode = keystone
[keystone_authtoken]
auth_type = password
auth_url = http://192.168.40.71:5000/v3
project_domain_name = Default
user_domain_name = Default
project_name = service
username = gnocchi
password = trang1234
interface = internalURL
region_name = RegionOne
[indexer]
url = mysql+pymysql://gnocchi:trang1234@192.168.40.71/gnocchi
[storage]
# coordination_url is not required but specifying one will improve
# performance with better workload division across workers.
# coordination_url = redis://192.168.40.71:6379
file_basepath = /var/lib/gnocchi
driver = file
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
# su -s /bin/bash gnocchi -c "gnocchi-upgrade" 
gnocchi-upgrade
systemctl enable openstack-gnocchi-api.service openstack-gnocchi-metricd.service
systemctl start openstack-gnocchi-api.service openstack-gnocchi-metricd.service
systemctl restart httpd
gnocchi resource list
yum install --enablerepo=centos-openstack-rocky -y openstack-ceilometer-notification openstack-ceilometer-central python2-ceilometerclient
cp /etc/ceilometer/pipeline.yaml /etc/ceilometer/pipeline.yaml.org
```

Chỉnh sửa file cấu hình `/etc/ceilometer/pipeline.yaml`

```sh
publishers:
    # set address of Gnocchi
    # + filter out Gnocchi-related activity meters (Swift driver)
    # + set default archive policy
    - gnocchi://?filter_project=service&archive_policy=low
```

Tiếp tục cấu hình:

```sh
mv /etc/ceilometer/ceilometer.conf /etc/ceilometer/ceilometer.conf.org
cat <<EOF > /etc/ceilometer/ceilometer.conf
[DEFAULT]
transport_url = rabbit://openstack:trang1234@192.168.40.71

[service_credentials]
auth_type = password
auth_url = http://192.168.40.71:5000/v3
project_domain_id = default
user_domain_id = default
project_name = service
username = ceilometer
password = trang1234
interface = internalURL
region_name = RegionOne
EOF
chmod 640 /etc/ceilometer/ceilometer.conf
chgrp ceilometer /etc/ceilometer/ceilometer.conf 
# su -s /bin/bash ceilometer -c "ceilometer-upgrade --skip-metering-database"
ceilometer-upgrade
systemctl enable openstack-ceilometer-notification.service openstack-ceilometer-central.service
systemctl start openstack-ceilometer-notification.service openstack-ceilometer-central.service
```

**Cấu hình Glance:**

Sửa file `/etc/glance/glance-api.conf` và `/etc/glance/glance-registry.conf`

```sh
[DEFAULT]
...
transport_url = rabbit://openstack:trang1234@192.168.40.71

[oslo_messaging_notifications]
...
driver = messagingv2
```

Khởi động lại dịch vụ:

    systemctl restart openstack-glance-api.service openstack-glance-registry.service

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
yum --enablerepo=centos-openstack-rocky install -y openstack-ceilometer-compute
cp /etc/ceilometer/ceilometer.conf /etc/ceilometer/ceilometer.conf.org
cat <<EOF > /etc/ceilometer/ceilometer.conf 
[DEFAULT]
transport_url = rabbit://openstack:trang1234@192.168.40.71

[service_credentials]
auth_url = http://192.168.40.71:5000
project_domain_id = default
user_domain_id = default
auth_type = password
username = ceilometer
project_name = service
password = trang1234
interface = internalURL
region_name = RegionOne
EOF
chmod 640 /etc/ceilometer/ceilometer.conf 
chgrp ceilometer /etc/ceilometer/ceilometer.conf 
```
Cấu hình nova compute sử dụng Telemetry, chỉnh file `/etc/nova/nova.conf`

```sh
[DEFAULT]
...
instance_usage_audit = True
instance_usage_audit_period = hour
notify_on_state_change = vm_and_task_state

[oslo_messaging_notifications]
...
driver = messagingv2
```

Khởi động dịch vụ:

```sh
systemctl enable openstack-ceilometer-compute.service
systemctl start openstack-ceilometer-compute.service
systemctl restart openstack-nova-compute.service
echo export OS_AUTH_TYPE=password >> /root/keystonerc
source /root/keystonerc
```





## Tham khảo

https://grafana.com/plugins/gnocchixyz-gnocchi-datasource