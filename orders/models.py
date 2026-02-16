from django.db import models
from django.conf import settings
from catalog.models import Product
from accounts.models import Tenant


class OrderStatus(models.TextChoices):
    CREATED = "CREATED", "Created"
    PAID = "PAID", "Paid"
    SHIPPED = "SHIPPED", "Shipped"
    CANCELLED = "CANCELLED", "Cancelled"


class Order(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, related_name="orders")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")

    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.CREATED)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "created_at"]),
            models.Index(fields=["tenant", "status"]),
        ]

    def __str__(self):
        return f"Order#{self.id} ({self.status})"

    def can_transition_to(self, new_status: str) -> bool:
        valid_transitions = {
            OrderStatus.CREATED: [OrderStatus.PAID, OrderStatus.CANCELLED],
            OrderStatus.PAID: [OrderStatus.SHIPPED], 
            OrderStatus.SHIPPED: [],
            OrderStatus.CANCELLED: [],
        }

        return new_status in valid_transitions.get(self.status, [])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=100)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
