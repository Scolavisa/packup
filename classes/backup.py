import os
import socket
import subprocess
from datetime import date


class Backup:
    def __init__(self, sftp_connection, logger, config):
        self.logger = logger
        self.settings = config
        self.sftp = sftp_connection

    def do_backup(self):
        """
        read backup rules and execute them
        creates seperate files as tar.gz for every backup rule
        :return:
        """
        self.logger.info("Backups according to backup commands in /etc/backupcommands.conf")
        command_file = open('./etc/backupcommands.conf', 'r')
        for command in command_file:
            line = command.strip()
            if not(line[0:1] == "#") and len(line) > 3:
                line = line.replace('$BACKUPDIR', self.settings["BACKUPDIR"])
                line = line.replace('$TRANSPORTDIR', self.settings["TRANSPORTDIR"])
                self.logger.info("Executing: {}....".format(line[0:15]))
                self.logger.debug("Executing: {}".format(line))
                subprocess.call(line, shell=True)
        # enable chaining
        return self

    def package_backup(self):
        self.logger.info("Package backups into one file")
        hostname = socket.gethostname()
        line = "tar -czvf {transpdir}/{hostname}.backup.tar.gz {backupdir}".format(
            transpdir=self.settings["TRANSPORTDIR"],
            hostname=hostname,
            backupdir=self.settings["BACKUPDIR"]
        )
        subprocess.call(line, shell=True)
        # enable chaining
        return self

    def encrypt(self):
        self.logger.info("Encrypt backup file")
        today = date.today()
        now = d1 = today.strftime("%Y-%m-%d")
        hostname = socket.gethostname()
        line = "openssl aes-256-cbc -pbkdf2 -pass pass:{pw} -salt -in {transpdir}/{hostname}.backup.tar.gz -out {transpdir}/backup-{now}{hostname}.tar.gz.aes".format(
            pw=self.settings["ENCPW"],
            transpdir=self.settings["TRANSPORTDIR"],
            now=now,
            hostname = hostname,
        )
        subprocess.call(line, shell=True)
        # remove unencrypted file
        os.unlink("{transpdir}/{hostname}.backup.tar.gz".format(transpdir=self.settings["TRANSPORTDIR"], hostname=hostname))
        # enable chaining
        return self

    def send_to_backupserver(self):
        self.logger.info("Send to backupserver")
        self.sftp.put_d(self.settings["TRANSPORTDIR"], '.')
        return self
