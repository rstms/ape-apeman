# ape manager exceptions


class ApeManagerException(Exception):
    pass


class UnknownContractABI(ApeManagerException):
    pass


class ExplorerNotAvailable(ApeManagerException):
    pass
