from institutions.models import UserInstitution


class CreateAccountSnapshot():
    """This class is launched by scheduler"""

    def __init__(self, *args, **kwargs):
        print("Creation of accounts snapshot: started")
        self.launch()
        print("Creation of accounts snapshot: finished")

    def launch(self):
        user_institutions = UserInstitution.objects.filter(is_active=True)
        for user_institution in user_institutions.iterator():
            user_institution.populate_or_update_accounts()
            """
            Update will be triggered at the end of populate_or_update method
            This is need for creating a snapshot for the initial creation of the accounts.
            """


if __name__ == '__main__':
    CreateAccountSnapshot()