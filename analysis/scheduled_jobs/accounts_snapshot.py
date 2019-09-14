from institutions.models import UserInstitution
from accounts.models import AccountSnapshot
from django.utils import timezone


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
            accounts = user_institution.account_set.filter(is_active=True)
            for account in accounts.iterator():
                self.create_account_snapshot(account)

    def create_account_snapshot(self, account):
        available_balance = account.available_balance
        current_balance = account.current_balance
        limit_amount = account.limit_amount
        current_date = timezone.now().date()
        AccountSnapshot.objects.get_or_create(account=account, date=current_date, defaults={"available_balance": available_balance,
                                                        "current_balance": current_balance, "limit_amount": limit_amount
                                                        })


if __name__ == '__main__':
    CreateAccountSnapshot()