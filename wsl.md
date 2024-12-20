# Windows Subsystem for Linux

***Note After 4/13/23 this failed to work***

## Installing

List off potential linux distros

`wsl --list --online`

I went with ubuntu:

`wsl --install -d Ubuntu`

## Running

Either use their built in ubuntu terminal (a bash shell by default), PowerShell (use command `wsl`), or use other terminals.
I am not sold on the ubuntu terminal yet as history seems to be shaky at best and colors are extreme.

## Useage

The home directory for WSL is located at: `\\wsl$\Ubuntu\home\dave`

### CA Certificates

Ball uses self signed certificates which aren't trusted by default, so we need to add the CAs to verify any connection.
Copy the `ca_certificates` directory into the home directory on wsl, move them into the `/usr/local/share/ca-certificates/` directory and then update the certs.

``` bash
sudo cp -R ca-certificates/* /usr/local/share/ca-certificates/
sudo update-ca-certificates --fresh
```

### Docker

For installing Docker, I just used docker desktop and was able to connect to it inside WSL.

So we don't need to get things running using sudo every time

``` bash
sudo groupadd docker
sudo usermod -aG docker $USER
```

## Communication Over Global Protect

Make a file called `wsl-vpnkit` that contains:

```sh
#!/bin/sh

POWERSHELL="$(command -v powershell.exe || echo '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe')"
USERPROFILE=$(wslpath "$($POWERSHELL -c 'Write-Host -NoNewline $env:USERPROFILE')")
CONF_PATH="$USERPROFILE/wsl-vpnkit/wsl-vpnkit.conf"
SOCKET_PATH="/var/run/wsl-vpnkit.sock"
PIPE_PATH="//./pipe/wsl-vpnkit"
TAP_PID_PATH="/var/run/vpnkit-tap-vsockd.pid"

VPNKIT_STORE="/files/vpnkit/vpnkit.exe"
NPIPERELAY_STORE="/files/npiperelay/npiperelay.exe"
VPNKIT_PATH="$USERPROFILE/wsl-vpnkit/wsl-vpnkit.exe"
NPIPERELAY_PATH="$USERPROFILE/wsl-vpnkit/npiperelay.exe"
TAP_NAME="eth1"
VPNKIT_GATEWAY_IP="192.168.67.1"
VPNKIT_HOST_IP="192.168.67.2"
VPNKIT_LOWEST_IP="192.168.67.3"
VPNKIT_HIGHEST_IP="192.168.67.14"
VPNKIT_WSL2_IP="$VPNKIT_LOWEST_IP"
VPNKIT_DEBUG=
WSL2_GATEWAY_IP="$(cat /etc/resolv.conf | awk '/^nameserver/ {print $2}')"
CHECK_HOST=example.com
DNS_IP="$VPNKIT_GATEWAY_IP"
CHECK_DNS=1.1.1.1

echo "starting wsl-vpnkit"
if [ -f "$CONF_PATH" ]; then
    . "$CONF_PATH"
    echo "loaded $CONF_PATH"
fi

hash () {
    md5sum "$1" | awk '{ print $1 }'
}

install_file () {
    if [ -f $2 ]; then
        if [ ! -f "$3" ]; then
            mkdir -p "$(dirname $3)"
            cp $2 "$3"
            echo "copied $1 to $3"
        else
            echo "$1 exists at $3"
            if [ `hash $2` != `hash "$3"` ]; then
                cp -f $2 "$3"
                echo "updated $1 at $3"
            fi
        fi
        if [ ! -f "$2-ln" ]; then
            ln -s "$3" "$2-ln"
            echo "created symbolic link at $2-ln"
        fi
    fi
}

install () {
    install_file vpnkit.exe "$VPNKIT_STORE" "$VPNKIT_PATH"
    install_file npiperelay.exe "$NPIPERELAY_STORE" "$NPIPERELAY_PATH"
}

relay () {
    echo "starting socat-npiperelay..."
    NPIPERELAY_SOCAT_PATH="$NPIPERELAY_PATH"
    if [ -f "$NPIPERELAY_STORE-ln" ]; then
        NPIPERELAY_SOCAT_PATH="$NPIPERELAY_STORE-ln"
        echo "using $NPIPERELAY_SOCAT_PATH for npiperelay.exe"
    fi
    socat UNIX-LISTEN:$SOCKET_PATH,fork,umask=007 EXEC:"$NPIPERELAY_SOCAT_PATH -ep -s $PIPE_PATH",nofork
}

relay_wait () {
    echo "waiting for $SOCKET_PATH ..."
    while [ ! -S "$SOCKET_PATH" ]; do
        sleep 0.1
    done
    echo "found $SOCKET_PATH"
}

vpnkit () {
    echo "starting vpnkit..."
    WIN_PIPE_PATH=$(echo $PIPE_PATH | sed -e "s:/:\\\:g")
    CMD='"$VPNKIT_PATH" \
        --ethernet $WIN_PIPE_PATH \
        --gateway-ip $VPNKIT_GATEWAY_IP \
        --host-ip $VPNKIT_HOST_IP \
        --lowest-ip $VPNKIT_LOWEST_IP \
        --highest-ip $VPNKIT_HIGHEST_IP \
    '
    if [ "$VPNKIT_DEBUG" ]; then
        CMD="$CMD"' --debug'
    fi
    eval "$CMD"
}

tap () {
    echo "starting vpnkit-tap-vsockd..."
    vpnkit-tap-vsockd --tap $TAP_NAME --path $SOCKET_PATH --daemon --pid $TAP_PID_PATH
    echo "started vpnkit-tap-vsockd"
}

ipconfig () {
    echo "configuring ip..."
    ip a add $VPNKIT_WSL2_IP/255.255.255.0 dev $TAP_NAME
    ip link set dev $TAP_NAME up
    ip route | grep -e "$VPNKIT_GATEWAY_IP" -e 'default' | tr '\n' '\0' | xargs -0 -n 1 sh -c 'ip route del $1' argv0
    ip route add default via $VPNKIT_GATEWAY_IP dev $TAP_NAME
    echo "ip config done"

    echo "adding rules to iptables..."
    iptables -t nat -A PREROUTING -d $WSL2_GATEWAY_IP/32 -p udp -m udp --dport 53 -j DNAT --to-destination $DNS_IP:53
    iptables -t nat -A PREROUTING -d $WSL2_GATEWAY_IP/32 -p tcp -m tcp --dport 53 -j DNAT --to-destination $DNS_IP:53
    iptables -t nat -A PREROUTING -d $WSL2_GATEWAY_IP/32 -j DNAT --to-destination $VPNKIT_HOST_IP
    iptables -t nat -A OUTPUT -d $WSL2_GATEWAY_IP/32 -p udp -m udp --dport 53 -j DNAT --to-destination $DNS_IP:53
    iptables -t nat -A OUTPUT -d $WSL2_GATEWAY_IP/32 -p tcp -m tcp --dport 53 -j DNAT --to-destination $DNS_IP:53
    iptables -t nat -A OUTPUT -d $WSL2_GATEWAY_IP/32 -j DNAT --to-destination $VPNKIT_HOST_IP
    iptables -t nat -A POSTROUTING -o $TAP_NAME -j MASQUERADE
    echo "iptables done"
}

check_ping () {
    ping -$1 -c 1 $3 >/dev/null && \
        echo "check: ✔️ ping success to IPv$1 $2 ($3)" || \
        echo "check: $([ $1 = '6' ] && echo '➖' || echo '❌') ping fail to IPv$1 $2 ($3)"
}

check_dns () {
    TYPE=$([ "$1" = "4" ] && echo 'A' || echo 'AAAA')
    nslookup -type=$TYPE $2 $3 >/dev/null && \
        echo "check: ✔️ nslookup success for $2 $TYPE using $3" || \
        echo "check: ❌ nslookup fail for $2 $TYPE using $3"
}

check_https () {
    wget --spider -q $1 && \
        echo "check: ✔️ wget success for $1" || \
        echo "check: ❌ wget fail for $1"
}

check () {
    check_ping 4 'WSL 2 gateway / Windows host' $WSL2_GATEWAY_IP
    check_ping 4 'VPNKit Windows host' $VPNKIT_HOST_IP
    check_ping 4 'VPNKit gateway' $VPNKIT_GATEWAY_IP
    check_dns 4 $CHECK_HOST $DNS_IP
    check_dns 4 $CHECK_HOST $VPNKIT_GATEWAY_IP
    check_dns 4 $CHECK_HOST $WSL2_GATEWAY_IP
    check_dns 4 $CHECK_HOST $CHECK_DNS
    check_ping 4 'external host' $CHECK_HOST
    check_dns 6 $CHECK_HOST $DNS_IP
    check_dns 6 $CHECK_HOST $VPNKIT_GATEWAY_IP
    check_dns 6 $CHECK_HOST $WSL2_GATEWAY_IP
    check_dns 6 $CHECK_HOST $CHECK_DNS
    check_ping 6 'external host' $CHECK_HOST
    check_https "https://$CHECK_HOST"
}

cleanup () {
    echo "cleaning up iptables..."
    iptables -t nat -S | grep $VPNKIT_GATEWAY_IP | cut -d " " -f 2- | tr '\n' '\0' | xargs -0 -r -n 1 sh -c 'iptables -t nat -D $1' argv0
    iptables -t nat -S | grep $VPNKIT_HOST_IP | cut -d " " -f 2- | tr '\n' '\0' | xargs -0 -r -n 1 sh -c 'iptables -t nat -D $1' argv0
    iptables -t nat -S | grep $TAP_NAME | cut -d " " -f 2- | tr '\n' '\0' | xargs -0 -r -n 1 sh -c 'iptables -t nat -D $1' argv0
    echo "iptables cleanup done"

    echo "cleaning up ip..."
    ip route | grep -e "$VPNKIT_GATEWAY_IP" -e 'default' | tr '\n' '\0' | xargs -0 -n 1 sh -c 'ip route del $1' argv0
    ip link set dev $TAP_NAME down
    ip route add default via $WSL2_GATEWAY_IP dev eth0
    echo "ip cleanup done"

    if [ -f "$TAP_PID_PATH" ]; then
        echo "stopping vpnkit-tap-vsockd"
        kill -- -$(cat $TAP_PID_PATH)
        echo "stopped vpnkit-tap-vsockd"
    fi

    $POWERSHELL -c 'Stop-Process -Force -Name wsl-vpnkit -ErrorAction SilentlyContinue'
}

close () {
    cleanup
    echo "stopped wsl-vpnkit"
    kill 0
}

if [ ${EUID:-$(id -u)} -ne 0 ]; then
    echo "Please run this script as root"
    exit 1
fi

cleanup
install
relay &
relay_wait
vpnkit &
tap
ipconfig
check
trap close exit
trap exit int term
wait
```

Add the following lines to the sudoers file (`sudo visudo`):

```bash
Cmnd_Alias      CMDS = /home/dave/wsl-vpnkit

dave ALL=NOPASSWD: CMDS
```

`sudo /home/dave/wsl-vpnkit` will need to be run in a terminal now when using global protect.

## Install K3d or K8s

You will need to contact ITS to get added to the `FW-GoogleDrive-Access` group.
Then k3d can be installed on the machine.

## Install Terraform

Follow these instruction until step 5:
[https://techcommunity.microsoft.com/t5/azure-developer-community-blog/configuring-terraform-on-windows-10-linux-sub-system/ba-p/393845](https://techcommunity.microsoft.com/t5/azure-developer-community-blog/configuring-terraform-on-windows-10-linux-sub-system/ba-p/393845)
