from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Sales(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class SalesItem(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Thread(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ThreadMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    content = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Checkpoint(models.Model):
    thread_id = models.IntegerField(null=True, blank=True)
    checkpoint_ns = models.TextField(default="")
    checkpoint_id = models.TextField(primary_key=True)
    parent_checkpoint_id = models.TextField(null=True, blank=True)
    type = models.TextField()
    checkpoint = models.BinaryField(null=True, blank=True)
    metadata = models.BinaryField(null=True, blank=True)


    def __str__(self):
        return f"{self.checkpoint_id} (Version: {self.version})"
    
    

