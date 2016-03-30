# Setting up an instance on Amazon EC2

![Amazon EC2 image](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/devices/ec2.png "Amazon EC2 image")

This is the process to launch snappy Ubuntu Core 16.04 on Amazon EC2 from an Ubuntu developer desktop.
You can then get started with your project!

> As your cloud instances won't be on the same network than your machine, you will need to replace all reference when
> connecting through web or ssh from **webdm.local** to the **<external-ip>** you got from your cloud provider.

## Setup on Amazon EC2

### Pre-requisites

1. If you do not already have an AWS account, you can [sign up online](http://aws.amazon.com/).
1. Once you have signed up for AWS, create an access key by following [these instructions](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-set-up.html#cli-signup).

### Install EC2 client tool

Canonical has the Amazon Elastic Compute Cloud CLI tools has part of the Ubuntu distribution.

Open a terminal with <Ctrl>+<Alt>+t and run the following commands:
```sh
$ sudo apt-add-repository multiverse
$ sudo apt-get update
$ sudo apt-get install ec2-api-tools
```

### Setup your account and configuration

When you sign up for EC2, you will be given a secret key and an access key. To use the ec2-* commands below, you with either need to export them to your environment. [See the AWS help for adding the commands](http://docs.aws.amazon.com/AWSEC2/latest/CommandLineReference/set-up-ec2-cli-linux.html).

Alternatively you can use `-O <ACCESS_KEY> -W <SECRET_KEY>` for all ec2-* commands.

1. It's now time to get SSH keys setup and Google Compute Engine configured to use them. If you already have an SSH key, you can
 skip creating an SSH key. Otherwise, create an SSH key for login in:
```sh
$ ssh-keygen -t ecdsa -b 521 -f ~/.ssh/snappy-ec2
```

1. Let's pass the SSH key information to EC2. The following command will import the key in to EC2, so we can specify it
whenever we launch an instance:
```sh
$ ec2-import-keypair -f ~/.ssh/snappy-ec2.pub snappy-ec2
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
Due to the unique way that Ubuntu Core is built, only HVM instances are available. We do not foresee making paravirtual
images available as Amazon is recommending HVM instance types.

Here's how you can find the list of available snappy images on EC2:
```sh
$ ec2-describe-images \
      -o 099720109477 \
      | grep ubuntu.*stable
```

**099720109477** is the Canonical Account ID. In the coming days, we will be adding indexing to make it easier to find the latest version of Ubuntu Core.

In this example, we are going to use ami-6c0a6704 as the image name.

### First Ubuntu Core instance

 The following command will create and launch an instance.
 ```sh
 $ ec2-run-instances <IMAGE_ID> \
  --region us-east-1 --key snappy-ec2 \
	--instance-type m3.medium \
	--user-data-file cloud.cfg
```

Which will output something quite a bit of instance details. Look for INSTANCE i-XXXXX. For example:

```
RESERVATION     r-3ad841d4     <TRUNCATED...>
INSTANCE        i-cd2cb333     <TRUNCATED...>
```

The **i-cd2cb333** is the instance ID. To find out what the public address is, run (replace **i-cd2cb333** with your instance ID):

```sh
$ ec2-describe-instances i-cd2cb333 | awk '/INSTANCE/{print$4}'
```

That's it. Your instance is ready to login to now via ssh using the external IP address returned from the successful instance creation.

### Check that the instance is running

Typically you would use gcloud compute ssh <name> at this point for a regular Ubuntu instance. However, at this time,
Ubuntu Core does not have event-based user creation. So you will need to manually SSH in as the Ubuntu user:
```sh
$ ssh -i ~/.ssh/snappy-ec2 ubuntu@<EXTERNAL IP ADDRESS>
```

## First boot to Ubuntu Core 16.04

> Note that the first boot can be longer than usual as your primary disk is repartioned to take all available free space.

Power on your Amazon EC2 and wait a couple of minutes for the OS to complete its first boot.

You can then access your snappy Ubuntu Core system by loading the webdm interface from your browser. Just point it to
http://webdm.local:4200.

> Remember that if your device/cloud isn't on the same network or your vm use port redirection, adapt **webm.local** and
> the port with the appropriate external IP and ports.

![Webdm vanilla interface](https://raw.githubusercontent.com/ubuntu-core/snappy-dev-website/master/src/img/setup/webdm.png)



Congrats, you just installed your new Snappy Ubuntu Core 16.04 system. It's now time to explore it and
install some snaps to it!
