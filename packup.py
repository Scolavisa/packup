#!/usr/bin/env python
import json
import pysftp
import logging
from classes.retention import Retention
from classes.backup import Backup

# read configuration
with open('./etc/backup.conf') as config_file:
    config = json.load(config_file)

# logging
# cant use logging object in the config file.
# transform loglevel in config to numeric level
numeric_level = getattr(logging, config["LOG"]["LEVEL"].upper(), None)
logging.basicConfig(
    filename=config["LOG"]["LOGFILE"],
    format='%(asctime)s %(levelname)s %(message)s',
    level=numeric_level
)


def main():
    logging.info("************************************* Start Process")

    FTPCRED = config["FTP"]
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys.load(FTPCRED["KNOWNHOSTS"])

    # Create SFTP  connection
    sftp = pysftp.Connection(
        host=FTPCRED["HOST"],
        username=FTPCRED["UN"],
        private_key=FTPCRED["PRIVKEY"],
        cnopts=cnopts
    )
    # Go to the correct directory for the duration of this connection
    sftp.cwd(FTPCRED["USEDIR"])

    Backup(sftp, logger=logging, config=config["BACKUP"])\
        .do_backup()\
        .package_backup()\
        .encrypt()\
        .send_to_backupserver()

    r = Retention(sftp, logger=logging, config=FTPCRED)
    file_list = r.read_file_list()
    r.remove_older_than(file_list, config["BACKUP"]["RETENTIONDAYS"])

    # Close SFTP  connection
    sftp.close()

    logging.info("************************************* END Process")


# Main entry point
if __name__ == '__main__': main()