"""
Stripe Service — Subscriptions, Payments, Webhooks
"""
import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

async def create_checkout_session(user, tier, success_url, cancel_url):
    """Create Stripe Checkout session."""
    price_map = {
        "pro": settings.STRIPE_PRO_PRICE_ID,
        "enterprise": settings.STRIPE_ENTERPRISE_PRICE_ID,
    }
    price_id = price_map.get(tier)
    if not price_id:
        raise ValueError(f"No price for tier: {tier}")
    
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, name=user.full_name)
        customer_id = customer.id
    else:
        customer_id = user.stripe_customer_id

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        allow_promotion_codes=True,
        subscription_data={"trial_period_days": 14},
    )
    return session.url

async def handle_webhook(payload, sig_header):
    """Process Stripe webhooks."""
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
    handlers = {
        "customer.subscription.created": _on_sub_created,
        "customer.subscription.deleted": _on_sub_deleted,
        "invoice.payment_failed": _on_payment_failed,
    }
    handler = handlers.get(event["type"])
    if handler:
        await handler(event["data"]["object"])
    return {"status": "ok"}

async def _on_sub_created(sub): pass
async def _on_sub_deleted(sub): pass
async def _on_payment_failed(invoice): pass
