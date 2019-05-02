## Evacuate VM

**Evacuate** là một kỹ thuật cho phép cứu máy ảo đang chạy trên các node compute bị "chết" (mô hình nhiều node compute)

* **Mô tả script**:

	* **B1:** Script thực hiện kiểm tra xem có node compute nào down không, nếu có thực hiện bước 2, nếu không thực hiện bước 4
	* **B2:** Kiểm tra xem node compute bị chết đó có VM không, nếu có chuyển bước 2, nếu không chuyển bước 4
	* **B3:** Thực hiện evacuate để cứu toàn bộ VM trên node bị down
	* **B4:** Hoàn thành script
	* **B5:** Đặt crontab chạy 1 giờ một lần để kiểm tra

* Tạo một file `/root/evacuate.sh` có nội dung như [ở đây](evacuate.sh)
* Phân quyền thực thi cho file 

		`$ chmod +x evacuate.sh`
* Tạo crontab

		echo "0 * * * * source /root/keystonerc ; /bin/bash evacuate.sh" >> /etc/crontab


* Trong đó:

	* File `keystonerc` chứa biến môi trường:

		export OS_PROJECT_DOMAIN_NAME=default
		export OS_USER_DOMAIN_NAME=default
		export OS_PROJECT_NAME=admin
		export OS_USERNAME=admin
		export OS_PASSWORD=trang1234
		export OS_AUTH_URL=http://controller:5000/v3
		export OS_IDENTITY_API_VERSION=3
		export PS1='[\u@\h \W(openstack)]\$ '

