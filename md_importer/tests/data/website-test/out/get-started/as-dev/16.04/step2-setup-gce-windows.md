# Setting up an instance on Google Cloud Engine

![Google Cloud Engine image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/gce.png "Google Cloud Engine image")

This is the process to launch snappy Ubuntu Core 16.04 on Google Cloud Engine from an Ubuntu developer desktop.
You can then get started with your project!

> As your cloud instances won't be on the same network than your machine, you will need to replace all reference when
> connecting through web or ssh from **webdm.local** to the **<external-ip>** you got from your cloud provider.

## Setup on Google Cloud Engine

### Pre-requisites

1. If you do not already have a Google Compute Engine Account, you can [sign up online](https://cloud.google.com/compute/docs/signup).
1.  As part of the Google Compute Engine account sign up process, you will need to create a project for use. Also make
sure that the project has the Compute Engine API enabled, by going to APIs & auth > APIs > Compute Engine API on the
[Google Developers Console](https://console.developers.google.com).

### Install GCE client tool

For more information on how to install the GCE CLI tools on your platform, check out [their website](https://cloud.google.com/compute/)

Note as well that some instructions can vary slightly. You can as well visit [this link](http://www.ubuntu.com/download/desktop/create-a-usb-stick-on-windows)
for getting the instructions on how to create an Ubuntu live disk.

### Setup your account and configuration

Now that you have a Google Compute Engine account setup and the cli tools installed, you'll need to configure the tools.

1. The Google Cloud SDK uses OAuth2 to authenticate the CLI commands.
```sh
$ gcloud auth login
<follow the on-screen instructions>
```

1. To make CLI use easier, let's set a couple of things up as default. First let's set a default project.
```sh
$ gcloud config set project <ID OF PROJECT>
```

1. Let's set default zone and region. Before you set default zone and region, you'll need to figure out what are
available. To get a list of the zones run:

```sh
$ gcloud compute zones list
NAME           REGION       STATUS          NEXT_MAINTENANCE TURNDOWN_DATE
asia-east1-b   asia-east1   UP
asia-east1-c   asia-east1   UP
asia-east1-a   asia-east1   UP
europe-west1-c europe-west1 UP
europe-west1-b europe-west1 UP
europe-west1-a europe-west1 UP (DEPRECATED)
us-central1-f  us-central1  UP
us-central1-b  us-central1  UP
us-central1-a  us-central1  UP
```

In our example, we'll pick **us-central1-f** as our default:
```sh
$ gcloud config set compute/zone us-central1-f
$ gcloud config set compute/region us-central1
```

1. It's now time to get SSH keys setup and Google Compute Engine configured to use them. If you already have an SSH key, you can
 skip creating an SSH key. Otherwise, create an SSH key for login in:
```sh
$ ssh-keygen -t ecdsa -b 521 -f ~/.ssh/snappy-gce
```

Let's pass the SSH key information to the Compute Engine. The following command will add the SSH key to every instance launched
```sh
$ gcloud compute project-info add-metadata --metadata-from-file sshKeys=~/.ssh/snappy-gce.pub
```

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
Here's how you can find the list of available snappy images on GCE:
```sh
$ gcloud compute images list --no-standard-images --project ubuntu-snappy
NAME                                       PROJECT       ALIAS DEPRECATED STATUS
ubuntu-snappy-core-1504-stable-2-v20150423 ubuntu-snappy                  READY
```

In this example, we are going to use ubuntu-snappy-core-1504-stable-2-v20150423 as the image name.

### First Ubuntu Core instance

 The following command will create and launch an instance. It will return when the instance has launched and is available.
 ```sh
$ gcloud compute instances create \
snappy-test \
--image-project ubuntu-snappy \
--image ubuntu-snappy-core-1504-stable-2-v20150423 \
--metadata-from-file user-data=cloud.cfg
```

That's it. Your instance is ready to login to now via ssh using the external IP address returned from the successful instance creation.

### Check that the instance is running

Typically you would use gcloud compute ssh <name> at this point for a regular Ubuntu instance. However, at this time,
Ubuntu Core does not have event-based user creation. So you will need to manually SSH in as the Ubuntu user:
```sh
$ ssh -i ~/.ssh/snappy-gce ubuntu@<EXTERNAL IP ADDRESS>
```

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your Google Cloud Engine and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

> Remember that if your device/cloud isn't on the same network or your vm use port redirection, adapt **webm.local** and
> the port with the appropriate external IP and ports.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)



Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
