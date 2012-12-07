import itertools
import mimetools
import mimetypes
import urllib2
import sys
import base64
import hashlib

import modules.settings

# Thanks to http://blog.doughellmann.com/2009/07/pymotw-urllib2-library-for-opening-urls.html

class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        fileHandle.close()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return

    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        parts = []
        part_boundary = '--' + self.boundary

        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


class Anubis():
    """
    Submits the file to the Anubis PE sandbox.
    """
    def __init__(self, logger):
        self.logger = logger
        # Initialize the settiings 
        settings_parser = modules.settings.SettingsParser(self.logger)
        self.submission_settings_list = settings_parser.parse_settings("Submission")

    def submit_anubis(self, file):
        # The sandbox submission URL
        url = "http://anubis.iseclab.org/submit.php"
        # Get the email address from the settings
        email = str(self.submission_settings_list["anubis"][0])

        form = MultiPartForm()
        form.add_field("notification", "email")
        form.add_field("email", email)
        filename = "IMHoneypot-%s" % hashlib.md5(file).hexdigest()
        form.add_field("analysisType", "file")
        form.add_file("executable", filename, fileHandle=open(file, "r"))
        body = str(form)
        # Form the request
        request = urllib2.Request(url)
        request.add_header("User-agent", "IMHoneypot")
        request.add_header("Content-type", form.get_content_type())
        request.add_header("Content-length", len(body))
        request.add_data(body)
        # Try to submit the file
        try:
            out = urllib2.urlopen(request)
            try:
                # Get the taskid from the response
                taskid = out.info()["taskid"]
            except:
                self.logger.log_console("Anubis sandbox submission error", "critical")
            else:
                self.logger.log_console("Anubis Task ID: %s" % taskid, "debug")

        except urllib2.HTTPError, e:
            self.logger.log_console("Anubis sandbox response error: %s" % e, "critical")
        except urllib2.URLError, e:
            self.logger.log_console("Anubis Sandbox response error: %s" % e, "critical")