# Setting up your x86 Device

![x86 Device image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/baremetal.png "x86 Device image")

From your desktop computer, you can download and install a pre-built Snappy Ubuntu Core 16.04 image for your x86 Device and copy it to an SD card, USB key or external disk that you will attach and boot from. You can then get started with your project!

> Make sure your board or device is connected to the same network as your computer to manage Ubuntu Core remotely via SSH, or has a screen and keyboard attached if you prefer managing Ubuntu Core directly on the board or device.

You can use an **USB card** or **disk drive** that you will attach to after installing Ubuntu Core on it.
You will need to ensure that the boot order in BIOS/UEFI is set to try that USB storage or new disk first.


## Downloading and installing

1. Start by **downloading the Ubuntu Core image** for x86 Device in your current folder.
```sh
wget http://people.canonical.com/~mvo/all-snaps/amd64-all-snap.img.xz
```
Once the download is finished, you’ll have a zip file named amd64-all-snap.img.xz.

1. **Insert your SD card, USB card or external disk**. Ensure there is no data you care about on this disk or card before running the commands below.

1. **Unmount it**: if your SD/USB card or external disk is mounted when you insert it into your computer (you will know it if the file manager automatically opens a window showing the disk's contents), you must manually unmount it before writing the snappy image to it. Either eject your SD/USB card or external disk from the file manager, or from the command line: `sudo umount /media/$USER/`

1. **Copy your downloaded image to the SD/USB card or external disk**. You must specify the path to the disk device representing your destination disk in the dd command below. Common device paths for those are either of the form **/dev/sdX** (such as **/dev/sdb**, not /dev/sdb1!) or **/dev/mmcblk0** (not /dev/mmcblk0p1!)
```sh
xzcat amd64-all-snap.img.xz | sudo dd of=/dev/sdX bs=32M
sync
```
 You will be prompted to enter your password after this command.

 > Note that this operation length can vary depending on your destination disk speed. There is no progress displayed unless you send SIGINFO signal pressing Ctrl+T.

1. **Eject** the SD card physically from your PC and **insert it** in your x86 Device.

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your x86 Device and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

> Remember that if your device/cloud isn't on the same network or your vm use port redirection, adapt **webm.local** and
> the port with the appropriate external IP and ports.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)



Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
