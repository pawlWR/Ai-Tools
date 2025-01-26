from core.models import Sales, SalesItem, Product
from django.db import IntegrityError
from django.db.models import ProtectedError
from langchain_core.tools import tool
from django.db.models import Q



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
    
@tool
def create_sales(name: str, email: str, phone: str, address: str) -> str:
    """Creates a new sales record."""
    try:
        sales = Sales.objects.create(name=name, email=email, phone=phone, address=address)
        return f"Sales record created successfully with ID: {sales.id}"
    except Exception as e:
        return f"Error creating sales record: {e}"

@tool
def update_sales(sales_id: int, name: str = None, email: str = None, phone: str = None, address: str = None) -> str:
    """Updates an existing sales record."""
    try:
        sales = Sales.objects.get(id=sales_id)
        if name:
            sales.name = name
        if email:
            sales.email = email
        if phone:
            sales.phone = phone
        if address:
            sales.address = address
        sales.save()
        return f"Sales record with ID {sales_id} updated successfully."
    except Sales.DoesNotExist:
        return f"Sales record with ID {sales_id} not found."
    except Exception as e:
        return f"Error updating sales record: {e}"

@tool
def delete_sales(sales_id: int) -> str:
    """Deletes a sales record. Deletes associated SalesItems due to CASCADE."""
    try:
        sales = Sales.objects.get(id=sales_id)
        sales.delete()
        return f"Sales record with ID {sales_id} and associated items deleted successfully."
    except Sales.DoesNotExist:
        return f"Sales record with ID {sales_id} not found."
    except ProtectedError as e:
        return f"Cannot delete sales record with ID {sales_id} because it is protected: {e}"
    except Exception as e:
        return f"Error deleting sales record: {e}"


@tool
def create_sales_item(sales_id: int, product_id: int, quantity: int) -> str:
    """Creates a new sales item associated with a sales record."""
    try:
        sales = Sales.objects.get(id=sales_id)
        product = Product.objects.get(id=product_id)
        if quantity < 1:
            return "Quantity must be at least 1."
        SalesItem.objects.create(sales=sales, product=product, quantity=quantity)
        return f"Sales item created successfully for Sales ID {sales_id}, Product ID {product_id}."
    except Sales.DoesNotExist:
        return f"Sales record with ID {sales_id} not found."
    except Product.DoesNotExist:
        return f"Product with ID {product_id} not found."
    except IntegrityError as e:
        return f"Integrity Error creating sales item: {e}"
    except Exception as e:
        return f"Error creating sales item: {e}"

@tool
def update_sales_item(sales_item_id: int, quantity: int = None, sales_id: int = None, product_id: int = None) -> str:
    """Updates an existing sales item."""
    try:
        sales_item = SalesItem.objects.get(id=sales_item_id)
        if quantity is not None:
            if quantity < 1:
                return "Quantity must be at least 1."
            sales_item.quantity = quantity
        if sales_id:
            sales = Sales.objects.get(id=sales_id)
            sales_item.sales = sales
        if product_id:
            product = Product.objects.get(id=product_id)
            sales_item.product = product
        sales_item.save()
        return f"Sales item with ID {sales_item_id} updated successfully."
    except SalesItem.DoesNotExist:
        return f"Sales item with ID {sales_item_id} not found."
    except Sales.DoesNotExist:
        return f"Sales record with ID {sales_id} not found."
    except Product.DoesNotExist:
        return f"Product with ID {product_id} not found."
    except Exception as e:
        return f"Error updating sales item: {e}"

@tool
def delete_sales_item(sales_item_id: int) -> str:
    """Deletes a sales item."""
    try:
        sales_item = SalesItem.objects.get(id=sales_item_id)
        sales_item.delete()
        return f"Sales item with ID {sales_item_id} deleted successfully."
    except SalesItem.DoesNotExist:
        return f"Sales item with ID {sales_item_id} not found."
    except Exception as e:
        return f"Error deleting sales item: {e}"

@tool
def list_sales(sales_id: int = None) -> str:
    """Lists sales records. If sales_id is provided, lists only that record."""
    try:
        if sales_id:
            sales = Sales.objects.get(id=sales_id)
            return str(sales)
        else:
            sales_list = Sales.objects.all()
            if sales_list:
                return "\n".join([str(sale) for sale in sales_list])
            else:
                return "No sales records found."
    except Sales.DoesNotExist:
        return f"Sales record with ID {sales_id} not found."
    except Exception as e:
        return f"Error listing sales records: {e}"

@tool
def list_sales_detailed(sales_id: int = None) -> str:
    """Lists sales records with more detail, including associated SalesItems."""
    try:
        if sales_id:
            sales = Sales.objects.get(id=sales_id)
            sales_items = SalesItem.objects.filter(sales=sales)
            items_str = "\n".join([f"  - {item.product.name} x {item.quantity}" for item in sales_items])
            return f"Sales ID: {sales.id}\nName: {sales.name}\nEmail: {sales.email}\nItems:\n{items_str}"
        else:
            sales_list = Sales.objects.all()
            output = ""
            for sales in sales_list:
                sales_items = SalesItem.objects.filter(sales=sales)
                items_str = "\n".join([f"  - {item.product.name} x {item.quantity}" for item in sales_items])
                output += f"Sales ID: {sales.id}\nName: {sales.name}\nEmail: {sales.email}\nItems:\n{items_str}\n\n"
            return output if output else "No sales records found."
    except Sales.DoesNotExist:
        return f"Sales record with ID {sales_id} not found."
    except Exception as e:
        return f"Error listing sales records: {e}"