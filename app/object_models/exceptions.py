class HealthCheckException(Exception):
    def __init__(self, module):
        self.module = module


class InputFileException(Exception):
    def __init__(self, mess="InputFileException"):
        self.mess = mess
        self.return_mess = "invalid input file"
        self.err_code = 1


class DetectException(Exception):
    def __init__(self, mess="DetectException"):
        self.mess = mess
        self.return_mess = "detection error"
        self.err_code = 2


class CannotDetectException(Exception):
    def __init__(self, mess="DetectException"):
        self.mess = mess
        self.return_mess = "cannot detect error"
        self.err_code = 2


class DetectSizeException(Exception):
    def __init__(self, mess="DetectSizeException"):
        self.mess = mess
        self.return_mess = "detect size error"
        self.err_code = 2


class MappingException(Exception):
    def __init__(self, mess="MappingException"):
        self.mess = mess
        self.return_mess = "mapping error"
        self.err_code = 3


class WrongOCRException(Exception):
    def __init__(self, mess="WrongOCRException"):
        self.mess = mess
        self.return_mess = "wrong ocr error"
        self.err_code = 4


class BlockedException(Exception):
    def __init__(self, mess="BlockedException"):
        self.mess = mess
        self.return_mess = "site is blocked"
        self.err_code = 4


class NoElementException(Exception):
    def __init__(self, mess="NoElementException"):
        self.mess = mess
        self.return_mess = "site is blocked"
        self.err_code = 4


class TimeoutException(Exception):  # Custom exception class
    pass


class PipelineException(Exception):
    def __init__(self, mess="PiplineException"):
        self.mess = mess
        self.return_mess = "Pipeline is not loaded"
        self.err_code = 5


class ClassifyTitleException(Exception):  # Custom exception class
    def __init__(self, mess="NoClassify", label=None):
        self.mess = mess
        self.return_mess = "Can't classify  this title or it is in an unknown class"
        self.err_code = 5
        self.label = label


class SizeException(Exception):
    def __init__(self, mess="Size image  > 10Mb"):
        self.mess = mess
        self.return_mess = "Max size of file must be less than 10Mb"
        self.err_code = 6


class SizeImageException(Exception):
    def __init__(self, mess="height, width image < 500px"):
        self.mess = mess
        self.return_mess = "Min height and weight of image  must be more than 500px"
        self.err_code = 7
