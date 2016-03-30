# Setting up your Intel® NUC

![Intel® NUC image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/Thin_Canyon_NUC_Front_Angle_Board.png "Intel® NUC image")

Installing Snappy Ubuntu Core on your Intel® NUC, only takes 3 steps and a 2G USB key:
1. Install a live version of Ubuntu Classic on a USB key.
1. Boot on your Intel® NUC from the live USB key.
1. Install Ubuntu Core onto Intel® NUC disk from the live session.
And you can get started with your project!

> Make sure your board is connected to the same network as your computer to manage Ubuntu Core remotely via SSH, or has a screen and keyboard attached if you prefer managing Ubuntu Core directly on the board.

## Create an Ubuntu live disk from Mac

Visit [this link](http://www.ubuntu.com/download/desktop/create-a-usb-stick-on-mac-osx) for getting the instructions on how to create an Ubuntu live disk.

## Installing from Live disk

Now that you have your Live Disk USB key, we will install the Ubuntu Core image after booting that Live Disk.

### Preparing the NUC (if using internal ROM as disk)
> Note that this step is only necessary in case you want to install Ubuntu Core on the 4GB eMMC Built-In Storage.
If you wired an ssd disk to your NUC, this section can be skipped.
1. Start your NUC by pressing the On button while pressing F2 during the boot up, this will open the BIOS settings.
1. On the initial screen, access the "advanced" tab and press to access the "Devices and Peripherals" Tab.
1. On the "Devices and Peripherals" menu, under the "On board devices" submenu, make sure that the emmc checkbox ("4GB emmc Built-in Storage") is checked.
  > If you didn't find this option, this means that you need to update your NUC BIOS to latest version. For this, you can follow online instructions on the [Intel website](http://www.intel.com/content/www/us/en/support/boards-and-kits/000005850.html).
1. In the "Boot" menu, "Secure boot" submenu, make sure that the "secure boot" is not checked.


### Booting from the Live CD

1. Insert the USB key with the Ubuntu live distribution
1. Start you Intel® NUC and push **F10** to enter the boot menu.
1. Select the USB key as boot option.
1. Choose **"Try Ubuntu without installing”**.

### Installing Ubuntu Core onto your Intel® NUC

Once the Live distro is running, open a terminal with the key combination Ctrl+Alt+t.

1. Start by **downloading the Ubuntu Core image** for Intel® NUC in your current folder.
```sh
wget http://people.canonical.com/~platform/snappy/ubuntu-core-15.04-intel-nuc.img.xz
```
Once the download is finished, you’ll have a zip file named ubuntu-core-15.04-intel-nuc.img.xz.

1. **Copy your downloaded image to the disk**. You must specify the path to the disk device representing your disk in the dd command below. Common device paths for the ssd disks are of the form **/dev/sdX** (such as **/dev/sda**, not /dev/sda1!). Please note that if you want to use the eMMC instead of an internal ssd drive, replace **/dev/sdX** by **/dev/mmcblk0** which refers to the eMMC option.

```sh
xzcat ubuntu-core-15.04-intel-nuc.img.xz | sudo dd of=/dev/sdX bs=32M
sync
```

 > Note that this operation length can vary depending on your disk speed. There is no progress displayed unless you send SIGINFO signal pressing Ctrl+T.

1. ​You can now **reboot** your Intel® NUC

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your Intel® NUC and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

> Remember that if your device/cloud isn't on the same network or your vm use port redirection, adapt **webm.local** and
> the port with the appropriate external IP and ports.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)



Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
