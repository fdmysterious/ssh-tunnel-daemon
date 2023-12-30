FROM alpine:3.19

# Install SSH server
RUN apk add --no-cache openrc openssh
RUN mkdir -p /run/openrc && touch /run/openrc/softlevel
RUN ash -c "echo 'PermitTunnel yes' >> /etc/ssh/sshd_config"
#RUN ash -c "echo 'AllowTcpForwarding yes' >> /etc/ssh/sshd_config"
#RUN ash -c "echo 'GatewayPorts yes' >> /etc/ssh/sshd_config"
RUN ash -c "sed -i 's/AllowTcpForwarding no/AllowTcpForwarding yes/g' /etc/ssh/sshd_config"
RUN ash -c "sed -i 's/GatewayPorts no/GatewayPorts yes/g' /etc/ssh/sshd_config"

#RUN rc-status && rc-service sshd start

ENTRYPOINT ["sh", "-c", "rc-status && rc-service sshd start && tail -f /dev/null"]
