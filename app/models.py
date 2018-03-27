# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Brand(models.Model):
	brand_id = models.AutoField(primary_key=True)
	category = models.ForeignKey('Category', models.DO_NOTHING)
	brand_name = models.CharField(max_length=250)
	brand_status = models.CharField(max_length=8)

	class Meta:
		managed = False
		db_table = 'brand'


class Category(models.Model):
	category_id = models.AutoField(primary_key=True)
	category_name = models.CharField(max_length=250)
	category_status = models.CharField(max_length=8)

	class Meta:
		managed = False
		db_table = 'category'


class Order(models.Model):
	inventory_order_id = models.AutoField(primary_key=True)
	user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
	inventory_order_total = models.FloatField()
	inventory_order_date = models.DateField()
	inventory_order_name = models.CharField(max_length=255)
	inventory_order_address = models.TextField()
	payment_status = models.CharField(max_length=6)
	inventory_order_status = models.CharField(max_length=100)
	inventory_order_created_date = models.DateField()

	class Meta:
		managed = False
		db_table = 'order'


class OrderProduct(models.Model):
	inventory_order_product_id = models.AutoField(primary_key=True)
	inventory_order = models.ForeignKey(Order, models.DO_NOTHING)
	product = models.ForeignKey('Product', models.DO_NOTHING)
	quantity = models.IntegerField()
	price = models.FloatField()
	tax = models.FloatField()

	class Meta:
		managed = False
		db_table = 'order_product'


class Product(models.Model):
	product_id = models.AutoField(primary_key=True)
	category = models.ForeignKey(Category, models.DO_NOTHING)
	brand = models.ForeignKey(Brand, models.DO_NOTHING)
	product_name = models.CharField(max_length=300)
	product_description = models.TextField()
	product_quantity = models.IntegerField()
	product_unit = models.CharField(max_length=150)
	product_base_price = models.FloatField()
	product_tax = models.DecimalField(max_digits=4, decimal_places=2)
	product_minimum_order = models.FloatField()
	product_enter_by = models.IntegerField()
	product_status = models.CharField(max_length=8)
	product_date = models.DateField()

	class Meta:
		managed = False
		db_table = 'product'


#User model
class User(models.Model):
	user_id = models.AutoField(primary_key=True)
	user_email = models.CharField(max_length=200)
	user_password = models.CharField(max_length=200)
	user_name = models.CharField(max_length=200)
	user_type = models.CharField(max_length=6)
	user_status = models.CharField(max_length=8)


	class Meta:
		managed = False
		db_table = 'user'
