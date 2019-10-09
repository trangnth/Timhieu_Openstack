## Hướng dẫn cài đặt rabbitmq trên centos7

```sh
yum -y install erlang socat
erl -version
cd /opt/
wget https://www.rabbitmq.com/releases/rabbitmq-server/v3.6.10/rabbitmq-server-3.6.10-1.el7.noarch.rpm
rpm --import https://www.rabbitmq.com/rabbitmq-release-signing-key.asc
rpm -Uvh rabbitmq-server-3.6.10-1.el7.noarch.rpm
systemctl start rabbitmq-server
systemctl enable rabbitmq-server
systemctl status rabbitmq-server
systemctl status firewalld
firewall-cmd --zone=public --permanent --add-port=4369/tcpsystemctl status firewalld
firewall-cmd --zone=public --permanent --add-port=4369/tcp
firewall-cmd --zone=public --permanent --add-port=25672/tcp
firewall-cmd --zone=public --permanent --add-port=5671-5672/tcp
firewall-cmd --zone=public --permanent --add-port=15672/tcp
firewall-cmd --zone=public --permanent --add-port=61613-61614/tcp
firewall-cmd --zone=public --permanent --add-port=1883/tcp
firewall-cmd --zone=public --permanent --add-port=8883/tcp
firewall-cmd --reload
setsebool -P nis_enabled 1
rabbitmq-plugins enable rabbitmq_management
chown -R rabbitmq:rabbitmq /var/lib/rabbitmq/
rabbitmqctl add_user admin trang1234
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

Truy cập vào địa chỉ `http://192.168.40.123:15672` với `user/pass` lần lượt là `admin/trang1234`

## Tham khảo

https://www.howtoforge.com/tutorial/how-to-install-rabbitmq-server-on-centos-7/

