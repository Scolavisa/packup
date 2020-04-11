from datetime import date

class Retention:
    def __init__(self, ftp_connection, logger, config):
        self.ftpconn = ftp_connection
        self.logger = logger
        self.settings = config


    def remove_older_than(self, days) -> None:
        """
        Finds and deletes files older than the requested number of days
        :param days: intended retention days
        :return:
        """
        self.logger.info("Read file list")
        file_list = self.ftpconn.listdir()

        if self.settings["DRYRUN"] == "True":
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
                    self.logger.info("File will be deleted")
                    if not self.settings["DRYRUN"] == "True":
                        self.ftpconn.remove(file_name)
                else:
                    self.logger.debug("File will NOT be deleted")

            else:
                self.logger.info("Can't render date of file: {}".format(file_name))

