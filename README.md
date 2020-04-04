# Packup
This project is used to create backups, encrypt the backup files package them and store them off-site through a sftp connection. 

## config
Use `etc/backup.conf` to configure. 

## deployment
Use pipenv to install and `pipenv run` to run the script
```
# deploy / install
pipenv install

# possibly in a cronjob
1 0 * * * * cd projectdir && pipenv run packup.py
```
Make sure you pipenv install with the same user that will be used for the cron command.

The programm expects a backup directory that will receive all backup files and a transport dir that wil be used to compress and encrypt all files in the backupdir. The resulting file will be transported to the backupserver (sftp). Both directories need to be defined in the configuration (./etc/backup.conf)

All backup commands are listed in ./etc/backupcommands. 

## Tips
Don't use passwords in the commandline. For Mysql: use the .my.cnf file to grand your user access.

Create file ~/.my.cnf and add following lines in it and replace mysqluser & mysqlpass values.
```
[client]
user=mysqluser
password=mysqlpass
```
For safety, make this file readable to you only by running chmod 0600 ~/.my.cnf. Don't provide -u and -p in a mysqldump command.   