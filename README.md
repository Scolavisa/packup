# Packup
This project is used to create backups of databases and files, package them, encrypt the result and store it off-site through an sftp connection

## Requirements
The script is meant to be run on a server that has Python3 installed. To install and run the script we use pipenv. Please consult your taste of server to meet these requirements. You need enough diskspace on your server for the intermediate files. Lastly you need a backup server accessible by the production server through sftp. The script uses public/private key negotiation for access to the backupserver.


## Configuration / etc directory
### setup
Use `etc/backup.conf` to configure. The etc directory contains an example of the configuration called `backup.example.conf`. Copy this file. Then fill it with the necessary values.
Most importantly: your config needs to have a BACKUPDIR and a TRANSPORTDIR. 
- BACKUPDIR: this directory will contain your intermediate files, usu. packages of your backups. They are the result of your backupcommands (see below)
- TRANSPORTDIR: this directory will be used to assemle everything in BACKUPDIR, encrypt it and send it to the backupserver.

Both should be readable/writable by the script user (cron user) but not by the world.

The backup will be chunked into separate files, you need to add CHUCKSIZE config parameter to your config. There is no default.

### sftp keys
the script uses sftp to transport the files to your backup server. If you get an error `No hostkey for host ***** found` you can fix this by using sftp in your terminal to access the backup server. 
```bash
$ sftp user@backupserver
The authenticity of host '.... (....ip....)' can't be established.
RSA key fingerprint is SHA256:...j38Z3I9c.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '....., ip' (RSA) to the list of known hosts.
Welcome to the STACK SFTP server
......'s password: 
Connected to .....
sftp> exit
```
This will save the hostkey, the error should be gone after that. 
When using a key to access the backup server, you will also need the webservers public key in the .ssh directory of the backup server. 

If you want to use priv/public key connection, you should leave out a pw entry in the backup.conf, and instead add a privkey entry and a path to the knownhosts file. 
To Use UN/PW, simply add those credentials in the conf file, any key entries will be ignored. 

### backup steps
The file `etc/backupcommands.conf` should contain all steps your backup needs to do, as if you were typing them in on the commandline. They might look like this: 
```commandline
mysqldump mydbname --single-transaction --add-drop-table > $BACKUPDIR/mydbname.sql
```
Make sure you define the directories in your backup.conf.
    
## Deployment
Use pipenv to install and `pipenv run` to run the script
```
# deploy / install
pipenv install

# possibly in a cronjob, runs every day at one o'clock.
1 0 * * * cd /your/packup/projectdir && pipenv run python packup.py
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
