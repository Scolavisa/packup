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
# Can't use logging object in the config file.
# So we need to transform loglevel in config to numeric level
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

    # Backup section
    Backup(sftp, logger=logging, config=config["BACKUP"])\
        .do_backup()\
        .package_backup()\
        .encrypt()\
        .send_to_backupserver()

    # Retention section
    if config["BACKUP"]["RETENTIONSCHEME"] == 'NONE':
        logging.info("Skipping retention, no scheme defined in config")
    else :
        if config["BACKUP"]["RETENTIONSCHEME"] == "OLDERTHANNROFDAYS" and \
                config["BACKUP"]["RETENTIONDAYS"] is not None:
            Retention(sftp, logger=logging, config=FTPCRED)\
                .remove_older_than(config["BACKUP"]["RETENTIONDAYS"])

        # elif: (todo next scheme)

        # elif: (todo next scheme)

    # Close SFTP  connection
    sftp.close()

    logging.info("************************************* END Process")


# Main entry point
if __name__ == '__main__': main()