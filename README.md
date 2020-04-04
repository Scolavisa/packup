# Packup
This project is used to create backups, encrypt the backup files package them and store them off-site through a sftp connection. 

## config
Use `etc/backup.conf` to configure. 

## deployment
use pipenv to install and pipenv run to run the script
```
# deploy / install
pipenv install

# possibly in a cronjob
1 0 * * * * cd projectdir && pipenv run packup.py
```
make sure you pipenv install with the same user that will be used for the cron command.

The programm expects a backup directory that will receive all backup files and a transport dir that wil be used to compress and encrypt all files in the backupdir. The resulting file will be transported to the backupserver (sftp). Both directories need to be defined in the configuration (./etc/backup.conf)

All backup commands are listed in ./etc/backupcommands. 