import uuid
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.models import UserRole
from orders.models import Order, OrderStatus
from .models import Payment, PaymentStatus


class MockPaymentView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user = request.user

        if user.role != UserRole.CUSTOMER:
            return Response({"detail": "Only customers can pay."}, status=403)

        order = Order.objects.filter(id=order_id, customer=user).first()
        if not order:
            return Response({"detail": "Order not found."}, status=404)

        if order.status != OrderStatus.CREATED:
            return Response({"detail": f"Order cannot be paid from status {order.status}."}, status=400)

        payment, created = Payment.objects.get_or_create(order=order)

        if payment.status == PaymentStatus.SUCCESS:
            return Response({"detail": "Order already paid."}, status=400)

        payment.reference_id = str(uuid.uuid4())
        payment.status = PaymentStatus.PENDING
        payment.save(update_fields=["reference_id", "status"])

        return Response(
            {
                "message": "Mock payment initiated",
                "order_id": order.id,
                "payment_status": payment.status,
                "reference_id": payment.reference_id,
            },
            status=status.HTTP_200_OK,
        )
