from owrx.controllers.template import WebpageController
from owrx.controllers.assets import ModificationAwareController
from owrx.breadcrumb import Breadcrumb, BreadcrumbItem, BreadcrumbMixin
from owrx.controllers.settings import SettingsBreadcrumb
from owrx.config.core import CoreConfig

from datetime import datetime, timezone
import mimetypes
import os
import re

class FileController(ModificationAwareController):
    def getModified(self, file):
        return datetime.fromtimestamp(os.path.getmtime(file), timezone.utc)

    def openFile(self, file):
        return open(file, "rb")

    def serve_file(self, file, content_type=None):
        try:
            modified = self.getModified(file)

            if not self.wasModified(file):
                self.send_response("", code=304)
                return

            f = self.openFile(file)
            data = f.read()
            f.close()

            if content_type is None:
                (content_type, encoding) = mimetypes.guess_type(file)
            self.send_response(data, content_type=content_type, last_modified=modified, max_age=3600)
        except FileNotFoundError:
            self.send_response("file '%s' not found" % file, code=404)

    def indexAction(self):
        filename = self.request.matches.group(1)
        self.serve_file("/tmp/" + filename)


class FilesController(WebpageController):
    def template_variables(self):
        files = [f for f in os.listdir('/tmp') if re.match(r'SSTV-[0-9]+-[0-9]+\.bmp', f)]
        rows  = ""

        for i in range(len(files)):
            # Start a row
            if i % 3 == 0:
                rows += '<tr>\n'
            # Print out individual tiles
            rows += ('<td class="file-tile"><img src="/files/%s" download="%s">' % (files[i], files[i])) + ('<p align="center">%s</p></td>\n' % files[i])
            # Finish a row
            if i % 3 == 2:
                rows += '</tr>\n'

        variables = super().template_variables()
        variables["rows"] = rows
        return variables

    def indexAction(self):
        self.serve_template("files.html", **self.template_variables())
