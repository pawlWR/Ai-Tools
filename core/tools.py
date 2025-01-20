from langchain_core.tools import tool
from .models import Product, Sales, SalesItem

@tool
def create_product(name: str, price: float) -> str:
    """
    Creates a product with the given name and price, handling potential errors.

    Args:
        name (str): The name of the product.
        price (float): The price of the product.

    Returns:
        str: A success message if the product is created, or an error message.
    """
    try:
        product = Product(name=name, price=price)
        product.save()
        return f"Product '{product.name}' created successfully."
    except Exception as e:
        return f"Error creating product: {str(e)}"

@tool
def create_sales_with_items(name: str) -> str:
    """
    Creates a sale with the given name.

    Args:
        name (str): The name of the customer.

    Returns:
        str: A success message if the sale is created, or an error message.
    """
    try:
        sales = Sales(name=name)
        sales.save()
        return f"Sales '{sales.name}' created successfully."
    except Exception as e:
        return f"Error creating sales: {str(e)}"
    
# @tool
# def list_products() -> str:
#     """
#     Lists all products, formatting the output for better readability.

#     Returns:
#         str: A formatted list of products or a message if no products are found.
#     """
#     products = Product.objects.all()
#     if not products:
#         return "No products found."

#     product_list = []
#     for product in products:
#         product_list.append(f"- {product.name} (Price: ${product.price:.2f})")

#     return "\n".join(product_list)



# @tool
# def list_sales_with_items() -> str:
#     """
#     Lists all sales, including customer details and product information for each sale item.

#     Returns:
#         str: A formatted list of sales or a message if no sales are found.
#     """
#     sales = Sales.objects.all()
#     if not sales:
#         return "No sales found."

#     sales_list = []
#     for sale in sales:
#         sales_items = SalesItem.objects.filter(sales=sale).values_list('product__name', 'quantity')
#         items_str = ", ".join([f"{name} x {quantity}" for name, quantity in sales_items])
#         sales_list.append(f"- {sale.name} (Email: {sale.email}, Phone: {sale.phone}, Address: {sale.address}): Items: {items_str if items_str else 'No items'}")

#     return "\n".join(sales_list)