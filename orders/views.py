from decimal import Decimal
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.models import UserRole
from catalog.models import Product
from .models import Order, OrderItem, OrderStatus
from .serializers import OrderCreateSerializer, OrderSerializer


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        user = request.user
        qs = Order.objects.all().prefetch_related("items")

        if user.role == UserRole.ADMIN:
            return qs
        elif user.role == UserRole.SELLER:
            return qs.filter(tenant=user.tenant)
        else:
            return qs.filter(customer=user)

    def list(self, request):
        qs = self.get_queryset(request).order_by("-created_at")
        return Response(OrderSerializer(qs, many=True).data)

    def create(self, request):
        user = request.user

        if user.role != UserRole.CUSTOMER:
            return Response({"detail": "Only customers can create orders."}, status=403)

        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items = serializer.validated_data["items"]

        with transaction.atomic():
            product_ids = [i["product_id"] for i in items]

            products = (
                Product.objects.select_for_update()
                .filter(id__in=product_ids, is_deleted=False)
            )

            product_map = {p.id: p for p in products}

            if len(product_map) != len(product_ids):
                return Response({"detail": "One or more products not found."}, status=400)

            tenant = None
            total_amount = Decimal("0.00")

            for item in items:
                product = product_map[item["product_id"]]
                qty = item["quantity"]

                if tenant is None:
                    tenant = product.tenant
                elif product.tenant_id != tenant.id:
                    return Response(
                        {"detail": "You cannot order products from multiple sellers in one order."},
                        status=400,
                    )

                if product.stock < qty:
                    return Response(
                        {"detail": f"Not enough stock for product {product.name}"},
                        status=400,
                    )

            order = Order.objects.create(
                tenant=tenant,
                customer=user,
                status=OrderStatus.CREATED,
                total_amount=Decimal("0.00"),
            )

            for item in items:
                product = product_map[item["product_id"]]
                qty = item["quantity"]

                unit_price = product.price
                line_total = unit_price * qty
                total_amount += line_total

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    unit_price=unit_price,
                    quantity=qty,
                    line_total=line_total,
                )

                product.stock = product.stock - qty
                product.save(update_fields=["stock"])

            order.total_amount = total_amount
            order.save(update_fields=["total_amount"])

        order = Order.objects.prefetch_related("items").get(id=order.id)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        order = self.get_queryset(request).filter(id=pk).first()
        if not order:
            return Response({"detail": "Order not found."}, status=404)
        return Response(OrderSerializer(order).data)


    """@action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        order = self.get_queryset(request).filter(id=pk).first()
        if not order:
            return Response({"detail": "Order not found."}, status=404)

        if request.user.role != UserRole.CUSTOMER:
            return Response({"detail": "Only customers can pay orders."}, status=403)

        if not order.can_transition_to(OrderStatus.PAID):
            return Response({"detail": f"Cannot pay order from status {order.status}"}, status=400)

        order.status = OrderStatus.PAID
        order.save(update_fields=["status"])

        return Response(OrderSerializer(order).data"""

    @action(detail=True, methods=["post"])
    def ship(self, request, pk=None):
        order = self.get_queryset(request).filter(id=pk).first()
        if not order:
            return Response({"detail": "Order not found."}, status=404)

        if request.user.role not in [UserRole.SELLER, UserRole.ADMIN]:
            return Response({"detail": "Only sellers or admins can ship orders."}, status=403)

        if not order.can_transition_to(OrderStatus.SHIPPED):
            return Response({"detail": f"Cannot ship order from status {order.status}"}, status=400)

        order.status = OrderStatus.SHIPPED
        order.save(update_fields=["status"])

        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_queryset(request).filter(id=pk).first()
        if not order:
            return Response({"detail": "Order not found."}, status=404)

        if request.user.role == UserRole.CUSTOMER:
            if order.customer_id != request.user.id:
                return Response({"detail": "You cannot cancel someone else's order."}, status=403)
        elif request.user.role in [UserRole.SELLER, UserRole.ADMIN]:
            pass
        else:
            return Response({"detail": "Not allowed."}, status=403)

        if not order.can_transition_to(OrderStatus.CANCELLED):
            return Response({"detail": f"Cannot cancel order from status {order.status}"}, status=400)

        with transaction.atomic():
            order_items = OrderItem.objects.select_related("product").filter(order=order)

            for item in order_items:
                product = item.product
                product.stock = product.stock + item.quantity
                product.save(update_fields=["stock"])

            order.status = OrderStatus.CANCELLED
            order.save(update_fields=["status"])

        return Response(OrderSerializer(order).data)
