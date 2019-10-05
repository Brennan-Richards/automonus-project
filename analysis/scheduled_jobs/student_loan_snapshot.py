from institutions.models import UserInstitution

class CreateStudentLoanSnapshot():
    """This class is launched by scheduler"""

    def __init__(self, *args, **kwargs):
        print("Creation of student loan snapshot: started")
        self.launch()
        print("Creation of student loan snapshot: finished")

    def launch(self):
        user_institutions = UserInstitution.objects.filter(is_active=True)
        for user_institution in user_institutions.iterator():
            user_institution.populate_liabilities_data()
            """
            Update will be triggered at the end of populate_or_update method
            This is need for creating a snapshot for the initial creation of the accounts.
            """


if __name__ == '__main__':
    CreateStudentLoanSnapshot()