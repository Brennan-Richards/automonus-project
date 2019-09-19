from django.db import models
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import uuid
from income.models import Income
from django.db.models import Sum


@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    if not hasattr(user, "profile"):
        Profile.objects.get_or_create(user=user)
    pass


def user_post_save(sender, instance, created, **kwargs):
    print("user post save")
    if created:
        Profile.objects.get_or_create(user=instance)


post_save.connect(user_post_save, sender=User)


class Profile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    agree_to_receive_emails = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return "{}".format(self.user.username)

    def get_income(self):
        income = Income.objects.filter(user_institution__user=self.user)\
            .aggregate(total=Sum("projected_yearly_minus_tax"))
        print(income)
        income = income["total"] if income.get("total") else 0
        return {
            "per_day": round(income/365, 2),
            "per_week": round(income/52, 2),
            "per_month": round(income/12, 2),
            "total": round(income, 2)
        }
