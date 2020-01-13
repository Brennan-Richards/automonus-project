from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path("check-auth/", views.StripeChecker.as_view(), name="check_stripe"),

    #Creating internal and external transfers.
    path(
        "external-transfer-create/",
        views.ExternalTransferCreateView.as_view(),
        name="external_transfer_create",
    ),
    path(
        "external-transfer-value/<uuid:to_user>/",
        views.ExternalTransferValueView.as_view(),
        name="external_transfer_value",
    ),
    path(
        "external-transfer-success/",
        views.ExternalTransferSuccessView.as_view(),
        name="external_transfer_success",
    ),
    path(
        "internal-transfer-value/",
        views.InternalTransferValueView.as_view(),
        name="internal_transfer_value",
    ),
    path(
        "internal-transfer-success/",
        views.InternalTransferSuccessView.as_view(),
        name="internal_transfer_success",
    ),
    path("try-again-later/", views.TryAgainErrorView.as_view(), name="try_again_later"),

    #Subscription

    #Client views
    path("subscribe/", views.Subscribe.as_view(), name="subscribe"),
    path("subscribe/update-subscription/", views.UpdateSubscriptionView.as_view(), name="update_subscription"),
    #Stripe API
        #Create customer
    path("subscribe/stripe-api-create-customer/", views.stripe_create_customer, name="create_customer_stripe"),
        #Update customer subscription
    path(
        "subscribe/update-subscription/stripe-api-upgrade-subscription/",
        views.stripe_upgrade_subscription,
        name="update_subscription_stripe"
    ),
        #Delete subscription
    path(
        "subscribe/update-subscription/stripe-api-delete-subscription/",
        views.stripe_delete_subscription,
        name="delete_susbcription_stripe"
    ),
    path(
        "subscribe/update-subscription/stripe-api-reactivate-subscription/",
        views.stripe_reactivate_subscription,
        name="reactivate_susbcription_stripe"
    ),

    #Subscription Cost Calculator
    path("mock-subscription-form/", views.MockSubscriptionCreate.as_view(), name="mocksubscription_create"),
    path("mock-subscription/<int:pk>/update", views.MockSubscriptionUpdate.as_view(), name="mocksubscription_update"),
    path("mock-subscription-display/", views.MockSubscriptionDisplay.as_view(), name="mocksubscription_display")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
