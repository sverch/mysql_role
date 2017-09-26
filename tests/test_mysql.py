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


@pytest.mark.parametrize("variable_name,expected", [
    ("version_comment", "MySQL Community Server (GPL)"),
    ("datadir", "/var/lib/mysql/"),
    ("basedir", "/usr/"),
    ("tmpdir", "/tmp"),
    ("lc_messages_dir", "/usr/share/mysql/"),
    ("socket", "/var/run/mysqld/mysqld.sock"),
    ("pid_file", "/var/run/mysqld/mysqld.pid"),
    ("port", "3306"),
    ("bind_address", "*"),
    ("general_log_file", "/var/lib/mysql/mysql.log"),
    ("general_log", "OFF"),
    ("slow_query_log", "ON"),
    ("slow_query_log_file", "/var/log/mysql/mysql-slow.log"),
    ("key_buffer_size", "256M"),
    ("max_allowed_packet", "64M"),
    ("table_open_cache", "256"),
    ("sort_buffer_size", "1M"),
    ("read_buffer_size", "1M"),
    ("read_rnd_buffer_size", "4M"),
    ("myisam_sort_buffer_size", "64M"),
    ("thread_cache_size", "8"),
    ("query_cache_size", "16M"),
    ("max_connections", "151"),
])
def test_config(Command, variable_name, expected):
    variable_query = build_show_variables_query(variable_name)
    mysql_cli_command = build_mysql_cli_command(variable_query)

    assert Command(mysql_cli_command).stdout.split("\t")[1] == expected


def build_mysql_cli_command(query):
    return "sudo mysql --defaults-extra-file=/etc/mysql/my.cnf -sN -e \'" + query + "\'"


def build_show_variables_query(variable_name):
    return "SHOW VARIABLES WHERE variable_name=\"" + variable_name + "\""
