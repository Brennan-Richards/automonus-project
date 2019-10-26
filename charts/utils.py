from django.db.models import Avg, Count, Min, Sum
from accounts.models import AccountSnapshot, Transaction
from income.models import Income
from liabilities.models import CreditCardSnapshot, StudentLoanSnapshot
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.contenttypes.models import ContentType


class ChartData():

    def prepare_chart_data(self, data, user, chart_name, chart_type):
        chart_series = list()
        chart_categories = list()  # x axis values

        for currency, dates_data in data.items():
            """Adding dates to chart_categories list in order to iterate them while preparing charts data.
            If some date has value for one currency, but it does not have it for another currency, then 0 value should be
            added instead"""

            """dates_data has a format of {date: amount, date2: amount2}"""
            chart_categories += list(dates_data.keys())  # keys are dates in this dictionary

        chart_categories = sorted(list(set(chart_categories)))  # removing duplicated values and sorting the list

        for currency, dates_data in data.items():
            chart_series_data = list()
            for date in chart_categories:
                if date in dates_data:
                    amount = dates_data[date]
                else:
                    amount = 0
                chart_series_data.append(amount)

            chart_series.append({
                "name": currency,
                "data": chart_series_data
            })
        chart_categories = [item.strftime("%m/%d/%Y") for item in chart_categories]
        chart_data = {"title": chart_name, "type": chart_type, "categories": chart_categories,
                      "chart_series": chart_series}
        print("4")
        return chart_data

    def prepare_chart_data_pie_chart(self, data, user, chart_name, chart_type):
        chart_series = list()
        chart_series_data = {"name": 'Categories',
                             "colorByPoint": "true",
                             "data": list()
                             }
        for name, val in data.items():
            chart_series_data["data"].append({
                "name": name,
                "y": val
            })
        chart_series.append(chart_series_data)

        chart_data = {"title": chart_name, "type": chart_type, "categories": list(data.keys()),
                      "chart_series": chart_series}
        return chart_data

    def get_transactions_data(self, user, chart_name, chart_type, account_types=None,
                              date_period_days=30, is_cumulative=False, model_name="Transaction"):
        if model_name == "Transaction":
            kwargs = {
                "account__user_institution__user": user,
                "account__type__name__in": account_types,
                "date__gte": timezone.now()-timedelta(days=date_period_days),
                "account__user_institution__is_active": True
            }
        else:  # InvestmentTransaction
            kwargs = {
                "account__user_institution__user": user,
                "date__gte": timezone.now() - timedelta(days=date_period_days),
                "type__name": "buy",
                "account__user_institution__is_active": True
            }

        # this does not include transaction with the amount below 0
        if not is_cumulative:
            kwargs["amount__gt"] = 0

        model = ContentType.objects.get(model=model_name.lower()).model_class()
        transactions_qs = model.objects.filter(**kwargs)
        transactions = transactions_qs \
            .values('date', 'currency__code') \
            .annotate(amount=Sum('amount'))
        data = dict()
        for item in transactions:
            currency_code = item["currency__code"]
            date = item["date"]
            # date = item["date"].strftime("%m/%d/%Y")
            amount = float(item["amount"])
            if not currency_code in data:
                data[currency_code] = dict()
            if not date in data[currency_code]:
                data[currency_code][date] = 0
            if is_cumulative:
                data[currency_code][date] += amount
            else:
                data[currency_code][date] += amount
        if is_cumulative:
            for k, v in data.items():
                v_mod = dict(sorted(v.items()))
                total_value = 0
                for key, value in v_mod.items():
                    total_value += value
                    v_mod[key] = round(total_value, 2)
                data[k] = v_mod
        # print(data)
        return data, transactions_qs

    #TODO: Get rid of this method and make it something more simple on the views.py page.
    def get_transactions_sum(self, user, account_types=None, date_period_days=30):
        # Gets total value of transactions over a given time period.
        kwargs = {
            "account__user_institution__user": user,
            "account__type__name__in": account_types,
            "date__gte": timezone.now()-timedelta(days=date_period_days),
            "amount__gt": 0,
            "account__user_institution__is_active": True
        }

        transactions = Transaction.objects.filter(**kwargs).values('date', 'currency__code') \
                                                  .annotate(amount=Sum('amount'))

        sum_transactions = 0
        for transaction in transactions:
            sum_transactions += transaction["amount"]

        return round(float(sum_transactions),2)


    def get_income_data(self, user, chart_name, chart_type):
        kwargs = {
            "user_institution__user": user,
            "user_institution__is_active": True
        }

        if chart_name == "Last year's income before and after taxes, cost of tax":
            income_data = Income.objects.filter(**kwargs).aggregate(
                last_year_income_minus_tax=Sum("last_year_income_minus_tax"),
                last_year_taxes=Sum("last_year_taxes")
            )
            data = {
                    "Last year income minus tax": round(float(income_data["last_year_income_minus_tax"]), 2),
                    "Last year taxes": round(float(income_data["last_year_taxes"]), 2)
                    }
        elif chart_name == "Projected income before and after taxes":
            income_data = Income.objects.filter(**kwargs).aggregate(
                projected_yearly_minus_tax=Sum("projected_yearly_minus_tax"),
                projected_yearly_taxes=Sum("projected_yearly_taxes")
            )
            data = {
                    "Projected yearly income minus tax": round(float(income_data["projected_yearly_minus_tax"]), 2),
                    "Projected yearly taxes": round(float(income_data["projected_yearly_taxes"]), 2)
                    }
        return data, income_data

    def get_spendings_data(self, user, chart_name, chart_type, account_types):
        print("get_spendings_data")
        data, transactions = self.get_transactions_data(user, chart_name, chart_type, account_types)
        data_dict = dict()
        for item in transactions.iterator():
            if ((item.category.sub_category_1 == "Payment") or (item.category.sub_category_1 == "Transfer")) and item.category.sub_category_2:
                category = item.category.sub_category_2
                print(category)
            else:
                category = item.category.sub_category_1

            if not category in data_dict:
                data_dict[category] = 0

            if item.amount > 0: #checks to see if transaction is outgoing, excludes incoming transactions of negative amounts
                data_dict[category] += float(item.amount)

        return data_dict, transactions

    def get_snapshots_data_by_model(self, user, chart_name, chart_type, account_types=None, account_subtypes=None, date_period_days=365, model_name="AccountSnapshot"):
        kwargs = {
            "account__user_institution__user": user,
            "date__gte": timezone.now() - timedelta(days=date_period_days),
            "account__user_institution__is_active": True
        }

        model = ContentType.objects.get(model=model_name.lower()).model_class()
        qs = model.objects.filter(**kwargs).order_by("date")

        if model_name == "AccountSnapshot":
            kwargs["type__name__in"] = account_types
            kwargs["subtype__name__in"] = account_subtypes
            snapshots = qs \
                .values('date', 'account__currency__code')\
                .annotate(field=Sum('current_balance'))
        else: #CreditCard
            snapshots = qs \
                .values('date', 'account__currency__code')\
                .annotate(field=Sum('last_statement_balance'))

        data = dict()
        for snapshot in snapshots:
            currency_code = snapshot["account__currency__code"]
            date = snapshot["date"]
            val = float(snapshot["field"])
            if not currency_code in data: #Creates a new empty dictionary for each currency_code (i.e. USD, GBP).
                data[currency_code] = dict()
            if not date in data[currency_code]: #Creates a key in currency_code dict. for each new date and sets = 0.
                data[currency_code][date] = 0
            data[currency_code][date] += val #Sets the value of date key to the 'val' of specified snapshot field.

        for k,v in data.items():
            #(Check) -- Aggregates items with same date in data dict. to create a pretty series and returns it.
            v_mod = dict(sorted(v.items()))
            total_value = 0
            for key, value in v_mod.items():
                total_value += value
                v_mod[key] = round(total_value, 2)
            data[k] = v_mod

        return data, qs

    def get_data_by_chart_name(self, user, chart_name, chart_type, qs_data=None, account_types=None, account_subtypes=None):
        """
        :param user:
        :param chart_name:
        :param chart_type:  "line", "pie", "column"
        :return:
        """
        #Accounts
        if chart_name == "Progress of your cash balances":
            print("2")
            data, qs_data = self.get_snapshots_data_by_model(user, chart_name, chart_type, account_types)
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)

        #Income
        elif chart_name == "Last year's income before and after taxes, cost of tax":
            data, qs_data = self.get_income_data(user, chart_name, chart_type)
            chart_data = self.prepare_chart_data_pie_chart(data, user, chart_name, chart_type)
        elif chart_name == "Projected income before and after taxes":
            data, qs_data = self.get_income_data(user, chart_name, chart_type)
            chart_data = self.prepare_chart_data_pie_chart(data, user, chart_name, chart_type)

        #Expenditures
        elif chart_name == "Your past month's spending by expenditure category:":
            data, qs_data = self.get_spendings_data(user, chart_name, chart_type, account_types)
            chart_data = self.prepare_chart_data_pie_chart(data, user, chart_name, chart_type)
        elif chart_name == "Your spending activity over the past quarter (90 days)":
            # line chart type by default
            data, qs_data = self.get_transactions_data(user, chart_name, chart_type, account_types, date_period_days=90)
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)

        #Liabilities
        elif chart_name == "Your student loan debt total over time":
            data, qs_data = self.get_snapshots_data_by_model(user, chart_name, chart_type, account_types, account_subtypes, model_name="CreditCardSnapshot")
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)
        elif chart_name == "Your credit card balance over time":
            data, qs_data = self.get_snapshots_data_by_model(user, chart_name, chart_type)
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)

        #Investments
        elif chart_name == "Progress of your total investments":
            data, qs_date = self.get_snapshots_data_by_model(user, chart_name, chart_type, account_types)
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)

        return chart_data, qs_data

    def get_charts_data_by_module(self, user, chart_type, category, account_types=None, account_subtypes=None):
        #This method returns a series of data + chart feature options for HighCharts on the frontend
        charts_data = list()
        if category == "spending":
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Your spending activity over the past quarter (90 days)",
                                                              chart_type=chart_type, account_types=account_types)
            charts_data.append(chart_data)
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Your past month's spending by expenditure category:",
                                                              chart_type="pie", account_types=account_types)
            charts_data.append(chart_data)
        elif category == "income":
            print("income")
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Last year's income before and after taxes, cost of tax", chart_type=chart_type)
            charts_data.append(chart_data)

            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Projected income before and after taxes", chart_type=chart_type)
            charts_data.append(chart_data)

        elif category == "liabilities":
          chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Your student loan debt total over time", chart_type=chart_type,
                                                            account_types=account_types, account_subtypes=account_subtypes)
          charts_data.append(chart_data)
          chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Your credit card balance over time", chart_type=chart_type,
                                                            account_types=account_types)
          charts_data.append(chart_data)
        elif category == "investments":
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Progress of your total investments", chart_type=chart_type,
                                                              account_types=account_types)
            charts_data.append(chart_data)
        elif category == "accounts":
            print("1")
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Progress of your cash balances", chart_type="line",
                                                              account_types=account_types)
            charts_data.append(chart_data)
        print("5")
        return charts_data
