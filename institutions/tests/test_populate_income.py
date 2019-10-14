from django.test import TestCase
import importlib
import os
from django.conf import settings
import institutions.models as test_model
# from institutions.models import client
# Create your tests here.
from django.contrib.auth.models import User
from income.models import Income, IncomeStream


ACCESS_TOKEN_1 = "TEST_TOKEN_1"
BANK_OF_AMERICA = "BANK_OF_AMERICA"
SUN_TRUST = "SUN_TRUST"
EMPTY_STREAMS = "EMPTY_STREAMS"

INCOME_RESPONSE = {
    ACCESS_TOKEN_1: {'income':
                     {'income_streams': [{'confidence': 0.99, 'days': 690, 'monthly_income': 500, 'name': 'UNITED AIRLINES'}, ],
                      'last_year_income': 6000,
                      'last_year_income_before_tax': 7285,
                      'max_number_of_overlapping_income_streams': 1,
                      'number_of_income_streams': 1,
                      'projected_yearly_income': 6085,
                      'projected_yearly_income_before_tax': 7389
                      },
                     'request_id': 'vqklFzddhj0Va9b'
                     },
    BANK_OF_AMERICA: {'income':
                      {'income_streams': [{'confidence': 0.99, 'days': 690, 'monthly_income': 500, 'name': 'UNITED AIRLINES'}],
                       'last_year_income': 6000,
                       'last_year_income_before_tax': 7285,
                       'max_number_of_overlapping_income_streams': 1,
                       'number_of_income_streams': 1,
                       'projected_yearly_income': 6085,
                       'projected_yearly_income_before_tax': 7389},
                      'request_id': 'j8f0wfFv1XkEUg8'
                      },
    SUN_TRUST: {'income':
                {'income_streams': [{'confidence': 0.99, 'days': 690, 'monthly_income': 500, 'name': 'UNITED AIRLINES'}],
                 'last_year_income': 6000,
                 'last_year_income_before_tax': 7285,
                 'max_number_of_overlapping_income_streams': 1,
                 'number_of_income_streams': 1,
                 'projected_yearly_income': 6085,
                 'projected_yearly_income_before_tax': 7389},
                'request_id': 'nQC7Pe4u7qo4Jvk'
                },
    EMPTY_STREAMS: {'income':
                    {'income_streams': [],
                     'last_year_income': 6000,
                     'last_year_income_before_tax': 7285,
                     'max_number_of_overlapping_income_streams': 1,
                     'number_of_income_streams': 1,
                     'projected_yearly_income': 6085,
                     'projected_yearly_income_before_tax': 7389},
                    'request_id': 'nQC7Pe4u7qo4Jvk'
                    }
}


class IncomeMock():

    def __init__(self, *args, **kwargs):
        pass

    def get(self, access_token):
        return INCOME_RESPONSE[access_token]


class MockPlaidClient():

    def __init__(self, *args, **kwargs):
        self.Income = IncomeMock()


class PopulateIncomeTest(TestCase):
    # institutions.tests.test_populate_income.PopulateIncomeTest
    fixtures = ['users_data']

    def setUp(self):
        self.first_user = User.objects.first()
        self.test_model = test_model
        self.test_model.client = MockPlaidClient()

    def test_base(self):
        institution = test_model.Institution.objects.create(
            name="Wells Fargo TEST", plaid_id="FIRST")
        self.first_user_institution, created = test_model.UserInstitution.objects.update_or_create(plaid_id='FIRST',
                                                                                                   user=self.first_user,
                                                                                                   institution=institution,
                                                                                                   is_active=True,
                                                                                                   defaults={"access_token": ACCESS_TOKEN_1})
        self.first_user_institution.populate_income_information()
        income = Income.objects.get(
            user_institution=self.first_user_institution)
        income_stream = IncomeStream.objects.filter(income=income)

        first_inc_resp = INCOME_RESPONSE[ACCESS_TOKEN_1]['income']

        #  check fields value
        self.assertEqual(first_inc_resp['max_number_of_overlapping_income_streams'],
                         income.max_number_of_overlapping_income_streams)
        self.assertEqual(first_inc_resp['number_of_income_streams'],
                         income.number_of_income_streams)

        self.assertEqual(first_inc_resp['last_year_income_before_tax'],
                         income.last_year_income_before_tax)
        self.assertEqual(first_inc_resp['last_year_income'],
                         income.last_year_income_minus_tax)

        self.assertEqual(first_inc_resp['projected_yearly_income_before_tax'],
                         income.projected_yearly_income_before_tax)
        self.assertEqual(first_inc_resp['projected_yearly_income'],
                         income.projected_yearly_minus_tax)

        # check calculate
        self.assertEqual(income.last_year_taxes,
                         round(income.last_year_income_before_tax - income.last_year_income_minus_tax, 2))
        self.assertEqual(income.projected_yearly_taxes,
                         round(income.projected_yearly_income_before_tax - income.projected_yearly_minus_tax, 2))

        # check count of array
        self.assertEqual(income_stream.count(), 1,
                         "check count income_streams")

    def test_empty_stream(self):
        institution = test_model.Institution.objects.create(
            name="Wells Fargo TEST", plaid_id=EMPTY_STREAMS)
        self.empty_stream, created = test_model.UserInstitution.objects.update_or_create(plaid_id=EMPTY_STREAMS,
                                                                                         user=self.first_user,
                                                                                         institution=institution,
                                                                                         is_active=True,
                                                                                         defaults={"access_token": EMPTY_STREAMS})
        self.empty_stream.populate_income_information()
        income = Income.objects.get(user_institution=self.empty_stream)
        income_stream = IncomeStream.objects.filter(income=income)

        empty_stream_inc_resp = INCOME_RESPONSE[EMPTY_STREAMS]['income']

        # check count of array
        self.assertEqual(income_stream.count(), 0,
                         "check count income_streams")
