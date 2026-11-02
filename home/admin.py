from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    QuizQuestion,
    ShortAnswerQuestion,
)


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'topic', 'position']
    list_editable = ['position']
    list_filter = ['topic']
    search_fields = ['prompt', 'topic']


@admin.register(ShortAnswerQuestion)
class ShortAnswerQuestionAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'position']
    list_editable = ['position']
    search_fields = ['prompt']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_active']
    list_filter = ['is_active', 'category']
    list_editable = ['price', 'stock', 'is_active']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name', 'description']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'price', 'quantity']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['user__username', 'full_name', 'postal_code']
    inlines = [OrderItemInline]
    readonly_fields = ['user', 'total', 'created_at']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'updated_at']
    inlines = [CartItemInline]
