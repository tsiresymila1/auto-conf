from fpm import get_php_version
from scanner import load_project
from nginx import boot_nginx, create_host, generate_nginx_config


def boot():
    # Auto-php default dir
    dir = "/home/tsiresy/WORK/PHP/auto-php"
    ext = ".local"

    # laod php version
    php = get_php_version()
    # get list of directory
    hosts, dirs = load_project(dir)
    create_host(hosts)
    php_default_version = "7.4"
    php_version = php_default_version if php_default_version in php else php[-1]
    for i, h in enumerate(hosts):
        generate_nginx_config(dirs[i], h, php_version)

    boot_nginx()
