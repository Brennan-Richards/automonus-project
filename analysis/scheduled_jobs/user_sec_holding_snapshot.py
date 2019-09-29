from institutions.models import UserInstitution

class CreateUserSecurityHoldingSnapshot():
    """This class is launched by scheduler"""

    def __init__(self, *args, **kwargs):
        print("Creation of user_holding_security snapshot: started")
        self.launch()
        print("Creation of user_holding_security snapshot: finished")

    def launch(self):
        user_institutions = UserInstitution.objects.filter(is_active=True)
        for user_institution in user_institutions.iterator():
            user_institution.populate_securities_and_holdings()


if __name__ == '__main__':
    CreateUserSecurityHoldingSnapshot()