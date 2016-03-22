#
#  * IMHoneypot - An Instant Messenger Honeypot *
#
#  Copyright (c) 2010 Lukas Rist
#
#
#  This program is free software; you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation; either version 3 of the License, or (at your option) any later
#  version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, see <http://www.gnu.org/licenses/>.

import purple
import time

import modules.callbacks
import modules.accounts
import modules.settings
import modules.logger
import modules.sqlite


class IMHoneypot():
    """
    Main instant messenger honeypot class. This represents the honeypot
    core which is responsible for module initializing.
    """

    def __init__(self):
        """Initializing the purple core"""
        # Initialize the logger
        self.logger = modules.logger.LogThis()
        self.logger.log_file("Starting IMHoneypot...", "debug")
        self.logger.log_console("Starting IMHoneypot...", "debug")
        # Initialize databases
        self.sqlite_db = modules.sqlite.SQLiteDB(self.logger)
        self.sqlite_db.create()
        # Get server settings
        self.settings_parser = modules.settings.SettingsParser(self.logger)
        server_settings_list = self.settings_parser.parse_settings("Server")
        # The information below is needed by libpurple
        name = "nullclient"
        version = "0.1"
        website = "N/A"
        dev_website = "N/A"
        # Sets initial parameters
        self.core = purple.Purple(name, version, website, dev_website, debug_enabled=True, default_path="prefs")
        # Initializes libpurple
        self.core.purple_init()

    def add_callbacks(self):
        """Adds all the callbacks to the purple core instanze"""
        # Initialize callbacks
        account_callbacks = modules.callbacks.AccountCallbacks(self.logger, self.active_accounts)
        blist_callbacks = modules.callbacks.BlistCallbacks(self.logger)
        conversation_callbacks = modules.callbacks.ConversationCallbacks(self.logger, self.active_accounts)
        # Add account callbacks
        self.core.add_callback('account', 'request-authorize', account_callbacks.account_request_authorization_cb)
        self.core.add_callback('account', 'request-add', account_callbacks.account_request_add_cb)
        self.core.add_callback('account', 'notify-added', account_callbacks.account_notify_added_cb)
        # Add buddy list callbacks
        self.core.add_callback('blist', 'request-add-buddy', blist_callbacks.blist_request_add_buddy_cb)
        # Add conversation callbacks
        self.core.add_callback('conversation', 'create-conversation', conversation_callbacks.create_conv_cb)
        self.core.add_callback('conversation', 'write-im', conversation_callbacks.write_im_cb)
        self.core.add_callback('conversation', 'write-conv', conversation_callbacks.write_conv_cb)
    
    def connect_signals(self):
        # Initialize signal callbacks
        signal_callbacks = modules.callbacks.SignalCallbacks(self.logger)
        # Connect signals to the core
        self.core.signal_connect('signed-on', signal_callbacks.signal_signed_on_cb)
        self.core.signal_connect('signed-of', signal_callbacks.signal_signed_of_cb)
        self.core.signal_connect('connection-error', signal_callbacks.signal_connection_error_cb)
        
    def init_accounts(self):
        """Initializing the accounts"""
        # Get the protocol settings
        protocol_settings_list = self.settings_parser.parse_settings("Protocols")
        # Initialize the account parser
        account_parser = modules.accounts.AccountParser(self.logger)
        account_list = account_parser.parse_accounts()
        self.active_accounts = {}
        for account in account_list:
            if account["protocol"] in protocol_settings_list.keys() and protocol_settings_list[account["protocol"]]:
                self.logger.log_console("Initializing: "+ str(account["name"]), "debug")

                # Get username from user
                username = account["user_name"]
                # Initialize protocol class
                protocol = purple.Protocol(account["protocol"])

                # Creates new account inside libpurple
                initialized_account = purple.Account(username, protocol, self.core)
                initialized_account.new()

                # Get password from user
                initialized_account.set_password(account["password"])

                # Set account protocol options
                account_info = {}
                account_info['connect_server'] = account["connect_server"]
                account_info['port'] = account["server_port"]
                account_info['ssl'] = account["ssl"]
                account_info['old_ssl'] = account["old_ssl"]
                initialized_account.set_protocol_options(account_info)

                # Enable account (connects automatically)
                if initialized_account.set_enabled(True):
                    self.active_accounts[account["protocol"]] = initialized_account
                else:
                    self.logger.log_console("Error enabling account: %s" % account["protocol"], "debug")


    def run(self):
        """The honeypot main loop"""
        # Loop the core
        while True:
            try:
                # Iterate the loop
                self.core.iterate_main_loop()
                # Give him some time
                time.sleep(0.01)
            # Ctrl + c stops the honeypot
            except KeyboardInterrupt():
                self.logger.log_console("^C received, shutting down imhoneypot", "debug")
                # Destroy the purple core
                self.core.destroy()
                # Breaks the loop
                break

if __name__ == "__main__":
    """
    Runs the IMHoneypot
    """

    # Initialize the honeypot instance and core
    honeypot = IMHoneypot()
    # Initialize accounts
    honeypot.init_accounts()
    # Add callbacks
    honeypot.add_callbacks()
    # Connect signals
    honeypot.connect_signals()
    # Run the Honeypot
    honeypot.run()
