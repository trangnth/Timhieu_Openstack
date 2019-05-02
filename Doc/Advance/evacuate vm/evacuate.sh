#!/bin/sh

#
# Created by trangnth
# Script evacuate VM in compute down
# Date: 12/04/2019
#


#
# Liệt kê các note compute down
#
node_com_down(){
    list_com_down=$(openstack compute service list -f value -c 'Host' -c 'State' | grep down | awk '{ print $1 }')
    echo $list_com_down
}


#
# Kiểm tra số lượng VM trên các node compute down
#
vm_compute_down(){
    echo "Kiem tra VM tren node $1"
    # Đếm số lượng VM trên compute
    list_vm=`openstack server list --host $1 -f value -c ID -c Status | wc -l`
    if [ $list_vm -eq 0 ]
    then 
        return 0
    else
        return 1
    fi
    exit   
}


#
# Thực hiện cứu VM tren compute down 
# 
evacuate_node_compute(){
    echo evacuate node $1
    nova host-evacuate $1
}


#
# Main function
#
main(){
    list_com_down=$(node_com_down)
       
    if [ -z "$list_com_down" ]
    then 
        echo "Khong co node compute down"
        exit 0
    else
        echo "Node compute down: "
        echo $list_com_down
        for com in $list_com_down
        do 
            vm_compute_down $com
            tmp=$?
            if [ $tmp -eq 0 ]
            then 
                echo "Node $com khong co VM"
            else
                # Node ton tai VM -> thuc hien evacuate
                evacuate_node_compute $com
            fi    
        done
        exit 0
    fi
}
 
main
