import purple

import time

import modules.analysis
import modules.sqlite
import modules.settings


class SignalCallbacks():
    """
    This class holds the callbacks for signals.
    """
    def __init__(self, logger):
        self.logger = logger

    def signal_signed_on_cb(self, username, protocol_id):
        self.logger.log_console("Signed on: %s (%s)" % (username, protocol_id), "debug")

    def signal_signed_of_cb(self, username, protocol_id):
        self.logger.log_console("Signed of: %s (%s)" % (username, protocol_id), "debug")

    def signal_connection_error_cb(self, username, protocol_id, short_desc, desc):
        self.logger.log_console("Connection error: (%s) %s" % (short_desc, desc), "debug")


class AccountCallbacks():
    """
    Class for account related callbacks
    """
    def __init__(self, logger, active_accounts):
        self.logger = logger
        self.active_accounts = active_accounts
        # Get settings
        settings_parser = modules.settings.SettingsParser(self.logger)
        self.logging_settings_list = settings_parser.parse_settings("Logging")
        self.analysis_settings_list = settings_parser.parse_settings("Analysis")
        self.analyzer = modules.analysis.Analyser()
        # Initialize database modules
        self.sqlite_db = modules.sqlite.SQLiteDB()

    def account_request_authorization_cb(self, remote_user, account, message, on_list, call_authorize_cb, call_deny_cb):
        """
        This will present a dialog informing the user of this and ask if the user authorizes or denies the remote user from adding him.

        @param: account The account that was added
        @param: remote_user The name of the user that added this account.
        @param: id The optional ID of the local account. Rarely used.
        @param: alias The optional alias of the remote user.
        @param: message The optional message sent by the user wanting to add you.
        @param: on_list Is the remote user already on the buddy list?
        @param: auth_cb The callback called when the local user accepts
        @param: deny_cb The callback called when the local user rejects
        @param: user_data Data to be passed back to the above callbacks

        @return: A UI-specific handle.
        """
        # Print some info
        self.logger.log_console("account_authorization_request from %s for account %s protocol %s with message: %s" % (remote_user[0], account[0], account[1], message), "debug")
        # Authorize him to add us
        call_authorize_cb()
        #remote_user_info = remote_user.user_info
        if self.analysis_settings_list["url"]:
            # Check message for URLs
            self.analyzer.analyse_message(message)
            #self.analyzer.analyse_message(remote_user_info)
        if self.logging_settings_list["sqlite"] == True:
            attack_time = time.strftime("%Y-%m-%d %X")
            self.sqlite_db.insert(attack_time, remote_user[0], message)

    def account_request_add_cb(account, remote_user, id, alias, message):
        """
        Notifies the user that the account was addded to a remote user's buddy
        list and asks ther user if they want to add the remote user to their
        buddy list.

        This will present a dialog informing the local user that the remote
        user added them to the remote user's buddy list and will ask if they
        want to add the remote user to the buddy list.

        @param account: The account that was added.
        @param remote_user: The name of the user that added this account.
        @param id: The optional ID of the local account. Rarely used.
        @param alias: The optional alias of the user.
        @param message: The optional message sent from the user adding you.
        """
        self.logger.log_console("%s added %s to his contact list with message: %s." % (remote_user[0], account[0], message), "debug")
        #self.active_accounts[account[1]].request_add_buddy(remote_user[0], remote_user[1])

    def account_notify_added_cb(account, remote_user, id, alias, message):
        """
        Notifies the user that the account was added to a remote user's
        buddy list.

        This will present a dialog informing the user that he was added
        to the remote user's buddy list.

        @param account: The account that was added.
        @param remote_user: The name of the user that added this account.
        @param id: The optional ID of the local account. Rarely used.
        @param alias: The optional alias of the user.
        @param message: The optional message sent from the user adding you.
        """
        self.logger.log_console("%s added %s to his contact list with message: %s." % (remote_user[0], account[0], message), "debug")

class BlistCallbacks():
    """
    Buddy list related callbacks
    """
    def __init__(self, logger):
        self.logger = logger

    def blist_request_add_buddy_cb(account, username, group, alias):
        """
        Requests from the user information needed to add a buddy to the buddy list.

        Parameters:
        account     The account the buddy is added to.
        username     The username of the buddy.
        group     The name of the group to place the buddy in.
        alias     The optional alias for the buddy.
        """
        self.logger.log_console("Requests from the user information needed to add a buddy to the buddy list", "debug")


class ConversationCallbacks():
    """
    Class for conversation callbacks.
    """
    def __init__(self, logger, active_accounts):
        self.logger = logger
        # Get settings
        settings_parser = modules.settings.SettingsParser(self.logger)
        self.logging_settings_list = settings_parser.parse_settings("Logging")
        self.analysis_settings_list = settings_parser.parse_settings("Analysis")
        self.analyzer = modules.analysis.Analyser(self.logger)
        # Initialize database modules
        self.sqlite_db = modules.sqlite.SQLiteDB(self.logger)
        self.active_accounts = active_accounts

    def create_conv_cb(self, name, type):
        """
        @param type: The type of conversation.
        @param name: The name of the conversation.
        """
        self.logger.log_console("New conversation from %s, type: %s" % (name, type), "debug")

    def write_im_cb(self, username, name, alias, message, flags):
        if message:
            # Remove html markup from message
            stripped = purple.markup_strip_html(message)
        else:
            stripped = "Empty message"
        if self.analysis_settings_list["url"]:
            # Check message for URLs and further analysis steps
            self.analyzer.analyse_message(stripped)
        if flags == 'SEND':
            sender = username
            self.logger.log_console(flags + ": " + sender + ": " + stripped, "debug")
        elif alias:
            sender = alias
        else:
            sender = name
        if flags == 'RECV':
            # Log to console and logfile
            self.logger.log_both(flags + ": " + name + ": " + stripped, "critical")
            # Log to instant messenger
            if self.logging_settings_list["icq"][1]:
                try:
                    icq = self.active_accounts["prpl-icq"]
                except KeyError:
                    self.logger.log_console("No icq account active for IM logging!", "warning")
                else:
                    username = icq.username
                    id = self.logging_settings_list["icq"][0]
                    message = "IMHoneypot - From: <FONT COLOR='#ff0000'>" + name + "</FONT> Message: <FONT COLOR='#ff0000'>" + stripped + "</FONT>"
                    self.send_message(id, message)
        # Log to sqlite database if enabled
        if self.logging_settings_list["sqlite"] == True:
            attack_time = time.strftime("%Y-%m-%d %X")
            self.sqlite_db.insert(attack_time, sender, stripped)

    def send_message(self, name, message):
        self.conversations = {}
        if name not in self.conversations:
            self.conversations[name] = purple.Conversation('IM', self.active_accounts["prpl-icq"], name)
            self.conversations[name].new()

        self.conversations[name].im_send(message)
        self.conversations[name].destroy()
        if name in self.conversations:
            del self.conversations[name]

    def write_conv_cb(self, name, sender_alias, message, flag):
        print name, sender_alias, message, flag