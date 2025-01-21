from langchain_core.tools import tool
from .models import Product, Sales, SalesItem
from typing import List, Dict,Any

@tool
def create_product(name: str, price: float) -> Dict[str, Any]:
    """Creates a product with the given name and price."""
    if price < 0:
        return {"success": False, "message": "Error: Price cannot be negative."}

    try:
        product = Product(name=name, price=price)
        product.save()
        return {
            "success": True,
            "message": f"Product {product.name} created successfully with price ${price:.2f}.",
            "product_id": product.id,
            "product_name": product.name
        }
    except Exception as e:
        return {"success": False, "message": f"Error creating product: {str(e)}"}

def create_sales_with_items(name: str, items: List[str] = []) -> Dict[str, Any]:
    """Creates a sale with specified items.

    Args:
        name (str): The name associated with the sale.
        items (List[str], optional): A list of item names to include in the sale. Defaults to an empty list.

    Returns:
        Dict[str, Any]: A dictionary containing the success status, message, and sale ID.
    """
    # Validate input
    if not name:
        return {
            "success": False,
            "message": "Sale name cannot be empty.",
            "sale_id": None,
        }
    
    # Create the sales record
    sale = Sales(name=name)
    sale.save()

    # Initialize a list to track added items
    added_items = []

    if items:
        for item_name in items:
            product = Product.objects.filter(name__iexact=item_name).first()
            if product:
                SalesItem.objects.create(sales=sale, product=product)
                added_items.append(item_name)
            else:
                print(f"Warning: Product '{item_name}' not found.")

    return {
        "success": True,
        "message": f"Sale created successfully for '{name}'" +
                   (f" with items: {', '.join(added_items)}." if added_items else "."),
        "sale_id": sale.id,
    }

@tool
def list_products() -> str:
    """Lists all products."""
    products = Product.objects.all()
    if not products:
        return "No products found."

    product_list = [f"- {product.name} (Price: ${product.price:.2f})" for product in products]
    return "\n".join(product_list)


