import os
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
        self.logger.info("Backups according to BU rules")
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
        line = "tar -czvf $TRANSPORTDIR/backup.tar.gz $BACKUPDIR"
        line = line.replace('$BACKUPDIR', self.settings["BACKUPDIR"])
        line = line.replace('$TRANSPORTDIR', self.settings["TRANSPORTDIR"])
        subprocess.call(line, shell=True)
        # enable chaining
        return self


    def encrypt(self):
        self.logger.info("Encrypt backup file")
        today = date.today()
        now = d1 = today.strftime("%Y-%m-%d")
        line = "openssl aes-256-cbc -pbkdf2 -pass pass:$PW -salt -in $TRANSPORTDIR/backup.tar.gz -out $TRANSPORTDIR/backup-{}.tar.gz.aes".format(now)
        line = line.replace('$BACKUPDIR', self.settings["BACKUPDIR"])
        line = line.replace('$TRANSPORTDIR', self.settings["TRANSPORTDIR"])
        line = line.replace('$PW', self.settings["ENCPW"])
        subprocess.call(line, shell=True)
        # remove unencrypted file
        os.unlink("{}/backup.tar.gz".format(self.settings["TRANSPORTDIR"]))
        # enable chaining
        return self


    def send_to_backupserver(self):
        self.logger.info("Send to backupserver")
        self.sftp.put_d(self.settings["TRANSPORTDIR"], '.')
        return self