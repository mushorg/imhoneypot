import re
import os
import urllib2
import hashlib
import magic

import modules.submission.monkeywrench
import modules.submission.anubis
import modules.settings

class Analyser():
    """
    This class runs all the different parts which are together forming the
    whole analysis process.
    """
    def __init__(self, logger):
        self.logger = logger
        # Reads in the analysis and submission settings
        settings_parser = modules.settings.SettingsParser(self.logger)
        self.analysis_settings_list = settings_parser.parse_settings("Analysis")
        self.submission_settings_list = settings_parser.parse_settings("Submission")
        # Initialize analysis modules
        self.analyzer = AnalyseCheck(self.logger)
        self.downloader = DownloadFile(self.logger)
        # Initialize submission modules
        self.monkey_it = modules.submission.monkeywrench.MonkeyWrench(self.logger)
        self.anubis = modules.submission.anubis.Anubis(self.logger)

    def analyse_message(self, message):
        # Looks for URL's in the message
        urls = self.analyzer.check_url(message)
        # If we found at least one URL...
        if len(urls) >= 1:
            for url in urls:
                if self.submission_settings_list["monkeywrench"]:
                    # Submit URL to monkeywrench
                    self.monkey_it.submit_monkeywrench(url)
                if self.analysis_settings_list["download_file"]:
                    # Download the file the URL is pointing on 
                    file_path, exists = self.downloader.file(url)
                    if self.analysis_settings_list["executable"] and not exists:
                        # Checks if the file is a PE executable
                        if self.analyzer.check_executable(file_path):
                            if self.submission_settings_list["anubis"][1]:
                                # Submits the file to the anubis PE sandbox
                                self.anubis.submit_anubis(file_path)


class AnalyseCheck():
    """
    This class analyzes the message
    """
    def __init__(self, logger):
        self.logger = logger
        self.urls = []

    def check_url(self, message):
        try:
            # Search for URLs and returns a list
            self.urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
        except Exception:
            pass
        self.logger.log_console("We found %s URL's in this message" % len(self.urls), "debug")
        return self.urls

    def check_executable(self, file):
        # Initialize the PE test looking for "magic patterns"
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        ftype =  ms.file(file)
        ms.close()
        self.logger.log_console("Filetype: %s" % ftype, "debug")
        if ftype == "PE32 executable for MS Windows (GUI) Intel 80386 32-bit":
            return True
        else:
            False


class DownloadFile():
    """
    This class handles everything related to downloading a file and saving
    it to the file system.
    """
    def __init__(self, logger):
        self.logger = logger

    def file(self, url):
        temp_file = self.openurl(url)
        file_path, exists = self.save_file(temp_file)
        return (file_path, exists)

    def openurl(self, url):
        """
        Opens a URL with modified exception handler and returns the
        file handler.
        """
        try:
            # Tries to get the file
            req = urllib2.Request(url)
            file_object = urllib2.urlopen(req)
        except IOError, e:
            if hasattr(e, "reason"):
                self.logger.log_console("Reason: %s" % e.reason, "critical")
            elif hasattr(e, "code"):
                self.logger.log_console("Error code: %s" % e.code, "critical")
        return file_object

    def save_file(self, file_object):
        """
        Computes a md5 hash from the file and if it's new, saves it to
        the file system. Returns the path to the file and a boolean if the
        file was new.
        """
        exists = False
        # Computing the md5 hash
        try:
            file = file_object.read()
            filename = hashlib.md5(file).hexdigest()
        except:
            self.logger.log_console("There was an error computing the md5 hash", "critical")
            return
        else:
            file_path = "files/" + filename
        # Check if file already exists
        if os.path.exists(file_path):
            self.logger.log_console("File: %s already exists" % filename, "debug")
            exists = True
        else:
            # Try to save the file to the file system
            try:
                new_file = open(file_path, 'wb')
                new_file.write(file)
                new_file.close()
                self.logger.log_console("New file stored: %s" % filename, "debug")
            except:
                self.logger.log_console("Error: writing file %s to disk" % filename, "critical")
        return (file_path, exists)