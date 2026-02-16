from django.db import models
from accounts.models import Tenant


class Category(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="categories")

    name = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "name")
        indexes = [
            models.Index(fields=["tenant", "name"]),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField(default=0)

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "sku")
        indexes = [
            models.Index(fields=["tenant", "sku"]),
            models.Index(fields=["tenant", "is_deleted"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"
