import os
import logging
import json
import subprocess
import tempfile
import signal
import requests
import time

class proxy_base:

    def __init__(self, cfg, **kwargs):

        fh = open(cfg, 'r')
        data = json.load(fh)

        proxy_config = {}

        for cfg in data:
            pt = cfg['Target']
            proxy_config[pt] = cfg

        self.cfg = cfg
        self.proxy_config = proxy_config

class proxy_server(proxy_base):

    # PLEASE WRITE ME

    def start_server(self):

        """
        cmd = [ proxy_server, "-host", options.proxy_host, "-port", options.proxy_port, "-config", options.proxy_config ]
        logging.debug(cmd)

        proc = subprocess.Popen(cmd)
        """

        return False

class proxy_servers(proxy_base):

    def __init__(self, cfg, **kwargs):

        proxy_base.__init__(self, cfg, **kwargs)

        self.pid_root = kwargs.get("pid_root", tempfile.gettempdir())

    def get_pid_name(self, placetype):

        return "wof-pip-proxy-%s.pid" % placetype

    def get_pid_file(self, placetype):

        fname = self.get_pid_name(placetype)
        return os.path.join(self.pid_root, fname)

    def get_pid(self, placetype):

        pid_file = self.get_pid_file(placetype)

        if not os.path.exists(pid_file):
            return None

        pid_fh = open(pid_file, "r")

        pid = pid_fh.readline()
        pid = int(pid)

        pid_fh.close()

        return pid

    def is_server_running(self, placetype):

        pid = self.get_pid(placetype)

        if not pid:
            return False

        # ps h -p ${PID} | wc -l

        cmd = [ "ps", "h", "-p", pid ]
        cmd = map(str, cmd)

        logging.info(" ".join(cmd))

        try:
            out = subprocess.check_output(cmd)
        except Exception, e:
            logging.warning(e)
            return False

        out = out.strip()
        logging.debug(out)

        if not out.startswith(str(pid)):
            return False

        return True

    def start_server(self, placetype, **kwargs):

        pip_server = kwargs.get('pip_server', None)
        data = kwargs.get('data', None)

        if not pip_server:
            raise Exception, "Y U NO pip-server"

        if not data:
            raise Exception, "Y U NO data"

        cfg = self.proxy_config[placetype]

        pidfile = self.get_pid_file(placetype)

        cmd = [
            pip_server, "-cors",
            "-port", cfg['Port'],
            "-data", data,
            "-pidfile", pidfile,
            cfg['Meta']
        ]

        if kwargs.get('sudo', False):

            sudo = [ "sudo", "-u", kwargs["sudo"] ]
            sudo.extend(cmd)

            cmd = sudo

        cmd = map(str, cmd)
        logging.info(" ".join(cmd))

        proc = subprocess.Popen(cmd)
        pid = proc.pid

        logging.info("start %s pip server with PID %s" % (placetype, pid))

        return proc

    def stop_server(self, placetype, **kwargs):

        pid_file = self.get_pid_file(placetype)
        pid = self.get_pid(placetype)

        if kwargs.get('sudo', False):

            cmd = [ "sudo", "kill", "-HUP", str(pid) ]
            cmd = map(str, cmd)

            logging.info(" ".join(cmd))

            out = subprocess.check_output(cmd)
            logging.debug(out)

        else:
            os.kill(pid, signal.SIGKILL)

        return True

    def restart_server(self, placetype, **kwargs):

        pid_file = self.get_pid_file(placetype)
        pid = self.get_pid(placetype)

        if kwargs.get('sudo', False):

            cmd = [ "sudo", "kill", "-USR2", str(pid) ]
            cmd = map(str, cmd)

            logging.info(" ".join(cmd))

            out = subprocess.check_output(cmd)
            logging.debug(out)

        else:
            os.kill(pid, signal.SIGUSR2)

        return True

    def ping_server(self, placetype):

        cfg = self.proxy_config[placetype]
        url = "http://localhost:%s" % cfg['Port']

        # req = urllib2.Request(url)
        # req.get_method = lambda : 'HEAD'

        try:

            # urllib2.urlopen(req)
            # return True

            rsp = requests.head(url)

            if rsp.status_code == 200:
                return True

            if rsp.status_code == 400:
                return True

            logging.info("%s returned %s" % (url, rsp.status_code))
            return False

        except Exception, e:
            logging.info("failed to %s, because %s" % (url, e))
            return False

    # wait for one or more servers to respond to a ping, like on startup

    def wait_for_godot(self, placetypes=None):

        if not placetypes:
            placetypes = self.proxy_config.keys()

        while True:

            pending = False

            for pt in placetypes:

                if not self.ping_server(pt):

                    logging.info("ping for %s failed" % pt)
                    pending = True
                    break

            if not pending:
                break

            logging.info("waiting for godot...")
            time.sleep(1)
