# Setting up your Vagrant VM

![Vagrant image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/vagrant.png "Vagrant image")

From your desktop computer, you can download and install a pre-built Snappy Ubuntu Core 16.04 image for your Vagrant VM. You can then get started with your project!

For our Vagrant users, we are now publishing Snappy Images for Vagrant. These images are bit-for-bit the same as the KVM images,
but packaged for Vagrant. A special "cloud-config" drive is included that enables SSH.

> Note: Ubuntu core does not support DKMS modules at this time. This means that the shared /vagrant file system is not
supported, but we anticipate supporting shared file systems in the future.

## Installing Vagrant

1. Fetch and install [VirtualBox](https://virtualbox.org)
1. Install [Vagrant](https://vagrantup.com)

### Download your Ubuntu Core image

Simply run:

1. Go to a directory (vagrant workspace) which will contain this configuration for Ubuntu Core.
```sh
cd ubuntu-core
```
1. Now, **download and start the Ubuntu Core image** for Vagrant.
```sh
vagrant init http://cloud-images.ubuntu.com/snappy/16.04/core/stable/current/core-stable-amd64-vagrant.box
vagrant up
```

> Note that only the first vagrant up will download the Ubuntu Core image before starting up. Further vagrant up
> will only spawn some Ubuntu Core instances.

### Ensure your vm is started

Once you see a message stating that the box is up and ready to go, you can login using vagrant ssh.
```sh
vagrant ssh
```

After you are done with the image, you can shut it down with `vagrant shutdown` or `vagrant destroy` to remove the image.

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your Vagrant and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

> Remember that if your device/cloud isn't on the same network or your vm use port redirection, adapt **webm.local** and
> the port with the appropriate external IP and ports.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)



Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
