from django.conf import settings
from django.test import TestCase
from urllib.parse import urlencode
from economy.models import Deposit

from economy.tests.factories import (
    SociBankAccountFactory,
    DepositFactory,
    TransferFactory,
    ProductOrderFactory,
    DepositCommentFactory,
    SociSessionFactory,
    SociProductFactory
)
from economy.forms import DepositForm, DepositCommentForm
from django.urls import reverse
from economy.views import (
    deposit_approve,
    deposit_invalidate,
    economy_home,
    deposits,
    deposit_detail,
    deposit_edit,
)
from users.tests.factories import UserFactory


class SociBankAccountTest(TestCase):
    def setUp(self):
        self.soci_account = SociBankAccountFactory(balance=500)

    def test_account_with_transactions__transaction_history_retrieved_correctly(self):
        SociBankAccountFactory(card_uuid=settings.SOCI_MASTER_ACCOUNT_CARD_ID)
        extra_account = SociBankAccountFactory(balance=2000)

        DepositFactory(account=self.soci_account, amount=1000)
        ProductOrderFactory(source=self.soci_account)
        TransferFactory(source=extra_account, destination=self.soci_account, amount=500)
        history = self.soci_account.transaction_history

        self.assertEqual(3, len(history))
        self.assertEqual(1, history["deposits"].count())
        self.assertEqual(1, history["product_orders"].count())
        self.assertEqual(1, history["transfers"].count())

    def test_account__add_funds__added_correctly(self):
        self.soci_account.add_funds(500)

        self.assertEqual(1000, self.soci_account.balance)

    def test_account__remove_funds__removed_correctly(self):
        self.soci_account.remove_funds(500)

        self.assertEqual(0, self.soci_account.balance)


class SociSessionTest(TestCase):
    def setUp(self):
        SociBankAccountFactory(card_uuid=settings.SOCI_MASTER_ACCOUNT_CARD_ID)
        self.session = SociSessionFactory()
        self.product = SociProductFactory(price=30)
        ProductOrderFactory(order_size=100, session=self.session, product=self.product)
        ProductOrderFactory(order_size=200, session=self.session, product=self.product)

    def test_total_product_orders__correct_amount_returned(self):
        self.assertEqual(2, self.session.total_product_orders)

    def test__total_revenue__returns_correct_sum(self):
        expected_revenue = (30 * 100) + (30 * 200)
        self.assertEqual(expected_revenue, self.session.total_revenue)


class ProductOrderTest(TestCase):
    def setUp(self):
        SociBankAccountFactory.create(card_uuid=settings.SOCI_MASTER_ACCOUNT_CARD_ID)
        self.product = SociProductFactory.create(price=65)
        self.product_order = ProductOrderFactory.create(order_size=150, product=self.product)

    def test__product_order_cost__returns_correct_amount(self):
        expected_cost = 65 * 150
        self.assertEqual(expected_cost, self.product_order.cost)


class DepositCommentTest(TestCase):
    def setUp(self):
        self.deposit_comment = DepositCommentFactory()

    def test__str_and_repr_does_not_crash(self):
        str(self.deposit_comment)
        repr(self.deposit_comment)

    def test__short_comment_value__does_not_render_ellipses(self):
        self.deposit_comment.comment = "Short and sweet."
        self.deposit_comment.save()

        self.assertNotIn("..", str(self.deposit_comment))

    def test__long_comment_value__renders_ellipses(self):
        self.deposit_comment.comment = "This is definitely not short and sweet."
        self.deposit_comment.save()

        self.assertIn("..", str(self.deposit_comment))


class DepositFormTest(TestCase):
    def setUp(self):
        self.deposit = DepositFactory()

    def test__valid_deposit_form__is_valid_returns_true(self):
        form = DepositForm(
            data={
                "amount": self.deposit.amount,
                "description": self.deposit.description,
                "receipt": self.deposit.receipt,
            }
        )
        self.assertTrue(form.is_valid())

    def test__invalid_deposit_form__is_valid_returns_false(self):
        form = DepositForm(
            data={
                "description": self.deposit.description,
                "receipt": self.deposit.receipt,
            }
        )
        self.assertFalse(form.is_valid())

    def test__invalid_inputs__is_valid_returns_false(self):
        form = DepositForm(data={"description": 123154, "amount": "Wrong string"})
        self.assertFalse(form.is_valid())


class DepositCommentFormTest(TestCase):
    def setUp(self):
        self.deposit_comment = DepositCommentFactory()

    def test__valid_deposit_comment_form__is_valid_returns_true(self):
        form = DepositCommentForm(data={"comment": self.deposit_comment.comment})
        self.assertTrue(form.is_valid())

    def test__deposit_comment_form_empty_data_set__is_valid_returns_false(self):
        form = DepositCommentForm(data={})
        self.assertFalse(form.is_valid())


class DepositApproveViewTest(TestCase):
    def setUp(self):
        self.not_approved_deposit = DepositFactory(signed_off_by=None)
        self.signing_user = UserFactory()
        self.soci_bank_account = SociBankAccountFactory()
        self.user_getting_funds = self.soci_bank_account.user

        self.deposit_from_user_getting_funds = DepositFactory(
            account=self.user_getting_funds.bank_account, amount=200
        )

    def test__not_signed_deposit_approve_view__is_valid(self):
        self.client.force_login(self.signing_user)
        self.assertFalse(None, self.not_approved_deposit.signed_off_by)
        self.client.post(
            reverse(
                viewname=deposit_approve,
                kwargs={"deposit_id": self.not_approved_deposit.id},
            )
        )
        self.not_approved_deposit.refresh_from_db()
        self.assertNotEqual(None, self.not_approved_deposit.signed_off_by)

    def test__approved_deposit__adds_funds_to_account(self):
        balance_before_approval = self.user_getting_funds.bank_account.balance
        self.client.force_login(self.signing_user)
        self.client.post(
            reverse(
                viewname=deposit_approve,
                kwargs={"deposit_id": self.deposit_from_user_getting_funds.id},
            )
        )
        self.user_getting_funds.bank_account.refresh_from_db()
        balance_after_approval = self.user_getting_funds.bank_account.balance
        balance_difference = balance_after_approval - balance_before_approval
        self.assertEqual(200, balance_difference)

    def test__approve_view__redirects_to_deposits_view(self):
        self.client.force_login(self.signing_user)
        response = self.client.post(
            reverse(
                viewname=deposit_approve, kwargs={"deposit_id": DepositFactory().id}
            )
        )
        self.assertRedirects(response, reverse(viewname=deposits))

    def test__approve_view__returns_status_code_302(self):
        self.client.force_login(self.signing_user)
        response = self.client.post(
            reverse(
                viewname=deposit_approve, kwargs={"deposit_id": DepositFactory().id}
            )
        )
        self.assertEqual(302, response.status_code)


class DepositInvalidateViewTest(TestCase):
    def setUp(self):
        self.signing_user = UserFactory()
        self.approved_deposit = DepositFactory(signed_off_by=self.signing_user)
        self.soci_bank_acount = SociBankAccountFactory()
        self.user_losing_funds = self.soci_bank_acount.user
        self.deposit_from_user_losing_funds = DepositFactory(
            account=self.user_losing_funds.bank_account,
            amount=400,
            signed_off_by=self.signing_user,
        )

    def test__signed_deposit_invalidate_view__is_invalidated(self):
        self.client.force_login(self.signing_user)
        self.assertNotEqual(None, self.approved_deposit.signed_off_by)
        self.client.post(
            reverse(
                viewname=deposit_invalidate,
                kwargs={"deposit_id": self.approved_deposit.id},
            )
        )
        self.approved_deposit.refresh_from_db()
        self.assertEqual(None, self.approved_deposit.signed_off_by)

    def test__invalidated_deposit__subtracts_funds_from_account(self):
        balance_before_invalidation = self.user_losing_funds.bank_account.balance
        self.client.force_login(self.signing_user)
        self.client.post(
            reverse(
                viewname=deposit_invalidate,
                kwargs={"deposit_id": self.deposit_from_user_losing_funds.id},
            )
        )
        self.user_losing_funds.bank_account.refresh_from_db()
        balance_after_invalidation = self.user_losing_funds.bank_account.balance
        balance_difference = balance_after_invalidation - balance_before_invalidation
        self.assertEqual(-400, balance_difference)

    def test__invalidate_view__returns_status_code_302(self):
        self.client.force_login(self.signing_user)
        response = self.client.post(
            reverse(
                viewname=deposit_invalidate, kwargs={"deposit_id": DepositFactory().id}
            )
        )
        self.assertEqual(302, response.status_code)

    def test__invalidate_view__redirects_to_deposits_view(self):
        self.client.force_login(self.signing_user)
        response = self.client.post(
            reverse(
                viewname=deposit_invalidate, kwargs={"deposit_id": DepositFactory().id}
            )
        )
        self.assertRedirects(response, reverse(viewname=deposits))


class EconomyHomeViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.bank_account = SociBankAccountFactory(user=self.user)
        self.generic_deposit = DepositFactory()
        self.deposit_POST_in_db = DepositFactory(
            id=1437, description="Dear god please work"
        )

    def test__economy_home_view_GET_request__renders_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse(viewname=economy_home))
        self.assertTemplateUsed(response, "economy/economy_home.html")

    # Use this as boilerplate when error handling for invalid form is handled in view
    def test__economy_home_view_POST_request__renders_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(economy_home),
            urlencode(
                {
                    "amount": self.generic_deposit.amount,
                    "description": self.generic_deposit.description,
                    "receipt": self.generic_deposit.receipt,
                }
            ),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertTemplateUsed(response, "economy/economy_home.html")

    def test__economy_home_view_POST_request__saves_deposit_correctly_in_db(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse(economy_home),
            urlencode(
                {
                    "amount": self.deposit_POST_in_db.amount,
                    "receipt": self.deposit_POST_in_db.receipt,
                    "description": self.deposit_POST_in_db.description,
                }
            ),
            content_type="application/x-www-form-urlencoded",
        )

        deposit_from_db = Deposit.objects.filter(id=1437)[0]
        self.assertEqual(self.deposit_POST_in_db, deposit_from_db)

    def test__economy_home_view_POST_request__returns_status_code_200(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(economy_home),
            urlencode(
                {
                    "amount": self.generic_deposit.amount,
                    "description": self.generic_deposit.description,
                    "receipt": self.generic_deposit.receipt,
                }
            ),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(200, response.status_code)

    def test__economy_home_view_GET_request__returns_status_code_200(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse(viewname=economy_home))
        self.assertEqual(200, response.status_code)


class DepositsViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.bank_account = SociBankAccountFactory(user=self.user)

    def test__deposits_view__renders_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse(deposits))
        self.assertTemplateUsed(response, "economy/economy_deposits.html")

    def test__deposits_view__returns_status_code_200(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse(deposits))
        self.assertEqual(200, response.status_code)


class DepositDetailViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.bank_account = SociBankAccountFactory(user=self.user)
        self.user_deposit_no_comment = DepositFactory(account=self.bank_account)
        self.deposit_comment = DepositCommentFactory()
        self.deposit_ten_comments = DepositFactory()
        DepositCommentFactory.create_batch(10, deposit=self.deposit_ten_comments)
        self.deposit_ten_comments.save()

    def test__deposit_detail_view_GET_request__renders_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                deposit_detail, kwargs={"deposit_id": self.user_deposit_no_comment.id}
            )
        )
        self.assertTemplateUsed(response, "economy/economy_deposit_detail.html")

    def test__deposit_detail_view_POST_request__renders_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                deposit_detail, kwargs={"deposit_id": self.user_deposit_no_comment.id}
            ),
            urlencode({"comment": self.deposit_comment.comment}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertTemplateUsed(response, "economy/economy_deposit_detail.html")

    def test__deposit_detail_view_POST_deposit_comment__saves_comment_in_db(self):
        self.client.force_login(self.user)
        comments_before_POST = self.deposit_ten_comments.comments.count()
        response = self.client.post(
            reverse(
                deposit_detail, kwargs={"deposit_id": self.deposit_ten_comments.id}
            ),
            urlencode({"comment": self.deposit_comment}),
            content_type="application/x-www-form-urlencoded",
        )
        self.deposit_ten_comments.refresh_from_db()
        comments_after_POST = self.deposit_ten_comments.comments.count()
        self.assertEqual(1, comments_after_POST - comments_before_POST)

    def test__deposit_detail_view_GET_request__returns_status_code_200(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                deposit_detail, kwargs={"deposit_id": self.user_deposit_no_comment.id}
            )
        )
        self.assertEqual(200, response.status_code)

    def test__deposit_detail_view_POST_request__returns_status_code_200(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                deposit_detail, kwargs={"deposit_id": self.user_deposit_no_comment.id}
            ),
            urlencode({"comment": self.deposit_comment.comment}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(200, response.status_code)


class DepositEditViewTest(TestCase):
    def setUp(self):
        self.deposit_user = UserFactory()
        self.bank_account = SociBankAccountFactory(user=self.deposit_user)
        self.deposit = DepositFactory(
            account=self.deposit_user.bank_account,
            amount=420,
            description="lol vipps uten gebyr",
        )
        self.deposit_GET_request = DepositFactory(
            account=self.deposit_user.bank_account, amount=1337
        )
        self.deposit_POST_request = DepositFactory()

    def test__deposit_edit_view_POST_request__changes_are_saved(self):
        self.client.force_login(self.deposit_user)
        self.client.post(
            reverse(deposit_edit, kwargs={"deposit_id": self.deposit.id}),
            urlencode({"amount": 400}),
            content_type="application/x-www-form-urlencoded",
        )
        self.deposit.refresh_from_db()
        self.assertEqual(400, self.deposit.amount)

    def test__deposit_edit_view_GET_request__returns_correct_instance_values(self):
        self.client.force_login(self.deposit_user)
        response = self.client.get(
            reverse(deposit_edit, kwargs={"deposit_id": self.deposit_GET_request.id})
        )
        response_deposit = response.context["deposit"]
        self.assertEqual(self.deposit_GET_request, response_deposit)

    def test__deposit_edit_view_GET_request__returns_correct_template(self):
        self.client.force_login(self.deposit_user)
        response = self.client.get(
            reverse(deposit_edit, kwargs={"deposit_id": self.deposit_GET_request.id})
        )
        self.assertTemplateUsed(
            response, template_name="economy/economy_deposit_edit.html"
        )

    def test__deposit_edit_view_POST_request__correct_redirect(self):
        self.client.force_login(self.deposit_user)
        response = self.client.post(
            reverse(deposit_edit, kwargs={"deposit_id": self.deposit_POST_request.id}),
            urlencode({"amount": self.deposit_POST_request.amount}),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertRedirects(response, reverse(economy_home))
