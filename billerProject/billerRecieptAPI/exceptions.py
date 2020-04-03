class ObjectNotPresentException(Exception):
    
    def __init__(self, errorMessage):
        self._m = errorMessage

    def __repr__(self):
        return f"ObjectNotPresentException({self._m})"