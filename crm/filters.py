import django_filters
from django.db import models
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    # Case-insensitive partial match for name
    name_icontains = django_filters.CharFilter(
        field_name='name', 
        lookup_expr='icontains',
        help_text="Case-insensitive partial match for customer name"
    )
    
    # Case-insensitive partial match for email
    email_icontains = django_filters.CharFilter(
        field_name='email', 
        lookup_expr='icontains',
        help_text="Case-insensitive partial match for email"
    )
    
    # Date range filters for created_at
    created_at_gte = django_filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='gte',
        help_text="Filter customers created on or after this date"
    )
    
    created_at_lte = django_filters.DateTimeFilter(
        field_name='created_at', 
        lookup_expr='lte',
        help_text="Filter customers created on or before this date"
    )
    
    # Custom filter for phone pattern (starts with +1)
    phone_pattern = django_filters.CharFilter(
        method='filter_phone_pattern',
        help_text="Filter customers by phone pattern (e.g., '+1' for US numbers)"
    )

    class Meta:
        model = Customer
        fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'phone': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'],
        }

    def filter_phone_pattern(self, queryset, name, value):
        """Custom method to filter by phone pattern"""
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset


class ProductFilter(django_filters.FilterSet):
    # Case-insensitive partial match for name
    name_icontains = django_filters.CharFilter(
        field_name='name', 
        lookup_expr='icontains',
        help_text="Case-insensitive partial match for product name"
    )
    
    # Price range filters
    price_gte = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='gte',
        help_text="Filter products with price greater than or equal to this value"
    )
    
    price_lte = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='lte',
        help_text="Filter products with price less than or equal to this value"
    )
    
    # Stock range filters
    stock_gte = django_filters.NumberFilter(
        field_name='stock', 
        lookup_expr='gte',
        help_text="Filter products with stock greater than or equal to this value"
    )
    
    stock_lte = django_filters.NumberFilter(
        field_name='stock', 
        lookup_expr='lte',
        help_text="Filter products with stock less than or equal to this value"
    )
    
    # Low stock filter (custom method)
    low_stock = django_filters.BooleanFilter(
        method='filter_low_stock',
        help_text="Filter products with low stock (less than 10)"
    )

    class Meta:
        model = Product
        fields = {
            'name': ['exact', 'icontains'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }

    def filter_low_stock(self, queryset, name, value):
        """Filter products with stock less than 10"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    # Total amount range filters
    total_amount_gte = django_filters.NumberFilter(
        field_name='total_amount', 
        lookup_expr='gte',
        help_text="Filter orders with total amount greater than or equal to this value"
    )
    
    total_amount_lte = django_filters.NumberFilter(
        field_name='total_amount', 
        lookup_expr='lte',
        help_text="Filter orders with total amount less than or equal to this value"
    )
    
    # Order date range filters
    order_date_gte = django_filters.DateTimeFilter(
        field_name='order_date', 
        lookup_expr='gte',
        help_text="Filter orders placed on or after this date"
    )
    
    order_date_lte = django_filters.DateTimeFilter(
        field_name='order_date', 
        lookup_expr='lte',
        help_text="Filter orders placed on or before this date"
    )
    
    # Filter by customer name (related field lookup)
    customer_name = django_filters.CharFilter(
        field_name='customer__name', 
        lookup_expr='icontains',
        help_text="Filter orders by customer name (case-insensitive partial match)"
    )
    
    # Filter by product name (related field lookup)
    product_name = django_filters.CharFilter(
        field_name='products__name', 
        lookup_expr='icontains',
        help_text="Filter orders containing products with this name"
    )
    
    # Filter orders that include a specific product ID
    product_id = django_filters.NumberFilter(
        field_name='products__id',
        help_text="Filter orders that include a specific product ID"
    )
    
    # Filter by customer email
    customer_email = django_filters.CharFilter(
        field_name='customer__email', 
        lookup_expr='icontains',
        help_text="Filter orders by customer email"
    )

    class Meta:
        model = Order
        fields = {
            'total_amount': ['exact', 'gte', 'lte'],
            'order_date': ['exact', 'gte', 'lte'],
            'customer__name': ['exact', 'icontains'],
            'customer__email': ['exact', 'icontains'],
            'products__name': ['exact', 'icontains'],
            'products__id': ['exact'],
        }