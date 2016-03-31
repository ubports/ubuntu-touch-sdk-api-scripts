# Setting up your Raspberry Pi 2

![Raspberry Pi 2 image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/raspberry-pi.png "Raspberry Pi 2 image")

From your desktop computer, you can download and install a pre-built Snappy Ubuntu Core 16.04 image for your Raspberry Pi 2 and copy it to an SD card, USB key or external disk that you will attach and boot from. You can then get started with your project!

> Make sure your board or device is connected to the same network as your computer to manage Ubuntu Core remotely via SSH, or has a screen and keyboard attached if you prefer managing Ubuntu Core directly on the board or device.

You will flash and then insert a SD card with Ubuntu Core on it. Then, just power up your device and you are ready to go!


## Downloading and installing

1. Start by **downloading the Ubuntu Core image** for Raspberry Pi 2 in your **Downloads** folder from [this link](http://people.canonical.com/~mvo/all-snaps/rpi2-all-snap.img.xz).
Once the download is finished, you’ll have a zip file named rpi2-all-snap.img.xz.

1. **Extract** the downloaded zip file into your Downloads folder. You should now have an uncompressed file named rpi2-all-snap.img.
> You might have to install archive extractor software, like [7-zip](http://www.7-zip.org/) or similar as the standard tools do not support xz

1. **Insert your SD card, USB card or external disk**. Ensure there is no data you care about on this disk or card before performing the next steps below.

1. **Copy your downloaded image to the SD card or external disk**. Install and launch [Win32DiskImager](http://sourceforge.net/projects/win32diskimager/files/latest/download).
 > Find out where what drive your SD/USB card or external disk is mounted to. Open a File Explorer window to check which drive your didk is listed under.  Here is an example of a card listed under **E:** and the setup in Diskimager.

 ![Windows drives](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/windows-drives.png)

  Win32DiskImager will need 2 elements:
   * *An Image File* which is the file you want to copy on your disk. Navigate to your *Downloads* folder and select the rpi2-all-snap.img image you have just extracted.
   * *A Device* which is the location of your SD/USB card or external disk. Select the Drive in which it is mounted.

   ![Win32DiskImager image selection](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/windows-diskimager-setup.png)

  > To be safe, unplug every External USB Drive you may have connected to your PC.

  When ready click on Write and wait for the process to complete.

1. Exit from Win32DiskImager. **Eject** the SD/USB card or external disk from the File Explorer window and **insert or attach it** in your Raspberry Pi 2.

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your Raspberry Pi 2 and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

> Remember that if your device/cloud isn't on the same network or your vm use port redirection, adapt **webm.local** and
> the port with the appropriate external IP and ports.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)



Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
