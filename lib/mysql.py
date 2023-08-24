import glob
import os
import subprocess


class MysqlConf(object):
    def __init__(self, app_dir: str) -> None:
        self.app_dir = app_dir

    def run_shell(self, cmd: str):
        subprocess.call(cmd, shell=True)

    def mysql_version(self):
        pattern = f"{self.app_dir}/mysql-[0-9].[0-9]"
        value = glob.glob(pattern)
        return sorted([self.extract_version(p) for p in value])

    def extract_version(self, s: str):
        return s.replace(f"{self.app_dir}/mysql-", "")

    def stop(self, version):
        mysql_dir = os.path.join(self.app_dir, f"mysql-{version}")
        pid = self.get_pid(mysql_dir)
        if pid != None:
            self.run_shell(f"kill -9 {pid}")
        self.delete_socket(mysql_dir)

    def start(self, version):
        self.stop(version=version)
        mysql_dir = os.path.join(self.app_dir, f"mysql-{version}")
        binary = os.path.join(mysql_dir, "bin", "mysqld")
        config = os.path.join(mysql_dir, "conf", "my.ini")
        self.run_shell(f"{binary} --defaults-file={config} & ")

    def get_pid(self, mysql_dir) -> str | None:
        pid_path = os.path.join(mysql_dir, "run", "mysqld.pid")
        if os.path.isfile(pid_path):
            f = open(pid_path,"r")
            pid = f.read()
            f.close()
            return pid
        return None

    def delete_socket(self, mysql_dir):
        socket_path = os.path.join(mysql_dir, "run", "mysqld.sock")
        socket_lock = os.path.join(mysql_dir, "run", "mysqld.sock.lock")
        if os.path.isfile(socket_path):
            os.unlink(socket_path)
        if os.path.isfile(socket_lock):
            os.unlink(socket_lock)
