from django.shortcuts import render
from django.conf import settings

from facebook_business.api import FacebookAdsApi
from facebook_business import adobjects


# Create your views here.

def marketing_master_dashboard(request):
    return render(request, 'marketing/marketing_master_dashboard.html')

def facebook_ads_dashboard(request):

    #Initialize Facebook Marketing API

    my_app_id = '614194015825107'
    my_app_secret = 'dfa2e645384c4184d9a4231578720745'
    my_access_token = 'EAAIumzAi7NMBAFNorDodaoZBSOik33EMSr2AaTM0GYH5YkwRn1HN9JoCJyM2sFBjUZCPLCwZB8LrrST5q29nC4HSVrqgXDvXCPPTQy1QttCR5WSi1nqiRvIq4TZBvnyydjezlbFPuxgC5brBxzKKOX95fxZCRj1MMPKp43ewQqrBQczjJLtzhJsmZAhUl8HDaCYE5oHa6TXwZCQWjE779tcuHycRDXAMKkSFyavfh82pwZDZD' # Your user access token
    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    

    #Add after FacebookAdsApi.init
    me = adobjects.AdUser(fbid='me')
    my_account = me.get_ad_accounts()[0]

    print(my_account)

    return render(request, 'marketing/facebook_ads_dashboard.html')

def google_ads_dashboard(request):
    return render(request, 'marketing/google_ads_dashboard.html')

def yelp_ads_dashboard(request):
    return render(request, 'marketing/yelp_ads_dashboard.html')
