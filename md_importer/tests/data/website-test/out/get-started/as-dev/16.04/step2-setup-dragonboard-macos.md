# Setting up your DragonBoard

![DragonBoard image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/dragonboard.png "DragonBoard image")

From your desktop computer, you can download and install a pre-built Snappy Ubuntu Core 16.04 image for your DragonBoard and copy it to an SD card. You can then get started with your project!

> Make sure your board is connected to the same network as your computer to manage Ubuntu Core remotely via SSH, or has a screen and keyboard attached if you prefer managing Ubuntu Core directly on the board.

## Downloading and installing

1. Start by **downloading the Ubuntu Core image** for DragonBoard in your current folder.
```sh
curl -O http://people.canonical.com/~ogra/snappy/all-snaps/dragonboard/dragon-all-snap.img.xz
```

1. **Extract** the downloaded zip file into your Downloads folder by double clicking on it. You should now have an uncompressed file named dragon-all-snap.img.
> You might have to install archive extractor software, like [The Unarchiver](https://itunes.apple.com/gb/app/the-unarchiver/id425424353?mt=12) or similar as the standard tools do not support xz

1. **Insert your SD card**. Ensure there is no data you care about on the SD card before running the commands below.

1. **Determine which disk to write to and inmount it**.
 * Run
```sh
diskutil list
```
 In the results identify your SD card, it will probably an entry like the one below:
```sh
/dev/disk0
  #:                       TYPE NAME                    SIZE       IDENTIFIER
  0:      GUID_partition_scheme                        *500.3 GB   disk0
/dev/disk2
  #:                       TYPE NAME                    SIZE       IDENTIFIER
  0:                  Apple_HFS Macintosh HD           *428.8 GB   disk1
                                Logical Volume on disk0s2
                                E2E7C215-99E4-486D-B3CC-DAB8DF9E9C67
                                Unlocked Encrypted
/dev/disk3
  #:                       TYPE NAME                    SIZE       IDENTIFIER
  0:     FDisk_partition_scheme                        *7.9 GB     disk3
  1:                 DOS_FAT_32 NO NAME                 7.9 GB     disk3s1
```
 > Note that your SD Card must be DOS_FAT_32 formatted. The SIZE will be the size of your SD card, in this example an 8GB SD Card.

 Write down the number after /dev/disk that is associated with your SD card, in this case 3.

 * Unmount your SD card by entering the command:
 `diskutil unmountDisk /dev/diskX` where X is the number you just wrote down. When successful you should see a message similar to this one: *Unmount of all volumes on diskX was successful*.

1. **Copy your downloaded image to the SD card**. Note that you need to specify the path to the disk device with the number you just wrote down in previous step.
```sh
sudo dd if=~/Downloads/dragon-all-snap.img of=/dev/diskX bs=32MB
sync
```
You will be prompted to enter your Apple password after this command.

 > Note that this operation length can vary depending on your SD card speed. There is no progress displayed unless you send SIGINFO signal pressing Ctrl+T.

1. **Eject** the SD card physically from your Mac and **insert it** in your DragonBoard.

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your DragonBoard and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)

<<ADDITIONAL_FIRST_BOOT_NOTES>>

Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!