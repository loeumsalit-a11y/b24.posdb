import os
import django

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posdb.settings')
django.setup()

from sales.models import Product, Order, OrderItem, Discount

def main():
    # Delete existing data to start fresh (optional, but safe for testing)
    Discount.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Product.objects.all().delete()

    print("--- 1. SEED INITIAL PRODUCTS ---")
    coffee = Product.objects.create(name='កាហ្វេ Espresso', category='food', price=1.50, stock=100, barcode='FOOD-001')
    sandwich = Product.objects.create(name='នំប៉័ង Club', category='food', price=3.99, stock=20, barcode='FOOD-002')
    headphones = Product.objects.create(name='កាស Wireless', category='electronics', price=49.99, stock=15, barcode='ELEC-001')
    charger = Product.objects.create(name='ខ្សែសាក USB-C', category='electronics', price=9.99, stock=4, barcode='ELEC-002')

    print("--- TASK 1: ADD 4 MORE PRODUCTS ---")
    mouse = Product.objects.create(name='Mouse ឥតខ្សែ', category='electronics', price=12.50, stock=50, barcode='ELEC-003')
    tshirt = Product.objects.create(name='អាវយឺត', category='clothing', price=8.00, stock=100, barcode='CLOTH-001')
    jeans = Product.objects.create(name='ខោខូវប៊យ', category='clothing', price=25.00, stock=30, barcode='CLOTH-002')
    water = Product.objects.create(name='ទឹកបរិសុទ្ធ', category='food', price=0.50, stock=200, barcode='FOOD-003')
    
    print("--- CREATE AN INITIAL ORDER (For OrderItem test) ---")
    order1 = Order.objects.create(cashier='សុភា', status='paid')
    OrderItem.objects.create(order=order1, product=coffee, quantity=2, unit_price=coffee.price)
    OrderItem.objects.create(order=order1, product=sandwich, quantity=1, unit_price=sandwich.price)

    print("\n--- TASK 2: ORM PRACTICE ANSWERS ---")
    ans1 = Product.objects.count()
    ans2_qs = Product.objects.filter(category='electronics').order_by('price')
    ans2 = ", ".join([f"{p.name} (${p.price})" for p in ans2_qs])
    ans3_qs = Product.objects.filter(stock__lte=10)
    ans3 = ", ".join([f"{p.name} (ស្តុក: {p.stock})" for p in ans3_qs])
    ans4 = Order.objects.filter(status='paid').count()
    ans5_items = OrderItem.objects.filter(order__pk=order1.pk)
    ans5 = ", ".join([f"{item.product.name}: ${item.subtotal}" for item in ans5_items])

    print(f"1: {ans1}")
    print(f"2: {ans2}")
    print(f"3: {ans3}")
    print(f"4: {ans4}")
    print(f"5: {ans5}")

    print("\n--- TASK 4: ADD A NEW ORDER VIA ADMIN (Simulated) ---")
    order2 = Order.objects.create(cashier='Admin', status='paid')
    OrderItem.objects.create(order=order2, product=headphones, quantity=1, unit_price=headphones.price)
    OrderItem.objects.create(order=order2, product=mouse, quantity=2, unit_price=mouse.price)
    print(f"Order #{order2.pk} total (before discount): ${order2.total}")

    print("\n--- TASK 6: BONUS CHALLENGE (DISCOUNT) ---")
    Discount.objects.create(order=order2, description='ការបញ្ចុះតម្លៃពិសេស', amount=5.00)
    # Reload order to check the property (it should calculate dynamically anyway)
    print(f"Order #{order2.pk} total (after $5.00 discount): ${order2.total}")

    print("\n--- TASK 5: DEACTIVATE A PRODUCT ---")
    p = Product.objects.get(barcode='FOOD-003')
    p.is_active = False
    p.save()
    print("Product FOOD-003 deactivated.")

if __name__ == '__main__':
    main()
