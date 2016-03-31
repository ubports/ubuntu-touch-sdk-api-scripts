# Setting up your KVM VM

![KVM image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/kvm.png "KVM image")

From your desktop computer, you can download and install a pre-built Snappy Ubuntu Core 16.04 image for your KVM VM. You can then get started with your project!
> Note that we only provide instructions to start the VM from Ubuntu. This is why you will find below instructions
> on how to start a live USB image. You can as well run this Ubuntu version in a VM, or install it.

## Create an Ubuntu live disk from Mac

Visit [this link](http://www.ubuntu.com/download/desktop/create-a-usb-stick-on-mac-osx) for getting the instructions on how to create an Ubuntu live disk.

## Checking for KVM support

Now that you have your Ubuntu installation running, we will install KVM and check that your hardware has the support
enabled before downloading the Ubuntu Core image.

### KVM setup

1. Open a terminal with the key combination Ctrl+Alt+t.
1. Run
```sh
$ sudo apt install qemu-kvm
```
1. Once installed, check for the hardware acceleration support:
```sh
$ kvm-ok
INFO: /dev/kvm exists
KVM acceleration can be used
```

This is the best outcome — it means that snappy will run fast on your system, taking advantage of hardware acceleration
in your CPU. If KVM is not supported on your system we recommend you try Ubuntu Core on a cloud instead.

### Download and preparing your Ubuntu Core image

1. Start by **downloading the Ubuntu Core image** for KVM in your current folder.
```sh
wget http://UNPUBLISHED/kvm-image-16.04.img.xz
```
Once the download is finished, you’ll have a zip file named kvm-image-16.04.img.xz.

1. **Unpack your downloaded image to the disk**.
```sh
unxz kvm-image-16.04.img.xz
```

You should now have an uncompressed file named kvm-image-16.04.img.

 > Note that this operation length can vary depending on your disk speed. There is no progress displayed unless you send SIGINFO signal pressing Ctrl+T.

### Start your KVM instance

You can now launch this virtual machine with KVM:
```sh
$ kvm -m 512 -redir :8022::22 -redir :8080::80 -redir :8042::4200 kvm-image-16.04.img
```

You should see a window pop up, with your Ubuntu Core virtual machine booting inside it.

 > Note that we redirect some ports from the guest Ubuntu Core image to the host. Here:
 > Port 22 (ssh) is redirected to 8022, port 80 to 8080 and port 4200 (webdm default port) to 8042.
 > When you get instructions to connect to some ports on the guests, you can replace with localhost:<host_port> instead.

Consequently, to connect to your VM, you will need to replace ```ssh ubuntu@webdm.local``` by
```ssh -p 8022 ubuntu@localhost```.

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your KVM and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://localhost:8042.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)



Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
