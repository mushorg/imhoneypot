import xml.dom.minidom

class AccountParser():
    """
    This module reads the accounts.xml file and parses the different Account
    settings. It returns a dictionary containing the different accounts.
    """
    def __init__(self, logger):
        # Initializes the logger
        self.logger = logger
        # Reads the accounts.xml file
        try:
            self.xml_file = open("accounts.xml")
            # Parse the xml file
            self.accounts_file = xml.dom.minidom.parse(self.xml_file)
        except:
            self.logger.log_console("Unable to read accounts.xml", "critical")

    def get_text(self, node_list):
        # Returns the textual content from a node
        node_text = ""
        for node in node_list:
            if node.nodeType == node.TEXT_NODE:
                node_text += node.data
        return node_text

    def parse_accounts(self):
        # Returns a list holding the not yet parse accounts
        self.handle_accounts_title(self.accounts_file.getElementsByTagName("title")[0])
        all_accounts = self.accounts_file.getElementsByTagName("account")
        account_list = self.handle_accounts(all_accounts)
        return account_list

    def handle_accounts_title(self, title):
        # Handles the file title
        self.logger.log_console("Loading: %s" % self.get_text(title.childNodes), "debug")

    def handle_accounts(self, all_accounts):
        # Handles the account list
        accounts = []
        for account in all_accounts:
            account = self.handle_account(account)
            accounts.append(account)
        return accounts

    def handle_account(self, account):
        """
        Creates the dictionary holding the different accounts. This gets
        returned to the honeypot core.
        """
        account_dict = {}
        account_dict["name"] = self.handle_account_name(account.getElementsByTagName("name")[0])
        account_dict["protocol"] = self.handle_account_protocol(account.getElementsByTagName("protocol")[0])
        account_dict["user_name"] = self.handle_account_user_name(account.getElementsByTagName("user_name")[0])
        account_dict["password"] = self.handle_account_password(account.getElementsByTagName("password")[0])
        account_dict["connect_server"] = self.handle_account_connect_server(account.getElementsByTagName("connect_server")[0])
        account_dict["server_port"] = self.handle_account_server_port(account.getElementsByTagName("server_port")[0])
        account_dict["ssl"] = self.handle_account_ssl(account.getElementsByTagName("ssl")[0])
        account_dict["old_ssl"] = self.handle_account_old_ssl(account.getElementsByTagName("old_ssl")[0])
        return account_dict

    def handle_account_name(self, account_name):
        return self.get_text(account_name.childNodes)

    def handle_account_protocol(self, account_protocol):
        return self.get_text(account_protocol.childNodes)

    def handle_account_user_name(self, account_user_name):
        return self.get_text(account_user_name.childNodes)

    def handle_account_password(self, account_password):
        return self.get_text(account_password.childNodes)

    def handle_account_connect_server(self, account_connect_server):
        return self.get_text(account_connect_server.childNodes)

    def handle_account_server_port(self, account_server_port):
        return self.get_text(account_server_port.childNodes)

    def handle_account_ssl(self, account_ssl):
        return self.get_text(account_ssl.childNodes)

    def handle_account_old_ssl(self, account_old_ssl):
        return self.get_text(account_old_ssl.childNodes)