# Product Management Agent Testing Prompts

## List Products

* "List all products." (Basic listing)
* "What products do you have?" (Alternative phrasing)
* "Show me the product catalog." (Another alternative)

## Create Product

* "Create a product named 'Wireless Mouse' with a price of 25.99." (Standard creation)
* "Add a new product: name 'Keyboard', price 79.50." (Alternative phrasing)
* "I want to create a product. Name: Monitor, Price: 299.00" (Another alternative)
* "Create a product named 'Negative Price Test' with a price of -10." (Test for negative price handling)
* "Create product name 'Test product with very very very very very very very long name' price 10" (Test for long name handling)

## Update Product

* "Update product with ID 1 to have the name 'Gaming Mouse' and a price of 39.99." (Update both name and price)
* "Change the price of product ID 2 to 99.00." (Update only price)
* "Rename product ID 3 to 'Office Keyboard'." (Update only name)
* "Update product with id 999 to have name 'Test'" (Test for non-existent product ID)
* "Update product with ID 1 to have price -10" (Test for negative price update)

## Delete Product

* "Delete product with ID 4." (Delete by ID)
* "Remove the product named 'Wireless Mouse'." (Delete by name)
* "Delete the product named 'Non Existent Product'" (Test for non-existent product name)
* "Delete the product named 'test product with very very very very very very very long name'" (Test for long name deletion)

## Bulk Create Products

* "Bulk create products: 'Laptop,1200.00;Tablet,350.50;Printer,199.99'." (Standard bulk creation)
* "Create these products: 'Product A,10;Product B,20;Product C,30'" (Alternative phrasing)
* "Bulk create products: 'Invalid Input'" (Test for invalid input format)
* "Bulk create products: 'Product With Negative Price,-10'" (Test for negative price in bulk creation)
* "Bulk create products: 'Product A,10;Product B,20;Product C,30;Product A,40'" (Test for duplicate product names)

## Bulk Delete Products

* "Bulk delete products: 'Laptop,Printer'." (Standard bulk deletion)
* "Remove these products: 'Tablet,Monitor'." (Alternative phrasing)
* "Bulk delete products: 'Nonexistent Product 1,Nonexistent Product 2'." (Test for non-existent product names)
* "Bulk delete products: 'Laptop,Laptop'" (Test for duplicate product names)



# Sales Management Agent Testing Prompts

## Create Sales

- "Create a sales record for John Doe, email john@email.com, phone 555-123-4567, address 123 Main St." (Standard creation)
- "Add a new sale: Name Jane Smith, Email jane@email.com, Phone 555-987-6543, Address 456 Oak Ave" (Alternative phrasing)
- "I need to create a sale for Bob Johnson, bob@email.com, 555-111-2222, 789 Pine Ln" (Another alternative)
- "Create a sales record for , , , " (Test for empty input)

## Update Sales

- "Update sales record with ID 1. Change the address to 999 Elm St." (Update single field)
- "Update sales ID 2. Name: Alice Lee, Email: [email address removed], Phone: 555-333-4444" (Update multiple fields)
- "Update sales with id 999. Name Test" (Test for non-existent ID)
- "Update sales ID 1" (Test for no fields to update)

## Delete Sales

- "Delete sales record with ID 3." (Standard deletion)
- "Remove sales with ID 5" (Alternative phrasing)
- "Delete sales with ID 999" (Test for non-existent ID)

## Create Sales Item

- "Create a sales item for sales ID 1, product ID 2, quantity 3." (Standard creation)
- "Add an item to sales ID 4: Product ID 6, Quantity 1." (Alternative phrasing)
- "Create sales item for sales ID 999, product ID 1, quantity 1" (Test for non-existent sales ID)
- "Create sales item for sales ID 1, product ID 999, quantity 1" (Test for non-existent product ID)
- "Create sales item for sales ID 1, product ID 1, quantity -1" (Test for negative quantity)
- "Create sales item for sales ID 1, product ID 1, quantity 0" (Test for zero quantity)

## Update Sales Item

- "Update sales item with ID 7. Change the quantity to 5." (Update single field)
- "Update sales item ID 8: Sales ID 9, Product ID 10." (Update related IDs)
- "Update sales item with ID 999. Quantity 1" (Test for non-existent sales item ID)
- "Update sales item with ID 1. Quantity -1" (Test for negative quantity)
- "Update sales item with ID 1. Quantity 0" (Test for zero quantity)
- "Update sales item with ID 1" (Test for no fields to update)

## Delete Sales Item

- "Delete sales item with ID 11." (Standard deletion)
- "Remove sales item ID 12." (Alternative phrasing)
- "Delete sales item with ID 999" (Test for non-existent sales item ID)

## List Sales

- "List all sales." (Basic list)
- "Show me the sales records." (Alternative phrasing)
- "List sales with ID 1." (List specific sales record)
- "List sales with ID 999" (Test for non-existent sales ID)

## List Sales Detailed

- "List all sales with details." (Detailed list)
- "Show me the detailed sales information." (Alternative phrasing)
- "List detailed sales for ID 2." (List specific sales record with details)
- "List detailed sales for ID 999" (Test for non-existent sales ID)
