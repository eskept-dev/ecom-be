import os
from logging.handlers import RotatingFileHandler


class CustomRotatingFileHandler(RotatingFileHandler):
    def doRollover(self):
        """
        Override to rename files as django.1.log, django.2.log, etc.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
            
        base, ext = os.path.splitext(self.baseFilename)
        for i in range(self.backupCount - 1, 0, -1):
            sfn = f"{base}.{i}{ext}"
            dfn = f"{base}.{i+1}{ext}"
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)

        dfn = f"{base}.1{ext}"

        if os.path.exists(dfn):
            os.remove(dfn)
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
        self.mode = 'w'
        self.stream = self._open()
