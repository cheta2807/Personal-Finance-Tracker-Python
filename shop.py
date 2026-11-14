price_jeans= 400
price_shirt= 500

qty_jeans = 5
qty_shirt = 4

total_jeans = price_jeans * qty_jeans
total_shirt = price_shirt * qty_shirt

subtotal = total_jeans + total_shirt
print("subtotal",subtotal)

Discount = subtotal * 0.10
print("Discount",Discount)

Final_total = subtotal - Discount
print("Final_total",Final_total)