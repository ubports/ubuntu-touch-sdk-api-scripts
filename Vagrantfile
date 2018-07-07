VAGRANTFILE_API_VERSION = "2"

$script = <<SCRIPT
apt update
apt -y install python-pip bzr pandoc
cd /vagrant
pip install -r requirements.txt
python manage.py migrate
python manage.py init_apidocs
echo 'cd /vagrant' >> /home/ubuntu/.bashrc
SCRIPT

Vagrant.configure(2) do |config|
    config.vm.provider "virtualbox" do |v|
        v.memory = 1024
    end
    config.ssh.forward_agent = true

    config.vm.box = "ubuntu/xenial64"
    config.vm.network "private_network", ip: "192.168.56.35"
    config.vm.hostname = "developer-ubuntu-com"

    config.vm.provision "shell", inline: $script
end
