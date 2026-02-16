from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import UserRole
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class TenantScopedQuerysetMixin:
    
    def filter_queryset_by_tenant(self, queryset):
        user = self.request.user

        if user.role == UserRole.ADMIN:
            return queryset

        return queryset.filter(tenant=user.tenant)


class CategoryViewSet(TenantScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Category.objects.all()
        return self.filter_queryset_by_tenant(qs)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)


class ProductViewSet(TenantScopedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Product.objects.filter(is_deleted=False)
        return self.filter_queryset_by_tenant(qs)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
