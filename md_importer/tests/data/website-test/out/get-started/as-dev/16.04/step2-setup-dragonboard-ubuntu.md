# Setting up your DragonBoard

![DragonBoard image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/dragonboard.png "DragonBoard image")

From your desktop computer, you can download and install a pre-built Snappy Ubuntu Core 16.04 image for your DragonBoard and copy it to an SD card. You can then get started with your project!

> Make sure your board is connected to the same network as your computer to manage Ubuntu Core remotely via SSH, or has a screen and keyboard attached if you prefer managing Ubuntu Core directly on the board.

## Downloading and installing

1. Start by **downloading the Ubuntu Core image** for DragonBoard in your current folder.
```sh
wget http://people.canonical.com/~ogra/snappy/all-snaps/dragonboard/dragon-all-snap.img.xz
```
Once the download is finished, you’ll have a zip file named dragon-all-snap.img.xz.

1. **Insert your SD card**. Ensure there is no data you care about on the SD card before performing next steps below.

1. **Unmount it**: if your SD card is mounted when you insert it into your computer (you will know it if the file manager automatically opens a window showing the card's contents), you must manually unmount it before writing the snappy image to it. Either eject your SD card from the file manager, or from the command line: `sudo umount /media/$USER/`

1. **Copy your downloaded image to the SD card**. You must specify the path to the disk device representing your SD card in the dd command below. Common device paths for the SD card disk device are either of the form **/dev/sdX** (such as **/dev/sdb**, not /dev/sdb1!) or **/dev/mmcblk0** (not /dev/mmcblk0p1!)
```sh
xzcat dragon-all-snap.img.xz | sudo dd of=/dev/sdX bs=32M
sync
```
 You will be prompted to enter your password after this command.

 > Note that this operation length can vary depending on your SD card speed. There is no progress displayed unless you send SIGINFO signal pressing Ctrl+T.

1. **Eject** the SD card physically from your PC and **insert it** in your DragonBoard.

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your DragonBoard and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)

<<ADDITIONAL_FIRST_BOOT_NOTES>>

Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
