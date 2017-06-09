#!/usr/bin/env bash
set -e

RESOURCES=/tmp/packer/resources

# update the system
sudo yum update -y

#
# package installation
# ====================
# install yum packages
[ ! -z  "$(cat ${RESOURCES}/requirements.yum | xargs)" ] && \
    sudo xargs yum install -y < ${RESOURCES}/requirements.yum

# install pip packages
[ ! -z  "$(cat ${RESOURCES}/requirements.pip | xargs)" ] && \
    sudo pip install -r ${RESOURCES}/requirements.pip

# install gem packages
[ ! -z  "$(cat ${RESOURCES}/requirements.gem | xargs)" ] && \
    sudo xargs gem install < ${RESOURCES}/requirements.gem

#
# ADD YOUR CODE HERE
# ==================

# install openvpnsa
# curl -o /tmp/openvpn-as-2.1.4-CentOS7.x86_64.rpm http://swupdate.openvpn.org/as/openvpn-as-2.1.4-CentOS7.x86_64.rpm
# sudo yum localinstall -y /tmp/openvpn-as-2.1.4-CentOS7.x86_64.rpm

# sudo chkconfig ntpd on
# sudo chkconfig openvpnas on

# sudo usermod -p '$1$7zmilYcg$26kyThOp3xSWVNIMOogtE.' openvpn

# fix ifconfig executable
# sudo ln -sf /sbin/ifconfig /usr/sbin/ifconfig
