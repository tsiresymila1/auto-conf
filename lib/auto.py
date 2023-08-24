import pathlib
import os
import re


class AuthConf(object):
    def __init__(self, nginx_dir) -> None:
        self.nginx_dir = nginx_dir

    def load_project(self, directory: str, ext: str = ".local"):
        list_dir = self.scan_directory(directory)
        return self.dir_with_hostname(list_dir, ext=ext)

    def scan_directory(self,directory: str) -> list[pathlib.PosixPath]:
        dir = pathlib.Path(directory)
        list_directory = [item for item in dir.glob("*") if item.is_dir()]
        return list_directory

    def dir_with_hostname(self, directory: list[pathlib.PosixPath] = [], ext=".local"):
        hosts = [f"{d.name}{ext}" for d in directory]
        php_version = [self.load_php_version(v) for v in hosts]
        # check default root directory
        dirs = [
            f"{str(d)}/public"
            if "public" in [t.name for t in d.glob("*") if t.is_dir()]
            else f"{str(d)}"
            for d in directory
        ]
        return hosts, dirs, php_version

    def load_php_version(self, host):
        file = f"{self.nginx_dir}/sites-available/{host}.conf"
        if not os.path.isfile(file):
            file = f"{self.nginx_dir}/sites-available/auto.{host}.conf"

        if os.path.isfile(file):
            f = open(file, "r")
            content = f.read()
            f.close()
            items = re.findall("^.*unix:\/var\/run\/php\/php.*$", content, re.MULTILINE)
            php = "".join(items).strip()
            version = "".join(re.findall("\d+\.\d+", php)).strip()
            print(version)
            return version
        return ""
