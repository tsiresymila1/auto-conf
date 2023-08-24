import glob
import os
import subprocess

class PHPConf(object):
    def __init__(self, socket_dir, app_dir) -> None:
        self.socket_dir = socket_dir
        self.app_dir = app_dir

    def run_shell(self, cmd: str):
        subprocess.call(cmd, shell=True)

    def extract_version(self, s: str):
        v1 = s.replace(f"{self.socket_dir}/php", "")
        return v1.replace("-fpm.sock", "")

    def clear_socket(self):
        pattern = f"{self.socket_dir}/php[0-9].[0-9]-fpm.sock"
        value = glob.glob(pattern)
        print(f"Removing socket >>> {self.socket_dir}")
        for v in value:
            print(f"Socket removed >>> {v}")
            os.unlink(v)

    def start_fpm(self,):
        self.clear_socket()
        pattern = f"{self.app_dir}/php[0-9].[0-9]"
        print(f"Loading php app >>> {pattern}")
        value = glob.glob(pattern)
        for v in value :
            print(f"Starting >>> {v.replace(f'{self.app_dir}/', '')} with config {os.path.join(v,'etc/php-fpm.conf')}")
            self.start_php_fpm(v)

    def start_php_fpm(self,path:str) :
        config_path = os.path.join(path,"etc/php-fpm.conf")
        self.run_shell(f"{path}/sbin/php-fpm --fpm-config {config_path} -D")
        

    def get_php_version(self):
        pattern = f"{self.socket_dir}/php[0-9].[0-9]-fpm.sock"
        value = glob.glob(pattern)
        return sorted([self.extract_version(p) for p in value])
