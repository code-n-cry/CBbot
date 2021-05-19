class EmailDoesNotExists(Exception):
    pass


class InvalidAddress(Exception):
    pass


class AmountError(Exception):
    pass


class BadTransaction(Exception):
    pass


class BadBalance(Exception):
    pass


class EmailVerifyRequestsExpired(Exception):
    pass