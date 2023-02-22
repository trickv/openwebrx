from owrx.controllers.template import WebpageController
from owrx.controllers.assets import AssetsController
from owrx.config.core import CoreConfig

import os
import re

class FileController(AssetsController):
    def getFilePath(self, file):
        return CoreConfig().get_temporary_directory() + "/" + file


class FilesController(WebpageController):
    # Get list of files to work on, sorted in reverse alphabetic
    # order (so that newer files appear first)
    def getFileList(self):
        dir = CoreConfig().get_temporary_directory()
        files = [f for f in os.listdir(dir) if re.match(r'SSTV-[0-9]+-[0-9]+\.bmp', f)]
        return sorted(files, reverse=True)

    # Delete all files except for <keepN> newest ones
    def cleanFiles(self, keepN):
        dir = CoreConfig().get_temporary_directory()
        files = self.getFileList()
        for f in files[keepN:]:
            try:
                os.unlink(dir + "/" + f)
            except:
                pass

    def template_variables(self):
        files = self.getFileList()
        rows  = ""

        for i in range(len(files)):
            # Start a row
            if i % 3 == 0:
                rows += '<tr>\n'
            # Print out individual tiles
            rows += ('<td class="file-tile">' +
                ('<a href="/files/%s" download="%s">' % (files[i], files[i])) +
                ('<img src="/files/%s" download="%s">' % (files[i], files[i])) +
                ('<p align="center">%s</p>' % files[i]) +
                '</a></td>\n')
            # Finish a row
            if i % 3 == 2:
                rows += '</tr>\n'

        # Finish final row
        if len(files) > 0 and len(files) % 3 != 0:
            rows += '</tr>\n'

        variables = super().template_variables()
        variables["rows"] = rows
        return variables

    def indexAction(self):
        self.serve_template("files.html", **self.template_variables())
