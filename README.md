# Packup
This project is used to create backups, encrypt the backup files package them and store them off-site through a sftp connection. 

## config
Use `etc/backup.conf` to configure. 

## deployment
use pipenv to install and pipenv run to run the script
```
pipen install
-- possibly in a cronjob
cd projectdir && pipenv run dobackup.py
```
make sure you pipenv install with the same user that will be used for the cron command.

### Copyright
(C) Scolavisa VOF 2020