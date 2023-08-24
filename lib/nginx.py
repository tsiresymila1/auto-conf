import os
import sh
import subprocess


class Nginx(object):
    def run_shell(self, cmd: str):
        subprocess.call(cmd, shell=True)

    def __init__(self, dir=os.path.join(os.getcwd(), "app", "nginx")):
        print(f"NGINX DIR :: {dir}")
        self.dir = dir

    def configure(self, hosts, dirs, default_php_version="8.2"):
        self.create_host(hosts)
        for i, h in enumerate(hosts):
            print(f"Config >>>> {h}:{dirs[i]}")
            self.create_config(dirs[i], h, default_php_version)
        self.start()

    def start(self):
        self.stop()
        print("Staring NGINX ...")
        self.run_shell(
            f"sudo {self.dir}/sbin/nginx -c {self.dir}/conf/nginx.conf -q -g  'daemon on; master_process on;'"
        )
        print("NGINX started ...")

    def reload(self):
        print("Loading NGINX ...")
        self.run_shell(
            f"sudo {self.dir}/sbin/nginx -c {self.dir}/conf/nginx.conf -q -g 'daemon on; master_process on;' -s reload"
        )
        print("NGINX loaded ...")

    def stop(self):
        self.run_shell(
            f"sudo {self.dir}/sbin/nginx -c {self.dir}/conf/nginx.conf -q -g 'daemon on; master_process on;' -s stop"
        )
        pid_file = f"{self.dir}/logs/nginx-portable.pid"
        if os.path.isfile(pid_file):
            self.run_shell(f"sudo rm -rf {pid_file}")

    def create_host(self, hostnames=[], tag="#auto-php"):
        sh.sudo.sed("-i", f"/{tag}/d", "/etc/hosts")
        hosts = [f"127.0.0.1 {h} {tag}" for h in hostnames]
        # gest host list
        for host in hosts:
            self.run_shell(f"sudo tee -a /etc/hosts > /dev/null << HOSTS \n {host}\n")
        print("HOSTS CREATED")

    def generate_config(self, default_dir, hostname, php_version):
        conf = f"""
            server {{
                listen 80;
                server_name {hostname};

                keepalive_timeout 300;
                index index.php index.html;
                error_log  {self.dir}/logs/{hostname}-error.log;
                access_log {self.dir}/logs/{hostname}-access.log;
                root {default_dir};
                location ~ \.php$ {{
                    try_files \$uri =404;
                    fastcgi_split_path_info ^(.+\.php)(/.+)\$;
                    fastcgi_pass unix:/home/tsiresy/PROJECT/PYTHON/pyterm/auto-php/run/php/php{php_version}-fpm.sock;
                    fastcgi_index index.php;
                    include fastcgi_params;
                    fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
                    fastcgi_param PATH_INFO \$fastcgi_path_info;
                }}
                location / {{
                    try_files \$uri \$uri/ /index.php?\$query_string;
                    # gzip_static on;
                }}
            }}
        """
        return conf

    def create_config(self, default_dir, hostname, php_version):
        conf = self.generate_config(default_dir, hostname, php_version)
        path_avalaible = f"{self.dir}/sites-available/{hostname}.conf"
        if not os.path.isfile(path_avalaible):
            path_avalaible = f"{self.dir}/sites-available/auto.{hostname}.conf"
            if os.path.exists(path_avalaible):
                os.unlink(path_avalaible)
            self.run_shell(f"""tee -a {path_avalaible} > /dev/null <<EOF\n{conf}""")
            print("NGINX config created !!")

        # create symbolik link
        path_enabled = f"{self.dir}/sites-enabled/{hostname}"
        if os.path.isfile(path_enabled):
            sh.unlink(path_enabled)
        sh.ln("-s", path_avalaible, path_enabled)
        print("NGINX config activated !!")

    def change_php_version(self,default_dir, hostname, php_version):
        self.create_config(default_dir, hostname, php_version)
        self.start()

