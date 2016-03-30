# Setting up an instance on Azure

![Azure image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/azure.png "Azure image")

This is the process to launch snappy Ubuntu Core 16.04 on Azure from an Ubuntu developer desktop.
You can then get started with your project!

> As your cloud instances won't be on the same network than your machine, you will need to replace all reference when
> connecting through web or ssh from **webdm.local** to the **<external-ip>** you got from your cloud provider.

## Setup on Microsoft Azure

### Pre-requisite

If you do not already have an Azure, you can [sign up online](https://account.windowsazure.com).

### Install Azure client tool

Open a terminal with <Ctrl>+<Alt>+t and run the following commands:
```sh
$ sudo apt update
$ sudo apt install nodejs npm nodejs-legacy
$ sudo npm install -g azure-cli
```

### Setup your account and configuration

Now that you have an Azure setup and the cli tools installed, you'll need to configure the tools.

Just run:
```sh
$ azure account download
```
Then follow the instructions provided.

Next, prepare your SSH Keys for Azure. Snappy is secure by default; there is no default password. In order to login to
your Ubuntu Core instance on Azure you will need to supply an SSH key that will work with Microsoft Azure.

 * If you have an existing key, let's convert it:
```sh
$ openssl req -x509  -key ~/.ssh/id_rsa -nodes -days 365  \
-newkey rsa:2048 -out ~/.ssh/snappy_azure.pem -subj "/CN=${USER}/"
```

 * If you don't have one, let's create a new key:
```sh
$ openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
-keyout ~/.ssh/snappy_azure.key -out ~/.ssh/snappy_azure.pem -subj "/CN=${USER}/"
```
After either of the above **openssl** commands, you'll want to copy the key and **snappy_azure.pem** to `~/.ssh`

### SSH configuration

SSH is disabled by default on snappy systems, for enhanced security. You can turn it on by providing some configuration
when you launch the instance, and for that you will need to create a cloud-init configuration file that will turn on SSH
so you can login to play with Ubuntu Core.

Create a file called `cloud.cfg` with the exact lines of text you see below:
```
# cloud-config
snappy:
    ssh_enabled: True
```

### Available Images
Here's how you can find the list of available snappy images on Azure:
```sh
$ azure vm image list | grep "Ubuntu-.*-Snappy"
data:    b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-15.04-Snappy-core-amd64-edge-201507020801-108-en-us-30GB
```
The naming convention is: `<publisher guuid>__Ubuntu-<version>-Snappy-<flavor>-<arch>-<publish_date>-<version>-<locale>-<disk_size>`.
Canonical's publisher GUUID on Microsoft Azure is **b39f27a8b8c64d52b05eac6a62ebad85**.

In our example, we'll use the latest image at the time of this writing, which is **b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-15.04-Snappy-core-amd64-edge-201507020801-108-en-us-30GB**.
We suggest you to replace the tags for date and version to use the latest one available.

### First Ubuntu Core instance

Now you are ready to launch the image on Azure. The general form of this command is:
```sh
$ azure vm create <NAME> <IMAGE> <USER> <PASSWORD> <flags>
```
The following is an example command. Remember to replace the image name by the latest available, and to replace {UNIQUE_ID} with something that uniquely identifies your machine, like snappy-test-{your_nickname} :

```sh
$ azure vm create {UNIQUE_ID} \
b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-15.04-Snappy-core-amd64-edge-201507020801-108-en-us-30GB ubuntu \
--location "North Europe" --no-ssh-password \
--ssh-cert ~/.ssh/snappy_azure.pem --custom-data ~/cloud.cfg -e
```

### Check that the instance is running

You will need to wait a minute or two while Azure provisions and launches the instance. It will show up in the list of your running instances:
```sh
$ azure vm list
info:    Executing command vm list
+ Getting virtual machines
data:    Name         Status     Location      DNS Name                  IP Address
data:    -----------  ---------  ------------  ------------------------  ----------
data:    snappy-test  ReadyRole  North Europe  snappy-test.cloudapp.net  <VARIABLE>
info:    vm list command OK
```

When the image state is **ReadyRole** you can make a note of the hostname from the listing above, and login with SSH to the instance (replace snappy-test.cloudapp.net with the DNS name from your azure vm list command):
```sh
$ ssh -i ~/.ssh/snappy_azure.key ubuntu@snappy-test.cloudapp.net
```

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your Azure and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

> Remember that if your device/cloud isn't on the same network or your vm use port redirection, adapt **webm.local** and
> the port with the appropriate external IP and ports.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)



Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
