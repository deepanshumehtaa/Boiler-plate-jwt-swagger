from economy.forms import DepositForm, DepositCommentForm, ProductOrderForm
from economy.models import (
    Deposit,
    DepositComment,
    SociBankAccount,
    SociSession,
    SociProduct,
    ProductOrder,
)
from users.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
import datetime
from django.utils import timezone
from rest_framework import status
from django.http import HttpResponse
from django.core.exceptions import SuspiciousOperation


def economy_home(request):
    """Renders the economy homepage for a user. Includes list of deposits and a form for submitting a new deposit"""
    if request.method == "GET":
        ctx = {
            "deposit_form": DepositForm(),
            "deposit_history": Deposit.objects.filter(
                account=request.user.bank_account
            ),
            "current_user": request.user,
        }
        return render(request, template_name="economy/economy_home.html", context=ctx)

    elif request.method == "POST":  # Should this maybe be handled in a different view?
        form = DepositForm(request.POST, request.FILES)
        if form.is_valid():  # needs handling for when form.is_valid() is False
            obj = form.save(commit=False)
            obj.account = request.user.bank_account
            obj.save()

            ctx = {
                "deposit_form": DepositForm(),
                "deposit_history": Deposit.objects.filter(
                    account=request.user.bank_account
                ),
                "current_user": request.user,
            }
            return render(
                request, template_name="economy/economy_home.html", context=ctx
            )


def deposits(request):
    """Renders all deposits seperated by approved and not approved"""
    if request.method == "GET":
        ctx = {
            "deposits_not_approved": Deposit.objects.filter(signed_off_by=None),
            "deposits_approved": Deposit.objects.exclude(signed_off_by=None),
        }
        return render(
            request, template_name="economy/economy_deposits.html", context=ctx
        )


def deposit_approve(request, deposit_id):
    if request.method == "POST":
        deposit = get_object_or_404(Deposit, pk=deposit_id)
        soci_account = get_object_or_404(SociBankAccount, pk=deposit.account.id)
        soci_account.add_funds(deposit.amount)
        deposit.signed_off_by = request.user
        deposit.signed_off_time = datetime.datetime.now()
        deposit.save()
        return redirect(reverse(deposits))


def deposit_invalidate(request, deposit_id):
    if request.method == "POST":
        deposit = get_object_or_404(Deposit, pk=deposit_id)
        soci_account = get_object_or_404(SociBankAccount, pk=deposit.account.id)
        soci_account.remove_funds(deposit.amount)
        deposit.signed_off_by = None
        deposit.signed_off_time = None
        deposit.save()
        return redirect(reverse(deposits))


def deposit_edit(request, deposit_id):
    deposit = get_object_or_404(Deposit, pk=deposit_id)
    form = DepositForm(request.POST or None, instance=deposit)
    ctx = {"deposit_form": form, "deposit": deposit}
    if request.method == "GET":
        return render(
            request, template_name="economy/economy_deposit_edit.html", context=ctx
        )
    elif request.method == "POST":
        if form.is_valid:
            form.save()
            return redirect(reverse(economy_home))
    else:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# TODO: Refactor so it looks cleaner
def deposit_detail(request, deposit_id):
    """Renders a detailed view of a deposit, handles sumbission of a deposit comment if the request method is POST"""
    """Is a lot the code here redundant? Can the logic be simplified somewhat?"""
    if request.method == "GET":
        deposit = get_object_or_404(Deposit, pk=deposit_id)
        deposit_comment = DepositComment.objects.filter(deposit=deposit)
        ctx = {
            "deposit": deposit,
            "deposit_comment": deposit_comment,
            "comment_form": DepositCommentForm(),
        }
        return render(
            request, template_name="economy/economy_deposit_detail.html", context=ctx
        )

    elif request.method == "POST":
        deposit = get_object_or_404(Deposit, pk=deposit_id)
        deposit_comment = DepositCommentForm(request.POST)
        if deposit_comment.is_valid():
            obj = deposit_comment.save(commit=False)
            obj.deposit = deposit
            obj.user = request.user
            obj.save()

            deposit = get_object_or_404(Deposit, pk=deposit_id)  # wtf am i doing here
            deposit_comment = DepositComment.objects.order_by("created").filter(
                deposit=deposit
            )
            ctx = {
                "deposit": deposit,
                "deposit_comment": deposit_comment,
                "comment_form": DepositCommentForm(),
            }
            return render(
                request,
                template_name="economy/economy_deposit_detail.html",
                context=ctx,
            )


def soci_sessions(request):
    if request.method == "GET":
        session_filter = request.GET.get("filter", None)
        if session_filter == "closed":
            paginator = Paginator(
                SociSession.objects.filter(closed=True).order_by("-start"), 30
            )
        elif session_filter == "open":
            paginator = Paginator(
                SociSession.objects.filter(closed=False).order_by("-start"), 30
            )
        else:
            paginator = Paginator(SociSession.objects.order_by("-start"), 30)
            session_filter = None  # do this in case the variable is set to something weird? Covers all template cases

        page_number = request.GET.get("page")
        paginated_soci_sessions = paginator.get_page(page_number)
        ctx = {
            "sessions": paginated_soci_sessions,
            "filter": session_filter,
        }
        return render(
            request, template_name="economy/economy_soci_sessions.html", context=ctx
        )
    else:
        return HttpResponse(status.HTTP_405_METHOD_NOT_ALLOWED)


def soci_session_create(request):
    session = SociSession.objects.create(type="krysseliste", signed_off_by=request.user)
    return redirect(
        reverse(soci_session_detail, kwargs={"soci_session_id": session.id})
    )


def soci_session_delete(request, soci_session_id):
    if request.method == "POST":
        session = get_object_or_404(SociSession, pk=soci_session_id)
        if not session.closed:
            session.delete()
            return redirect(reverse(soci_sessions))
        else:
            raise (SuspiciousOperation)
    else:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def soci_session_close(request, soci_session_id):
    if request.method == "POST":
        session = get_object_or_404(SociSession, pk=soci_session_id)
        if session.closed:
            raise SuspiciousOperation
        else:
            for product_order in session.product_orders.all():
                product_order.source.remove_funds(
                    product_order.cost
                )  # charging amount due from list
                # if a source account does not exist this view crashes while still having charged
                # money and keeps the session open. Should this be handled? Or should we always assume a user
                # has an account?
            session.end = timezone.now()
            session.closed = True
            session.save()
        return redirect(reverse(soci_sessions))
    else:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def soci_session_detail(request, soci_session_id):
    if request.method == "GET":
        session = get_object_or_404(SociSession, pk=soci_session_id)
        ctx = {
            "session": session,
            "products": SociProduct.objects.all(),
            "users": User.objects.filter(bank_account__isnull=False),
            "product_order_form": ProductOrderForm(),
        }
        return render(
            request,
            template_name="economy/economy_soci_session_detail.html",
            context=ctx,
        )
    else:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def product_order_delete(request, product_order_id):
    if request.method == "POST":
        product_order = get_object_or_404(ProductOrder, pk=product_order_id)
        if product_order.session.closed:
            raise SuspiciousOperation  # closed sessions should not have products tampered with
        product_order.delete()
        return redirect(
            reverse(
                soci_session_detail,
                kwargs={"soci_session_id": product_order.session.id},
            )
        )
    else:
        return HttpResponse(status.HTTP_405_METHOD_NOT_ALLOWED)


def product_order_add(request, soci_session_id):
    if request.method != "POST":
        return HttpResponse(status.HTTP_405_METHOD_NOT_ALLOWED)

    session = get_object_or_404(SociSession, pk=soci_session_id)
    form_data = ProductOrderForm(request.POST)

    if not form_data.is_valid():
        raise SuspiciousOperation(
            "Error: Cannot add product orders to closed or non-existent sessions"
        )

    form = form_data.save(commit=False)
    form.session = session
    form.save()

    return redirect(
        reverse(soci_session_detail, kwargs={"soci_session_id": soci_session_id})
    )
