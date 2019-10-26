from django.test import TestCase

# Create your tests here.

def get_accounts_snapshots_data(self, user, chart_name, chart_type, account_types, date_period_days=365):
    kwargs = {
        "account__user_institution__user": user,
        "date__gte": timezone.now() - timedelta(days=date_period_days),
        "account__type__name__in": account_types,
        "account__user_institution__is_active": True
    }
    qs = AccountSnapshot.objects.filter(**kwargs).order_by("date")
    transactions = qs \
        .values('date', 'account__currency__code') \
        .annotate(amount=Sum('current_balance'))
    data = dict()
    for item in transactions:
        currency_code = item["account__currency__code"]
        date = item["date"]
        # date = item["date"].strftime("%m/%d/%Y")
        amount = float(item["amount"])
        if not currency_code in data:
            data[currency_code] = dict()
        if not date in data[currency_code]:
            data[currency_code][date] = 0
        data[currency_code][date] += amount

    for k, v in data.items():
        v_mod = dict(sorted(v.items()))
        total_value = 0
        for key, value in v_mod.items():
            total_value += value
            v_mod[key] = round(total_value, 2)
        data[k] = v_mod

    return data, qs
