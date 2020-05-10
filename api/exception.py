class UnsupportedOSError(Exception):
    def __str__(self):
        return "Unsupported operating system"


class IpFormatError(Exception):
    def __str__(self):
        return "Wrong ip format, try XX.XX.XX.XX format"


class PythonVersionError(Exception):
    def __init__(self, version):
        self.version = version

    def __str__(self):
        return f'Python version {self.version} is lower than 3.7.2'
