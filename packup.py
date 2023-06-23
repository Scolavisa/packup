#!/usr/bin/env python
import json
import logging
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

    # Backup section
    Backup(logger=logging, config=config)\
        .do_backup()\
        .package_backup()\
        .encrypt()\
        .split()\
        .send_to_backupserver()

    logging.info("************************************* END Process")

# Main entry point
if __name__ == '__main__': main()