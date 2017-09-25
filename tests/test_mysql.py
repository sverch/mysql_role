import pytest


@pytest.fixture()
def AnsibleDefaults(Ansible):
    return Ansible("include_vars", "defaults/main.yml")["ansible_facts"]


def test_mysql_packages(Package):
    assert Package("mysql-apt-config").is_installed
    assert Package("python-mysqldb").is_installed
    assert Package("mysql-common").is_installed
    assert Package("mysql-server").is_installed


def test_mysql_service(File, Service, Socket, AnsibleDefaults):
    mysql_port = AnsibleDefaults["mysql_port"]

    assert File("/etc/init.d/mysql")
    assert Service("mysql").is_enabled
    assert Service("mysql").is_running
    assert Socket("tcp://127.0.0.1:" + str(mysql_port))


def test_mysql_database(Command):
    BD = "echo \'show databases;\'|mysql -u root -pdefault|grep -w test01"
    User = "echo \'show databases;\'|mysql -u testing -ptesting|grep -w test01"
    assert Command(BD).rc is 0
    assert Command(User).rc is 0


def test_config(Command):
    assert Command("sudo mysql --defaults-extra-file=/etc/mysql/my.cnf -sN -e \'SHOW VARIABLES WHERE variable_name=\"version_comment\"\'").stdout is "version_comment	MySQL Community Server (GPL)"
