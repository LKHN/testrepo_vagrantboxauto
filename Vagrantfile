# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "almalinux-8-test"
  #config.vm.define "al8-test-a"
  config.vm.hostname = "al8-test-a"
  config.ssh.insert_key = false

  config.vm.provision "shell",
    inline: "cp /etc/machine-id /vagrant/machine-id-$HOSTNAME"

  config.vm.provider "libvirt" do |v, override|
     override.vm.synced_folder ".", "/vagrant",
      type: "nfs",
      nfs_version: 4,
      nfs_udp: false

    v.qemu_use_session = false
    #v.default_prefix = ""
    v.channel :type => 'unix', :target_name => 'org.qemu.guest_agent.0', :target_type => 'virtio'
    v.memory = 2048
    v.cpus = 2
  end
  config.vm.provider "virtualbox" do |v, override|
  end
  config.vm.provider "vmware_desktop" do |v, override|
  end
end
