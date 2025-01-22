from langchain_core.tools import tool
from core.models import Product
from django.db.models import Q
from django.core.validators import MinValueValidator

@tool
def list_products() -> str:
    """Lists all products in the database."""
    products = Product.objects.all()
    if not products:
        return "There are no products in the database."
    product_list = "\n".join([f"- {product.name} (Price: ${product.price:.2f})" for product in products])
    return f"**Product List:**\n{product_list}"

@tool
def create_product(name: str, price: float) -> str:
    """Creates a new product."""
    try:
        if price < 0:
            return "Error: Price cannot be negative."
        product = Product.objects.create(name=name, price=price)
        return f"Product '{product.name}' created successfully (ID: {product.id})."
    except Exception as e:
        return f"Error creating product: {e}"

@tool
def update_product(product_id: int, name: str = None, price: float = None) -> str:
    """Updates an existing product."""
    try:
        product = Product.objects.get(pk=product_id)
        if name:
            product.name = name
        if price is not None:  # Check if price is provided
            product.price = price
        product.save()
        return f"Product '{product.name}' (ID: {product.id}) updated successfully."
    except Product.DoesNotExist:
        return f"Product with ID {product_id} does not exist."
    except Exception as e:
        return f"Error updating product: {e}"

@tool
def delete_product(product_id: int = None, product_name: str = None) -> str:
    """Deletes an existing product by ID or name."""
    if not product_id and not product_name:
        return "Please provide either product_id or product_name to delete a product."

    try:
        if product_id:
            product = Product.objects.get(pk=product_id)
            product.delete()
            return f"Product with ID {product_id} deleted successfully."
        elif product_name:
            products = Product.objects.filter(Q(name__iexact=product_name))
            if products.exists():
                deleted_count, _ = products.delete()
                return f"{deleted_count} product(s) with name '{product_name}' deleted successfully."
            else:
                return f"No product found with name '{product_name}'."
    except Exception as e:
        return f"Error deleting product: {e}"


@tool
def bulk_create_products(products_data: str) -> str:
    """Creates multiple products from a comma-separated list of name and price pairs.
    Example input: "Product A,10.00;Product B,20.50;Product C,15.75"
    """
    try:
        products_list = []
        product_entries = products_data.split(';')
        for entry in product_entries:
            name, price_str = entry.split(',')
            name = name.strip()
            price = float(price_str.strip())
            if price < 0:
                return f"Error: Price for {name} cannot be negative."
            products_list.append(Product(name=name, price=price))

        Product.objects.bulk_create(products_list)
        return f"{len(products_list)} products created successfully."
    except ValueError:
        return "Invalid input format. Please use 'Name,Price;Name,Price;...' format."
    except Exception as e:
        return f"Error creating products: {e}"

@tool
def bulk_delete_products(product_names: str) -> str:
    """Deletes multiple products by name from a comma-separated list.
    Example input: "Product A,Product B,Product C"
    """
    try:
        names = [name.strip() for name in product_names.split(',')]
        deleted_count, _ = Product.objects.filter(name__in=names).delete()
        if deleted_count > 0:
            return f"{deleted_count} product(s) deleted successfully."
        else:
            return "No matching products found for deletion."
    except Exception as e:
        return f"Error deleting products: {e}"