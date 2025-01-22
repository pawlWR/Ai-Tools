from langchain_core.tools import tool
from core.models import Sales, SalesItem, Product
from django.db import IntegrityError
from django.db.models import ProtectedError

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