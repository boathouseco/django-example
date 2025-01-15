from django.shortcuts import redirect,render
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.conf import settings
from boathouseexample.boathouse import BoathouseApi
import json
import uuid
import asyncio

def home(request):
    # Create the createAccountUrl dynamically based on the request
    protocol = "https" if request.is_secure() else "http"
    create_account_url = f"{protocol}://{request.get_host()}/login"

    # Iframe URL
    iframe_url = (
        "https://my.boathouse.pro/api/v1/pricingtableiframe?p=7844a538-d99e-4dee-b296-08dc57f5b69a"
        f"&l={create_account_url}"
        "&s=https%3A%2F%2Fmy.boathouse.pro%2Fcss%2Fpricing-table-default.css"
    )

    return render(request, "home.html", {
        "create_account_url": create_account_url,
        "iframe_url": iframe_url,
    })


def login(request):
    if request.method == "POST":
        # Generate a random email address
        random_email_address = f"playground-{uuid.uuid4()}@mailexample.com"

        # Instantiate BoathouseApi and get a response
        boathouse_api = BoathouseApi(settings.BOATHOUSE_CONFIG)

        async def fetch_boathouse_response():
            return await boathouse_api.get_boathouse_response(random_email_address, None)

        # Run the async task to fetch response
        response_data = asyncio.run(fetch_boathouse_response())

        # Set the cookie with the paddle customer ID from the response
        response = redirect("/account")
        response.set_cookie("paddleCustomerId", response_data.paddleCustomerId, httponly=True)
        return response

    return render(request, "login.html")

def account(request):
    # Fetch the paddleCustomerId from cookies
    paddle_customer_id = request.COOKIES.get("paddleCustomerId")

    async def fetch_boathouse_response():
        boathouse_api = BoathouseApi(settings.BOATHOUSE_CONFIG)
        return await boathouse_api.get_boathouse_response(None, paddle_customer_id, "http://localhost:8000/account")

    # Run the async task to fetch response
    boathouse_response = asyncio.run(fetch_boathouse_response())

    context = {
        "paddle_customer_id": paddle_customer_id,
        "boathouse": boathouse_response,
        "pretty_boathouse_response": json.dumps(boathouse_response.dict(), indent=4)
    }

    return render(request, "account.html", context)

def processing(request):
    search_params = request.GET.get("pids")

    if not search_params:
        return HttpResponse("Missing 'pids' parameter.", status=400)

    price_ids = search_params.split(",")

    # Fetch the paddleCustomerId from cookies
    paddle_customer_id = request.COOKIES.get("paddleCustomerId")

    async def fetch_boathouse_response():
        boathouse_api = BoathouseApi(settings.BOATHOUSE_CONFIG)
        return await boathouse_api.get_boathouse_response(None, paddle_customer_id)

    # Run the async task to fetch response
    boathouse_response = asyncio.run(fetch_boathouse_response())

    # Check if the purchase is complete
    active_subscriptions = boathouse_response.activeSubscriptions
    checkout_completed = all(
        any(active_pid.lower() == pid.lower() for active_pid in active_subscriptions)
        for pid in price_ids
    )

    # Redirect or render based on the completion status
    if checkout_completed:
        return redirect("/account")

    return render(request, "processing.html")