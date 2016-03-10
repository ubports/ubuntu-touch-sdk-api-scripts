# Setting up your Beaglebone Black

![Beaglebone Black image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/beaglebone.png "Beaglebone Black image")

From your desktop computer, you can download and install a pre-built Snappy Ubuntu Core 16.04 image for your Beaglebone Black and copy it to an SD card. You can then get started with your project!

> Make sure your board is connected to the same network as your computer to manage Ubuntu Core remotely via SSH, or has a screen and keyboard attached if you prefer managing Ubuntu Core directly on the board.

## Downloading and installing

1. Start by **downloading the Ubuntu Core image** for Beaglebone Black in your **Downloads** folder from [this link](http://people.canonical.com/~mvo/all-snaps/bbb-all-snap.img.xz).
Once the download is finished, you’ll have a zip file named bbb-all-snap.img.xz.

1. **Extract** the downloaded zip file into your Downloads folder. You should now have an uncompressed file named bbb-all-snap.img.
> You might have to install archive extractor software, like [7-zip](http://www.7-zip.org/) or similar as the standard tools do not support xz

1. **Insert your SD card**. Ensure there is no data you care about on the SD card before performing next steps below.

1. **Copy your downloaded image to the SD card**. Install and launch [Win32DiskImager](http://sourceforge.net/projects/win32diskimager/files/latest/download).
 > Find out where what drive your SD card is mounted to. Open a File Explorer window to check which drive your SD card is listed under.  Here is an example of a card listed under **E:** and the setup in Diskimager.

 ![Windows drives](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/windows-drives.png)

  Win32DiskImager will need 2 elements:
   * *An Image File* which is the file you want to copy on your SD Card. Navigate to your *Downloads* folder and select the bbb-all-snap.img image you have just extracted.
   * *A Device* which is the location of your SD card. Select the Drive in which your SD card is mounted.

   ![Win32DiskImager image selection](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/windows-diskimager-setup.png)

  > To be safe, unplug every External USB Drive you may have connected to your PC.

  When ready click on Write and wait for the process to complete.

1. Exit from Win32DiskImager. **Eject** the SD card from the File Explorer window and **insert it** in your Beaglebone Black.

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your Beaglebone Black and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)

Since we require our own boot loader in order to be fully compatible with Snappy, it's recommended to remove the bootloader available in the eMMC partition:
* On first boot (or each boot if you don't want to erase the bootloader available at the eMMC), you can also force it to boot to the sd card by pressing the user/boot switch button before powering up the device.
* Then, to remove the bootloader in the eMMC partition, you can run the following command on you Ubuntu Core system: `sudo dd if=/dev/zero of=/dev/mmcblk1 bs=1024 count=1024`


Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
