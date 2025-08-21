class TwoFactorAuthException(Exception):
    """Exception raised for errors in the two-factor authentication process."""

    def __init__(self, message="Two-factor authentication required."):
        self.message = message
        super().__init__(self.message)


class NonExistentAccountException(Exception):
    """Exception raised when the account does not exist."""

    def __init__(self, message="The account does not exist."):
        self.message = message
        super().__init__(self.message)


class GoogleVinculationException(Exception):
    """Exception raised when Google account vinculation is required."""

    def __init__(self, message="Google account vinculation is required."):
        self.message = message
        super().__init__(self.message)
