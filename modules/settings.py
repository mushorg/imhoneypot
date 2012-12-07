import xml.dom.minidom

class SettingsParser():
    """
    
    """
    def __init__(self, logger):
        self.logger = logger
        try:
            self.xml_file = open("settings.xml")
            self.settings_file = xml.dom.minidom.parse(self.xml_file)
        except:
            self.logger.log_console("Unable to read settings.xml", "critical")

    def get_text(self, node_list):
        node_text = ""
        for node in node_list:
            if node.nodeType == node.TEXT_NODE:
                node_text += str(node.data)
        return node_text

    def parse_settings(self, section_name):
        self.section_name = section_name
        self.handle_settings_title(self.settings_file.getElementsByTagName("title")[0])
        all_sections = self.settings_file.getElementsByTagName("section")
        for section in all_sections:
            if section.attributes["name"].value == section_name:
                section = self.handle_section(section)
                return section

    def handle_settings_title(self, title):
        #print "Reading: %s, section: %s" % (self.get_text(title.childNodes),self.section_name)
        pass

    def handle_section(self, section):
        section_dict = {}
        section_dict["section"] = section.attributes["name"].value
        # Server settings handling
        if section_dict["section"] == "Server":
            pass
        # Protocol settings handling
        if section_dict["section"] == "Protocols":
            for node in section.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    protocol = str(node.nodeName)
                    section_dict[protocol] = self.handle_protocol(section.getElementsByTagName(protocol)[0])
        # Logging settings handling
        if section_dict["section"] == "Logging":
            for node in section.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    log_type = str(node.nodeName)
                    section_dict[log_type] = self.handle_log_type(section.getElementsByTagName(log_type)[0])
        # Analysis settings handling
        if section_dict["section"] == "Analysis":
            for node in section.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    analysis_type = str(node.nodeName)
                    section_dict[analysis_type] = self.handle_analysis_type(section.getElementsByTagName(analysis_type)[0])
        # Submission settings handling
        if section_dict["section"] == "Submission":
            section_dict["monkeywrench"] = self.handle_monkeywrench(section.getElementsByTagName("monkeywrench")[0])
            section_dict["anubis"] = self.handle_anubis(section.getElementsByTagName("anubis")[0])

        return section_dict

    # Server section

    # Protocols section
    def handle_protocol(self, protocol):
        if self.get_text(protocol.childNodes) == "True":
            return True
        else:
            return False

    # Logging section
    def handle_log_type(self, log_type):
        try:
            id = log_type.attributes["id"].value
            if self.get_text(log_type.childNodes) == "True" and id:
                return (id, True)
            else:
                return (id, False)
        except KeyError:
            if self.get_text(log_type.childNodes) == "True":
                return True
            else:
                return False

    # Analysis section
    def handle_analysis_type(self, analysis_type):
        if self.get_text(analysis_type.childNodes) == "True":
            return True
        else:
            return False

    # Submission section
    def handle_monkeywrench(self, monkeywrench):
        if self.get_text(monkeywrench.childNodes) == "True":
            return True
        else:
            return False

    def handle_anubis(self, anubis):
        email = anubis.attributes["email"].value
        if self.get_text(anubis.childNodes) == "True":
            return (email, True)
        else:
            return (email, False)