import stripe
from django.conf import settings

def create_checkout_session(line_items, metadata, success_url, cancel_url):
    """Create a Stripe Checkout Session and return the session object.

    This function centralizes stripe interaction and makes it easier to mock in tests.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        metadata=metadata,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session
