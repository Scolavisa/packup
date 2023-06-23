from datetime import date

class Retention:
    def __init__(self, sftp_connection, logger, config):
        self.sftpconn = sftp_connection
        self.logger = logger
        self.sftpsettings = config["FTP"]
        self.backupsettings = config["BACKUP"]

    # execute retention scheme as configured in config file
    def doRetentionScheme(self) -> None:
        # check if we need to delete remote files due to retention
        if self.backupsettings["RETENTIONSCHEME"] == 'NONE':
            self.logger.info("Skipping retention, no scheme defined in config")
        else:
            if self.backupsettings["RETENTIONSCHEME"] == "OLDERTHANNROFDAYS" and \
                    self.backupsettings["RETENTIONDAYS"] is not None:
                        self.remove_older_than(self.backupsettings["RETENTIONDAYS"])

            # todo implement other retention schemes
            # elif self.backupsettings["RETENTIONSCHEME"] == "LASTNBACKUPS" and \
            #        self.backupsettings["RETENTIONBACKUPS"] is not None:
            #            self.remove_last_n_backups(self.backupsettings["RETENTIONBACKUPS"])
            else:
                self.logger.info("Retention scheme {} not implemented".format(self.backupsettings["RETENTIONSCHEME"]))

    def remove_older_than(self, days) -> None:
        """
        Finds and deletes files older than the requested number of days
        :param days: intended retention days
        :return:
        """
        self.logger.info("*** Retention scheme: remove older than {} days".format(days))
        self.logger.info("Read file list")
        file_list = self.sftpconn.listdir()

        if self.sftpsettings["DRYRUN"] == "True":
            self.logger.info("Dryrun set to true, not deleting indicated files")

        self.logger.info("Found {} files in the current server directory".format(len(file_list)))

        for file_name in file_list:
            # check if file should be deleted
            # extract datepart
            file_date = file_name[7:17]
            if len(file_date) == 10:
                self.logger.debug("Examening {}".format(file_date))
                year = int(file_date[0:4])
                month = int(file_date[5:7])
                day = int(file_date[8:])
                diff = date.today() - date(year, month, day)
                if diff.days >= days:
                    # delete this file
                    self.logger.info("File {} will be deleted".format(file_name))
                    if not self.sftpsettings["DRYRUN"] == "True":
                        self.sftpconn.remove(file_name)
                else:
                    self.logger.debug("File will NOT be deleted")

            else:
                self.logger.info("Can't render date of file: {}".format(file_name))

