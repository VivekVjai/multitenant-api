from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    SELLER = "SELLER", _("Seller")
    CUSTOMER = "CUSTOMER", _("Customer")


class User(AbstractUser):
    
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
    )

    def clean(self):
        super().clean()
