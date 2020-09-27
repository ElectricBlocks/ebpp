import json

class InvalidError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        rv = dict()
        rv["status"] = "INVALID_ERROR"
        rv["response"] = self.message
        return rv

class JsonError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        rv = dict()
        rv["status"] = "JSON_ERROR"
        rv["response"] = self.message
        return rv

class PPError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        rv = dict()
        rv["status"] = "PP_ERROR"
        rv["response"] = self.message
        return rv

class ConvError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        rv = dict()
        rv["status"] = "CONV_ERROR"
        rv["response"] = self.message
        return rv