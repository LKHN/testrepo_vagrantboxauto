import pytest
import testinfra


# vagrant user and group are present
def test_vagrant_user_present(host):
    assert host.user("vagrant").exists
    assert host.group("vagrant").exists
    assert host.user("vagrant").uid == 1000
    assert host.user("vagrant").gid == 1000


# sudoers file created correctly
def test_sudoers_file_present(host):
    with host.sudo():
        sudoers_file = host.file("/etc/sudoers.d/vagrant")
        sudoers_file.contains("vagrant     ALL=(ALL)     NOPASSWD: ALL")


# guest additions/tools/agents/kernel modules are installed
def test_guest_tools_is_installed(host):
    kvm_tools = ['qemu-guest-agent', 'rsync', 'nfs-utils']
    hypervisor = host.check_output("systemd-detect-virt")
    if hypervisor == "kvm":
        for package in kvm_tools:
            assert host.package(package).is_installed
    elif hypervisor == "oracle":
        vb_guest_cmd = host.run("lsmod | grep vboxguest")
        assert vb_guest_cmd.succeeded == True
        assert host.package("nfs-utils").is_installed
    elif hypervisor == "vmware":
        assert host.package("open-vm-tools").is_installed
        assert host.package("nfs-utils").is_installed
    else:
        raise NotImplementedError(f'unsupported hypervisor {hypervisor}')


# guest additions/tools/agents services running and enabled
def test_guest_tools_is_running(host):
    hypervisor = host.check_output("systemd-detect-virt")
    if hypervisor == "kvm":
        assert host.service("qemu-guest-agent.service").is_running
    elif hypervisor == "oracle":
        assert host.service("vboxadd-service.service").is_running
    elif hypervisor == "vmware":
        assert host.service("vmtoolsd.service").is_running
    else:
        raise NotImplementedError(f'unsupported hypervisor {hypervisor}')


# no public SSH keys except the Vagrant’s one are present
def test_insecure_vagrant_ssh_pub_key(host):
    authorized_keys = host.file("/home/vagrant/.ssh/authorized_keys").content_string
    if len(authorized_keys.splitlines()) == 1:
        # SHA256 checksum of "$vagrant_insecure_pub_key vagrant"
        assert host.file(
            "/home/vagrant/.ssh/authorized_keys").sha256sum == "9aa9292172c915821e29bcbf5ff42d4940f59d6a148153c76ad638f5f4c6cd8b"
    else:
        raise NotImplementedError(f'vagrant public key is not lonely')


# check shared folders are working
def test_shared_folder_is_working(host):
    assert host.mount_point("/vagrant").exists
    assert host.file("/vagrant/Vagrantfile").exists


# installer logs and kickstart files are removed
def test_installer_leftovers(host):
    assert host.file("/root/anaconda-ks.cfg").exists == False
    assert host.file("/root/original-ks.cfg").exists == False
    assert host.file("/var/log/anaconda").exists == False
    assert host.file("/root/install.log").exists == False
    assert host.file("/root/install.log.syslog").exists == False


# Check Network stack working properly
def test_network_is_working(host):
    almalinux = host.addr("almalinux.org")
    assert almalinux.is_resolvable
    assert almalinux.port(443).is_reachable

# TODO 1: SSH host key is unique for every new launched VM
# TODO 2: /etc/machine-id is unique for every new launched VM
