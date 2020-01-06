from django.db.models import Avg, Count, Min, Sum
from accounts.models import AccountSnapshot, Transaction
from income.models import Income, IncomeStream
from liabilities.models import CreditCardSnapshot, StudentLoanSnapshot, StudentLoan, CreditCard
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
        # print(data)
        # print(chart_categories) #Format: [[datetime.date(2019, 10, 30)],[...]]
        for currency, dates_data in data.items():
            chart_series_data = list()
            for date in chart_categories:
                if date in dates_data:
                    amount = dates_data[date]
                else:
                    amount = 0
                chart_series_data.append(amount)
            # print(chart_series_data)
            chart_series.append({
                "name": "Current Total Balance",
                "data": chart_series_data
            })
        # print(chart_series, "1")

        if chart_name == "Your student loan debt total over time":
            student_loans = StudentLoan.objects.filter(user_institution__user=user, user_institution__is_active=True)
            for loan in student_loans:
                amortization_series = list()
                amortization_dates = list()
                amortization_data = loan.amortize(30, loan.minimum_payment_amount)
                amortization_points_data = amortization_data[0]
                amortization_dates_data = amortization_data[1]
                counter = 0
                for value in amortization_points_data: #[val1, val2, ...]
                    if (len(amortization_series) - 1) <= counter:
                        amortization_series.append(value)
                        # print(counter)
                        # print(value, len(amortization_series), "append")
                        counter += 1
                    else:
                        amortization_series[counter] += amount
                        # print(counter)
                        # print(value, len(amortization_series), "aggregate")
                        counter += 1

                for date in amortization_dates_data: #[date1, date2, ...]
                    if not date in chart_categories:
                        chart_categories.append(date)

                # print(type(amortization_dates_data[0]), type(chart_categories[0]))

                for snapshot_date in chart_categories:
                    if amortization_dates_data[0] > snapshot_date:
                        amortization_series.insert(0, [])
                    # print(date, "XX")

                if amortization_series[-1] > amortization_series[-2]: #If slope is increasing
                    # print(amortization_series[-1], amortization_series[-2])
                    color = 'red'
                else: # slope decreasing
                    color = 'green'

                chart_series.append({
                    "name": "Projection of your {} loan balance at minimum payment amount".format(loan.guarantor_name),
                    "data": amortization_series,
                    "color":color
                    })

        # print(chart_categories)
        chart_categories = [item.strftime("%m/%d/%Y") for item in chart_categories]
        chart_data = {"title": chart_name, "type": chart_type, "categories": chart_categories,
                      "chart_series": chart_series}
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

    def get_transactions_data(self, user, chart_name, chart_type, date_period_days, account_types=None,
                              is_cumulative=False, model_name="Transaction"):
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

    def get_income_data(self, user, chart_name, chart_type):
        kwargs = dict()
        if chart_name == "Your monthly income by income stream":
            kwargs["income__user_institution__user"] = user
            kwargs["income__user_institution__is_active"] = True
            income_data = IncomeStream.objects.filter(**kwargs)
            data = dict()
            for stream in income_data:
                data[stream.name] = round(float(stream.monthly_income), 2)
            print(data)

        elif chart_name == "Last year's income before and after taxes, cost of tax":
            kwargs["user_institution__user"] = user
            kwargs["user_institution__is_active"] = True

            income_data = Income.objects.filter(**kwargs).aggregate(
                last_year_income_minus_tax=Sum("last_year_income_minus_tax"),
                last_year_taxes=Sum("last_year_taxes")
            )
            data = {
                    "Last year income minus tax": round(float(income_data["last_year_income_minus_tax"]), 2),
                    "Last year taxes": round(float(income_data["last_year_taxes"]), 2)
                    }
        elif chart_name == "Projected income before and after taxes":
            kwargs["user_institution__user"] = user
            kwargs["user_institution__is_active"] = True
            income_data = Income.objects.filter(**kwargs).aggregate(
                projected_yearly_minus_tax=Sum("projected_yearly_minus_tax"),
                projected_yearly_taxes=Sum("projected_yearly_taxes")
            )
            data = {
                    "Projected yearly income minus tax": round(float(income_data["projected_yearly_minus_tax"]), 2),
                    "Projected yearly taxes": round(float(income_data["projected_yearly_taxes"]), 2)
                    }
        return data, income_data

    def get_spendings_data(self, user, chart_name, chart_type, date_period_days, account_types):
        print("get_spendings_data")
        data, transactions = self.get_transactions_data(user, chart_name, chart_type, date_period_days, account_types)
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

    def get_snapshots_data_by_model(self, user, chart_name, chart_type, model_name, account_types=None, account_subtypes=None, date_period_days=365):
        kwargs = {
            "account__user_institution__user": user,
            "date__gte": timezone.now() - timedelta(days=date_period_days),
            "account__user_institution__is_active": True
        }

        if model_name == "AccountSnapshot":
            kwargs["account__type__name__in"] = account_types
            if account_subtypes is not None:
                kwargs["account__subtype__name__in"] = account_subtypes

            model = ContentType.objects.get(model=model_name.lower()).model_class()
            qs = model.objects.filter(**kwargs).order_by("date")

            snapshots = qs \
                .values('date', 'account__currency__code')\
                .annotate(field=Sum('current_balance'))

        else: #CreditCard
            model = ContentType.objects.get(model=model_name.lower()).model_class()
            qs = model.objects.filter(**kwargs).order_by("date")
            snapshots = qs \
                .values('date', 'account__currency__code')\
                .annotate(field=Sum('last_statement_balance'))

        data = dict() #Finishes as {Currency:{date1:val1},{date2:val2}}
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
            #(Check) -- Aggregates items with same date in <data> dictionary to create a pretty series and returns it.
            v_mod = dict(sorted(v.items()))
            total_value = 0
            for key, value in v_mod.items():
                total_value += value
                v_mod[key] = round(total_value, 2)
            data[k] = v_mod

        return data, qs

    def get_data_by_chart_name(self, user, chart_name, chart_type, date_period_days=None, qs_data=None, account_types=None, account_subtypes=None):
        """
        :param user:
        :param chart_name:
        :param chart_type:  "line", "pie", "column"
        :return:
        """
        #Accounts
        if chart_name == "Progress of your cash balances":
            print("2")
            data, qs_data = self.get_snapshots_data_by_model(user, chart_name, chart_type, model_name="AccountSnapshot", account_types=account_types, account_subtypes=account_subtypes)
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)

        #Income
        elif chart_name == "Your monthly income by income stream":
            data, qs_data = self.get_income_data(user, chart_name, chart_type)
            chart_data = self.prepare_chart_data_pie_chart(data, user, chart_name, chart_type)
        elif chart_name == "Last year's income before and after taxes, cost of tax":
            data, qs_data = self.get_income_data(user, chart_name, chart_type)
            chart_data = self.prepare_chart_data_pie_chart(data, user, chart_name, chart_type)
        elif chart_name == "Projected income before and after taxes":
            data, qs_data = self.get_income_data(user, chart_name, chart_type)
            chart_data = self.prepare_chart_data_pie_chart(data, user, chart_name, chart_type)

        #Expenditures
        elif chart_name == "Your past month's spending by expenditure category:":
            data, qs_data = self.get_spendings_data(user, chart_name, chart_type, date_period_days, account_types)
            chart_data = self.prepare_chart_data_pie_chart(data, user, chart_name, chart_type)
        elif chart_name == "Your spending activity over the past 30 days":
            # line chart type by default
            data, qs_data = self.get_transactions_data(user, chart_name, chart_type, date_period_days, account_types)
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)

        #Liabilities
        elif chart_name == "Your student loan debt total over time":
            data, qs_data = self.get_snapshots_data_by_model(user, chart_name, chart_type, model_name="AccountSnapshot", account_types=account_types, account_subtypes=account_subtypes)
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)
        elif chart_name == "Your credit card balance over time":
            data, qs_data = self.get_snapshots_data_by_model(user, chart_name, chart_type, model_name="CreditCardSnapshot")
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)

        #Investments
        elif chart_name == "Progress of your total investments":
            data, qs_date = self.get_snapshots_data_by_model(user, chart_name, chart_type, model_name="AccountSnapshot", account_types=account_types)
            chart_data = self.prepare_chart_data(data, user, chart_name, chart_type)

        return chart_data, qs_data

    def get_charts_data_by_module(self, user, chart_type, category, date_period_days=None, account_types=None, account_subtypes=None):
        #This method returns one or more series of data + chart configuration options for use with HighCharts
        charts_data = list()
        if category == "spending":
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Your spending activity over the past 30 days",
                                                              date_period_days=date_period_days, chart_type=chart_type, account_types=account_types)
            charts_data.append(chart_data)
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Your past month's spending by expenditure category:",
                                                              date_period_days=date_period_days, chart_type="pie", account_types=account_types)
            charts_data.append(chart_data)

        elif category == "income":
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Your monthly income by income stream", chart_type=chart_type)
            charts_data.append(chart_data)
        elif category == "income2":
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Last year's income before and after taxes, cost of tax", chart_type=chart_type)
            charts_data.append(chart_data)

            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Projected income before and after taxes", chart_type=chart_type)
            charts_data.append(chart_data)

        elif category == "liabilities":
            if StudentLoan.objects.filter(user_institution__is_active=True, account__user_institution__user=user):
              chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Your student loan debt total over time", chart_type=chart_type,
                                                                account_types=account_types, account_subtypes=account_subtypes)
              charts_data.append(chart_data)
            if CreditCard.objects.filter(user_institution__is_active=True, account__user_institution__user=user):
              chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Your credit card balance over time", chart_type=chart_type,
                                                                account_types=account_types)
              charts_data.append(chart_data)

        elif category == "investments":
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Progress of your total investments", chart_type=chart_type,
                                                              account_types=account_types)
            charts_data.append(chart_data)

        elif category == "accounts":
            chart_data, qs_data = self.get_data_by_chart_name(user=user, chart_name="Progress of your cash balances", chart_type="line",
                                                              account_types=account_types)
            charts_data.append(chart_data)

        return charts_data
