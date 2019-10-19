class BadAccountData(Exception):
    def __init__(self):
        # Call the base class constructor with the parameters it needs
        self.errors = errors
        super().__init__()
        # Now for your custom code...
        self.errors = errors
