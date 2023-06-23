import os
import socket
import subprocess
import pysftp
from classes.retention import Retention
from datetime import date

class Backup:
    def __init__(self, logger, config):
        self.logger = logger
        self.backupsettings = config["BACKUP"]
        self.sftpsettings = config["FTP"]
        self.config = config

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
                line = line.replace('$BACKUPDIR', self.backupsettings["BACKUPDIR"])
                line = line.replace('$TRANSPORTDIR', self.backupsettings["TRANSPORTDIR"])
                self.logger.info("Executing: {}....".format(line[0:15]))
                self.logger.debug("Executing: {}".format(line))
                subprocess.call(line, shell=True)
        # enable chaining
        return self

    # package all backup files into one tar.gz file, ready to be encrypted and then chunked
    def package_backup(self):
        self.logger.info("Package backups into one file")
        hostname = socket.gethostname()
        line = "tar -czvf {transpdir}/{hostname}.backup.tar.gz {backupdir}".format(
            transpdir=self.backupsettings["TRANSPORTDIR"],
            hostname=hostname,
            backupdir=self.backupsettings["BACKUPDIR"]
        )
        subprocess.call(line, shell=True)
        # enable chaining
        return self

    # encrypt the backup file using the configured encryption password
    def encrypt(self):
        self.logger.info("Encrypt backup file")
        today = date.today()
        now = d1 = today.strftime("%Y-%m-%d")
        hostname = socket.gethostname()
        line = "openssl aes-256-cbc -pbkdf2 -pass pass:{pw} -salt -in {transpdir}/{hostname}.backup.tar.gz -out {transpdir}/backup-{now}{hostname}.tar.gz.aes".format(
            pw=self.backupsettings["ENCPW"],
            transpdir=self.backupsettings["TRANSPORTDIR"],
            now=now,
            hostname = hostname,
        )
        subprocess.call(line, shell=True)
        # remove unencrypted file
        os.unlink("{transpdir}/{hostname}.backup.tar.gz".format(transpdir=self.backupsettings["TRANSPORTDIR"], hostname=hostname))
        # enable chaining
        return self

    # split resulting backup file into chunks
    def split(self):
        self.logger.info("Split backup file into chunks")
        today = date.today()
        now = d1 = today.strftime("%Y-%m-%d")
        hostname = socket.gethostname()
        line = "split -b {chunksize} {transpdir}/backup-{now}{hostname}.tar.gz.aes {transpdir}/backup-{now}{hostname}.tar.gz.aes.chunk".format(
            chunksize=self.backupsettings["CHUNKSIZE"],
            transpdir=self.backupsettings["TRANSPORTDIR"],
            now=now,
            hostname=hostname,
        )
        subprocess.call(line, shell=True)
        # remove input file
        os.unlink("{transpdir}/backup-{now}{hostname}.tar.gz.aes".format(transpdir=self.backupsettings["TRANSPORTDIR"], now=now, hostname=hostname))
        # enable chaining
        return self

    # send all chunks to the backup server
    def send_to_backupserver(self):
        self.logger.info("Send to backupserver")
        self.connect()
        self.sftp.put_d(self.backupsettings["TRANSPORTDIR"], '.')
        Retention(self.sftp, logger=self.logger, config=self.config).doRetentionScheme()
        self.disconnect()
        return self

    # connect to the backup server
    def connect(self):
        # todo: check if all config values are set for both connection methods (PW or private key)
        self.logger.info("Connect to backupserver")
        # if we have a PW we use that to connect, otherwise we need a private key
        if self.sftpsettings["PW"] is None:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys.load(self.sftpsettings["KNOWNHOSTS"])

            # Create SFTP  connection
            self.sftp = pysftp.Connection(
                host=self.sftpsettings["HOST"],
                username=self.sftpsettings["UN"],
                private_key=self.sftpsettings["PRIVKEY"],
                cnopts=cnopts
            )
        else:
            self.sftp = pysftp.Connection(
                host=self.sftpsettings["HOST"],
                username=self.sftpsettings["UN"],
                password=self.sftpsettings["PW"],
            )

        # Go to the correct directory for the duration of this connection
        self.logger.debug("Change to directory on backup server: {}".format(self.sftpsettings["USEDIR"]))
        self.sftp.cwd(self.sftpsettings["USEDIR"])
        return self

    # disconnect from the backup server
    def disconnect(self):
        self.logger.info("Disconnect from backupserver")
        self.sftp.close()
        return self