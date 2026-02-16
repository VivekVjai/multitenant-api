import os
import logging

from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from orders.models import OrderStatus
from .models import Payment, PaymentStatus


logger = logging.getLogger(__name__)

class MockPaymentWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):

        received_secret = request.headers.get("X-WEBHOOK-SECRET")
        expected_secret = os.getenv("PAYMENT_WEBHOOK_SECRET")

        if received_secret != expected_secret:
            
            logger.warning("Webhook rejected: invalid secret")
            return Response({"detail": "Invalid webhook secret"}, status=403)

        reference_id = request.data.get("reference_id")
        payment_status = request.data.get("status")

        if not reference_id or payment_status not in ["SUCCESS", "FAILED"]:
            logger.warning(
                "Webhook rejected: invalid payload",
                extra={"reference_id": reference_id, "status": payment_status},
            )
            return Response({"detail": "Invalid payload"}, status=400)

        
        logger.info(
            "Webhook received",
            extra={"reference_id": reference_id, "status": payment_status},
        )

        with transaction.atomic():
            payment = (
                Payment.objects
                .select_for_update()      
                .select_related("order")  
                .filter(reference_id=reference_id)
                .first()
            )

            if not payment:
                return Response({"detail": "Payment not found"}, status=404)

            if payment.status == PaymentStatus.SUCCESS:
                return Response({"message": "Already processed"}, status=200)

            payment.status = payment_status
            payment.save(update_fields=["status"])

            order = payment.order

            if payment_status == "SUCCESS":
                order.status = OrderStatus.PAID
                order.save(update_fields=["status"])

            elif payment_status == "FAILED":

                pass

        return Response(
            {
                "message": "Webhook processed",
                "order_id": payment.order.id,
                "order_status": payment.order.status,
                "payment_status": payment.status,
            },
            status=status.HTTP_200_OK,
        )
