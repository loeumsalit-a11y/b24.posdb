# sales/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem, Discount

@login_required
def order_detail(request, pk):
    """បង្ហាញព័ត៌មានលម្អិតនៃការបញ្ជាទិញ និងទំនិញក្នុងនោះ"""
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()
    return render(request, 'sales/order_detail.html', {'order': order, 'items': items})



from django.db.models import Sum, Q
from django.utils import timezone

@login_required
def dashboard(request):
    """បង្ហាញស្ថិតិសំខាន់ៗលើ Dashboard"""
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_products = Product.objects.filter(is_active=True, stock__lte=10).count()
    total_orders = Order.objects.count()
    
    # សរុបទឹកប្រាក់លក់បាន (Paid orders)
    paid_orders = Order.objects.filter(status='paid')
    total_revenue = sum(order.total for order in paid_orders)
    
    # ការបញ្ជាទិញថ្មីៗ ៥
    recent_orders = Order.objects.order_by('-created_at')[:5]

    # Data for Charts
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models.functions import TruncDate

    last_7_days = timezone.now().date() - timedelta(days=6)
    daily_sales = Order.objects.filter(status='paid', created_at__date__gte=last_7_days) \
        .annotate(date=TruncDate('created_at')) \
        .values('date') \
        .annotate(total=Sum('items__unit_price')) \
        .order_by('date')

    top_products = OrderItem.objects.values('product__name') \
        .annotate(total_qty=Sum('quantity')) \
        .order_by('-total_qty')[:5]
    
    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'daily_sales_json': list(daily_sales),
        'top_products_json': list(top_products),
    }
    return render(request, 'sales/dashboard.html', context)


@login_required
def product_list(request):
    """បង្ហាញផលិតផល active ទាំងអស់ ជាមួយមុខងារស្វែងរក និង Filter តាមប្រភេទ"""
    query = request.GET.get('q')
    category = request.GET.get('cat')
    
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(barcode__icontains=query)
        )
    
    if category:
        products = products.filter(category=category)
        
    return render(request, 'sales/product_list.html', {
        'products': products, 
        'query': query,
        'selected_category': category,
        'categories': Product.CATEGORY_CHOICES
    })



@login_required
def product_detail(request, pk):
    """បង្ហាញព័ត៌មានលម្អិតសម្រាប់ផលិតផលតែមួយ"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sales/product_detail.html', {'product': product})


@login_required
def order_list(request):
    """បង្ហាញការបញ្ជាទិញទាំងអស់"""
    orders = Order.objects.all()
    return render(request, 'sales/order_list.html', {'orders': orders})


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def checkout(request):
    """ទំព័រសម្រាប់រើសទំនិញ និងចេញវិក្កយបត្រ"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            cashier_name = data.get('cashier', 'Anonymous')
            
            if not cart:
                return JsonResponse({'success': False, 'error': 'Cart is empty'})
            
            # 1. បង្កើត Order
            order = Order.objects.create(cashier=cashier_name, status='paid')
            
            # 2. បង្កើត OrderItems
            for item in cart:
                product = Product.objects.get(pk=item['id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    unit_price=product.price
                )
                # ដកស្តុក
                product.stock -= item['quantity']
                product.save()
            
            return JsonResponse({'success': True, 'order_id': order.pk})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    products = Product.objects.filter(is_active=True, stock__gt=0)
    return render(request, 'sales/checkout.html', {'products': products})
