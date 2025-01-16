# from langchain_core.tools import tool
# from .models import Product

# # Tool to create a product
# @tool(name="create_product", description="Create a new product")
# def create_product(name: str, price: float) -> str:
#     """Create a new product."""
#     product = Product(name=name, price=price)
#     product.save()
#     return f"Product '{product.name}' created successfully."

# # Tool to read a product
# @tool(name="read_product", description="Retrieve a product by its ID")
# def read_product(product_id: int) -> str:
#     """Retrieve a product by its ID."""
#     try:
#         product = Product.objects.get(id=product_id)
#         return f"Product ID: {product.id}, Name: {product.name}, Price: {product.price}"
#     except Product.DoesNotExist:
#         return f"Product with ID {product_id} does not exist."

# # Tool to update a product
# @tool(name="update_product", description="Update an existing product")
# def update_product(product_id: int, name: str, price: float) -> str:
#     """Update an existing product."""
#     try:
#         product = Product.objects.get(id=product_id)
#         product.name = name
#         product.price = price
#         product.save()
#         return f"Product '{product.name}' updated successfully."
#     except Product.DoesNotExist:
#         return f"Product with ID {product_id} does not exist."

# # Tool to delete a product
# @tool(name="delete_product", description="Delete a product by its ID")
# def delete_product(product_id: int) -> str:
#     """Delete a product by its ID."""
#     try:
#         product = Product.objects.get(id=product_id)
#         product.delete()
#         return f"Product '{product.name}' deleted successfully."
#     except Product.DoesNotExist:
#         return f"Product with ID {product_id} does not exist."

# # Tool to list all products
# @tool(name="list_products", description="List all products")
# def list_products() -> str:
#     """List all products."""
#     products = Product.objects.all()
#     if not products:
#         return "No products found."
    
#     product_list = "\n".join([f"ID: {p.id}, Name: {p.name}, Price: {p.price}" for p in products])
#     return f"Products:\n{product_list}"
