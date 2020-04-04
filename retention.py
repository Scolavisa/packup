#!/usr/bin/env python
"""
Enforce retention of files on off-site backup drive
Use ./etc/backup.conf to to configure connection credentials and backup parameters
"""

import json
import pysftp
from datetime import date
import logging

# read configuration
with open('./etc/backup.conf') as config_file:
    config = json.load(config_file)

FTPCRED = config["FTP"]
cnopts = pysftp.CnOpts()
cnopts.hostkeys.load(FTPCRED["KNOWNHOSTS"])

# logging
# cant use logging object in the config file.
# transform loglevel in config to numeric level
numeric_level = getattr(logging, config["LOG"]["LEVEL"].upper(), None)
logging.basicConfig(
    filename=config["LOG"]["LOGFILE"],
    format='%(asctime)s %(levelname)s %(message)s',
    level=numeric_level
)
logging.info("************************************* Start Process")

# open sftp to backup server
with pysftp.Connection(
        host=FTPCRED["HOST"],
        username=FTPCRED["UN"],
        private_key=FTPCRED["PRIVKEY"],
        cnopts=cnopts) as sftp:
    sftp.cwd('drive')
    file_list = sftp.listdir()
    # listing
    for file_name in file_list:
        # check if file should be deleted
        # extract datepart
        file_date = file_name[7:17]
        if len(file_date) == 10:
            logging.debug("Examening {}".format(file_date))
            year = int(file_date[0:4])
            month = int(file_date[5:7])
            day = int(file_date[8:])
            diff = date.today() - date(year, month, day)
            if diff.days >= config["BACKUP"]["RETENTIONDAYS"]:
                # delete this file
                logging.info("File will be deleted: {}".format(file_name))
                #sftp.remove(file_name)
        else:
            logging.info("Can't render date of file: {}".format(file_name))

logging.info("************************************* END Process")