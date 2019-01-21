## Một số các câu lệnh thường dùng trong Keystone

### 1. Lấy token

Trước hết cần khai báo thông tin để xác thực, ví dụ:

```sh
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=trang1234
export OS_AUTH_URL=http://192.168.40.71:5000/v3
export OS_IDENTITY_API_VERSION=3
export PS1='[\u@\h \W(keystone)]\$ '
```

Lấy token

```sh
[root@trang-40-71 ~(keystone)]# openstack token issue
+------------+----------------------------------------+
| Field      | Value                                  |
+------------+----------------------------------------+
| expires    | 2019-01-17T10:50:46+0000               |
| id         | gAAAAABcQE_2I0BWfv9ajpPa40UwYIm7mtR....|
| project_id | 6ca743a0ed51475983e5febdc0cf5707       |
| user_id    | 93d01e50adfe49e0a0ada96740ecbbc6       |
+------------+----------------------------------------+
```

### Các câu lệnh làm việc với user, project, groups, roles, domain

Liệt kê danh sách:

```sh
openstack user list
openstack project list
openstack group list
openstack role list
openstack domain list
```

Tạo domain mới:

	openstack domain create <tên domain>

Tạo project mới trong domain

	openstack project create <tên-project> --domain <tên-domain> --description "<miêu tả về domain>"

Tạo mới user với domain

```sh
openstack user create <tên-user> [--email <email(optional)>] \
  --domain <tên domain> --description "<mô tả về domain>" \
  --password <password>
```

Xem các role của user:

	openstack role list --user <tên user> --project <tên project>

Gán role cho user:

	openstack role add --project <tên project> --project-domain <tên domain> --user <tên user> --user-domain <tên domain> <tên role>



## Tham khảo

https://docs.openstack.org/python-openstackclient/latest/cli/command-list.html

https://docs.openstack.org/keystone/pike/admin/cli-manage-projects-users-and-roles.html