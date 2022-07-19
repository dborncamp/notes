# ThunderBird

They are looking to get CI/CD processes for all of the codebase.
They want a GitLab Runner running a shell executer that can ssh out onto an attached board.
This will run _"hardware in the loop"_ testing via ssh.

## Servers

`ssh dborncam@plfsw-lx`

I will need sudo access for `gitlab-runner` on the server to start the server.
I should run `gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner` after getting that access.
Then I should be able to get a runner to talk to GitLab.

The runner config:

```toml
concurrent = 1
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "plfsw-lx"
  url = "https://gitlab.aero.ball.com/"
  token = "8qKHKfMecq9t5a-TWKRo"
  executor = "shell"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]

```

```bash
sudo gitlab-runner install --working-directory=/export/home/gitlab-runner --config /etc/gitlab-runner/config.toml --user gitlab-runner
sudo gitlab-runner start
sudo gitlab-runner register --url https://gitlab.aero.ball.com/ --registration-token LNkJtfUNSxjbiZpoqLG28qKHKfMecq9t5a-TWKRo
```

The server is at:

ssh dborncam@plfsw-lx

The board is at 192.168.0.64 `ssh-keygen -R 192.168.0.64 && ssh root@192.168.0.64`.
Or use `ssh-keygen -R 192.168.0.64 && ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no root@192.168.0.64`

Root password on the board is `celp`

To start a new image use `grmon -nb -uart /dev/leap1_dsu -baud 921600 -c ~/core/tools/grmon_config_leap700.scr`

Then type `laod /opt/celp/linuxbuild-2.0.0_3/output/images/image.ram`

Then `go`

Leave the terminal running

```shell
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCwTcWOO8osQFmkvHAaylX3Uo+DdCEJn8WfOVoMoCIavtcoLS0GhGy5g6jo47KBOtdHg8m8d7shEhGEiNBLjqAE/wMJrV/deQnwI2Bfhvv7D9jkX4fOzA0ZNJKHI6hv3pLkaLK6iOXeULwCUBhDXpw7+BrK8D9k+YzXBPQ46jpyS6n+bzoeZgxNd4QgwdoW4tHENt47Mj1INRy1scPSK3FKSuvmFrUy4LyK4xZDOVqzixqg2nRS/tN9HHibMB0A9/XOaTMvJk0hykh7k1o0OLBPNNUec8f+9qM/AEHXi+wtcuKhtEm6bfYJskIMDllTctvV4WmWBqQm+MZiLkc+ZVNz dborncam@plfsw-lx" > /root/.ssh/authorized_keys
echo "AuthorizedKeysFile  /etc/ssh/authorized_keys" > /etc/ssh/sshd_config
```

To get files onto the image involves parsing https://confluence.aero.ball.com/display/CELP/Build+Guides+for+CELP to figure out that the normal build processes don't work and that the root filesystem is managed by MkProm.
The root file system is built by buildroot then loaded using mkprom so the kernal config will need to be updated with the correct cpio file.
To add files:

- add the files to `/opt/celp/configs/rootfs/`
- change the kernel config `linux/build-linux/.config` to point to the right archive.
By default, it is hardcoded to an old build. Set: `CONFIG_INITRAMFS_SOURCE="/opt/celp/linuxbuild-2.0.0_3/dist/.rootfs.cpio"`.
The path will need to be changed to reference the correct rootfs in the build.

To view the files in the rootfs use: `cpio --list < /opt/celp/linuxbuild-2.0.0_3/dist/buildroot/build-br/images/rootfs.cpio`

Documentation on the process: https://confluence.aero.ball.com/pages/viewpage.action?pageId=121937369
