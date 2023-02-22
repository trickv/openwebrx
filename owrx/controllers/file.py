from owrx.controllers.template import WebpageController
from owrx.controllers.assets import AssetsController
from owrx.config.core import CoreConfig

class FileController(AssetsController):
    def getFilePath(self, file):
        return CoreConfig().getStoredFilePath(file)


class FilesController(WebpageController):
    def template_variables(self):
        files = CoreConfig().getStoredFiles()
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
