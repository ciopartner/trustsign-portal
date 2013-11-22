# -*- coding: utf-8 -*-
import json
from django.contrib import messages
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from oscar.apps.basket.views import BasketView as CoreBasketView


def get_messages(basket, offers_before, offers_after,
                 include_buttons=True):
    """
    Return the messages about offer changes
    """
    # Look for changes in offers
    SHOW_NEW_TOTAL = False

    offers_lost = set(offers_before.keys()).difference(
        set(offers_after.keys()))
    offers_gained = set(offers_after.keys()).difference(
        set(offers_before.keys()))

    # Build a list of (level, msg) tuples
    offer_messages = []
    for offer_id in offers_lost:
        offer = offers_before[offer_id]
        msg = render_to_string(
            'basket/messages/offer_lost.html',
            {'offer': offer})
        offer_messages.append((
            messages.WARNING, msg))
    for offer_id in offers_gained:
        offer = offers_after[offer_id]
        msg = render_to_string(
            'basket/messages/offer_gained.html',
            {'offer': offer})
        offer_messages.append((
            messages.SUCCESS, msg))

    # We use the 'include_buttons' parameter to determine whether to show the
    # 'Checkout now' buttons.  We don't want to show these on the basket page.
    if SHOW_NEW_TOTAL:
        msg = render_to_string(
            'basket/messages/total.html',
            {'basket': basket,
             'include_buttons': include_buttons})
        offer_messages.append((
            messages.INFO, msg))

    return offer_messages


class BasketView(CoreBasketView):

    def json_response(self, ctx, flash_messages):
        basket_html = render_to_string(
            'basket/partials/basket_content.html',
            RequestContext(self.request, ctx))
        payload = {
            'content_html': basket_html,
            'total_items': self.request.basket.num_items,
            'messages': flash_messages.to_json()}
        return HttpResponse(json.dumps(payload),
                            content_type="application/json")