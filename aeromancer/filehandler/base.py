import abc
import fnmatch


class FileHandler(object):
    __metaclass__ = abc.ABCMeta

    INTERESTING_PATTERNS = []

    def supports_file(self, file_obj):
        """Does this plugin want to process the file?
        """
        return any(fnmatch.fnmatch(file_obj.path, ip)
                   for ip in self.INTERESTING_PATTERNS)

    @abc.abstractmethod
    def process_file(self, session, file_obj):
        return

    @abc.abstractmethod
    def delete_data_for_file(self, session, file_obj):
        return
