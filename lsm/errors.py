class BaseError(BaseException):
    pass

class ExecReturnCodeError(BaseException):
    def __init__(self, cmd, code=-1, output=None):
        super(ExecReturnCodeError, self).__init__(
            '%s exited with code %d' % (cmd, code))
        self.code = code
        self.output = output