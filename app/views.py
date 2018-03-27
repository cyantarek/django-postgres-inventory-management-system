from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from .models import Product, Brand, User, Category
from django.contrib.auth import login, logout, authenticate
from django.core.paginator import Paginator
from django.db import connection
from datetime import date

cursor = connection.cursor()


def index(request):
	if not request.session.get("user_id"):
		return redirect("/login/")

	sessions = Session.objects.all()
	users_online = sessions.count()

	cursor.execute("SELECT COUNT(user_id) FROM inventory.user WHERE user_status = 'active'")
	users_count = cursor.fetchone()
	cursor.execute("SELECT COUNT(category_id) FROM inventory.category WHERE category_status = 'active'")
	category_count = cursor.fetchone()
	cursor.execute("SELECT COUNT(brand_id) FROM inventory.brand WHERE brand_status = 'active'")
	brand_count = cursor.fetchone()
	cursor.execute("SELECT COUNT(product_id) FROM inventory.product WHERE product_status = 'active'")
	product_count = cursor.fetchone()
	query = "SELECT SUM(inventory_order_total) FROM inventory.order WHERE inventory_order_status = 'active'"

	if request.session["user_type"] == 'user':
		query += " AND user_id = %s" % request.session["user_id"]
	cursor.execute(query)
	total_order_value = cursor.fetchone()

	query = "SELECT SUM(inventory_order_total) FROM inventory.order WHERE inventory_order_status = 'active' and payment_status = 'cash'"
	if request.session["user_type"] == 'user':
		query += " AND user_id = %s" % request.session["user_id"]
	cursor.execute(query)
	total_cash_value = cursor.fetchone()

	query = "SELECT SUM(inventory_order_total) FROM inventory.order WHERE inventory_order_status = 'active' and payment_status = 'credit'"
	if request.session["user_type"] == 'user':
		query += " AND user_id = %s" % request.session["user_id"]
	cursor.execute(query)
	total_credit_value = cursor.fetchone()

	cursor.execute("""SELECT
  SUM(order.inventory_order_total) AS order_total,
  SUM(CASE WHEN order.payment_status = 'cash'
    THEN order.inventory_order_total ELSE 0 END) AS cash_order_total,
  SUM(CASE WHEN order.payment_status = 'credit'
    THEN order.inventory_order_total ELSE 0 END) AS credit_order_total,
  user.user_name
FROM inventory.order
  INNER JOIN inventory.user
    ON user.user_id = inventory.order.user_id
WHERE inventory.order.inventory_order_status = 'active' GROUP BY inventory.order.user_id""")
	users_data = cursor.fetchall()
	paginator = Paginator(users_data, 5)
	page = request.GET.get("page")
	paginated_user_data = paginator.get_page(page)

	return render(request, "index.html", {"users_count": users_count,
										  "category_count": category_count,
										  "brand_count": brand_count,
										  "product_count": product_count,
										  "total_order_value": total_order_value,
										  "total_cash_value": total_cash_value,
										  "total_credit_value": total_credit_value,
										  "users_data": paginated_user_data,
										  "users_online": users_online,
										  })


def login_view(request):
	if request.method == "POST":
		# user = User.objects.filter(user_email=request.POST["username"]).first()
		try:
			user = User.objects.raw("SELECT * FROM user WHERE user_email = '%s'" % request.POST["username"])[0]
		except:
			user = None
		if user:
			if request.POST["password"] == user.user_password:
				if user.user_status == "Active":
					request.session["user_id"] = user.user_id
					request.session["user_name"] = user.user_name
					request.session["user_type"] = user.user_type
					request.session["user_email"] = user.user_email
					return HttpResponseRedirect("/")
				else:
					messages.success(request, "User is disabled. Please contact master")
					return redirect("/login/")
			else:
				messages.success(request, "Username or password error")
				return redirect("/login/")
		else:
			messages.success(request, "Username or password error")
			return redirect("/login/")
	return render(request, "login.html", {})


def logout_view(request):
	request.session.flush()
	return redirect("/login/")


def user_profile(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")

	if request.method == "POST":
		user = User.objects.raw("SELECT * FROM user WHERE user_email = '%s'" % request.session["user_email"])[0]
		if request.POST["user_new_password"] != request.POST["user_re_enter_password"]:
			messages.error(request, "Password not matched")
			return redirect("/profile/")
		elif request.POST["user_new_password"] and not request.POST["user_re_enter_password"]:
			messages.error(request, "Password empty")
			return redirect("/profile/")
		elif request.POST["user_new_password"] and request.POST["user_re_enter_password"]:
			user.user_password = request.POST["user_new_password"]
		user.user_name = request.POST["user_name"]
		user.user_email = request.POST["user_email"]
		user.save()
		request.session["user_name"] = user.user_name
		request.session["user_type"] = user.user_type
		request.session["user_email"] = user.user_email
		messages.success(request, "Profile Updated")
		return redirect("/profile/")
	return render(request, "profile.html", {})


def user_management(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	if request.POST.get("search"):
		users = User.objects.filter(user_email__contains=request.POST["search"])
	else:
		users = User.objects.all()
	paginator = Paginator(users, 10)
	page = request.GET.get("page")
	paginated_users = paginator.get_page(page)
	return render(request, "users.html", {"users": paginated_users})


def status_change_user(request, id):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	user = User.objects.get(user_id=id)
	if user.user_status == "Active":
		user.user_status = "Inactive"
	else:
		user.user_status = "Active"
	user.save()
	referer = request.META["HTTP_REFERER"]
	return redirect(referer)


def add_user(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	if request.method == "POST":
		user = User.objects.create(
			user_email=request.POST["user_email"],
			user_name=request.POST["user_name"],
			user_password=request.POST["user_password"],
			user_status="Active",
		)
		return redirect("/user/")


def category_management(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	categories = Category.objects.all()
	paginator = Paginator(categories, 10)
	page = request.GET.get("page")
	paginated_categories = paginator.get_page(page)
	return render(request, "category.html", {"categories": paginated_categories})


def status_change_category(request, id):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	category = Category.objects.get(category_id=id)
	if category.category_status == "active":
		category.category_status = "inactive"
		print(category.category_status)
	else:
		category.category_status = "active"
	category.save()

	referer = request.META["HTTP_REFERER"]
	return redirect(referer)


def add_category(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	if request.method == "POST":
		category = Category.objects.create(
			category_name=request.POST["category_name"],
			category_status="active",
		)
		return redirect("/category/")


def brand_management(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	brands = Brand.objects.all()
	categories = Category.objects.all()
	paginator = Paginator(brands, 10)
	page = request.GET.get("page")
	paginated_brands = paginator.get_page(page)
	return render(request, "brand.html", {"brands": paginated_brands, "categories": categories})


def status_change_brand(request, id):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	brand = Brand.objects.get(brand_id=id)
	if brand.brand_status == "active":
		brand.brand_status = "inactive"
		print(brand.brand_status)
	else:
		brand.brand_status = "active"
	brand.save()
	referer = request.META["HTTP_REFERER"]
	return redirect(referer)


def add_brand(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	if request.method == "POST":
		category = Category.objects.get(category_id=request.POST["category_id"])
		brand = Brand.objects.create(
			brand_name=request.POST["brand_name"],
			category=category,
			brand_status="active",
		)
		return redirect("/brand/")


def product_management(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	# products = Product.objects.raw("SELECT product_name, category_name, brand_name, product_quantity, user_name, product_status FROM product INNER JOIN category ON product.category_id = category.category_id INNER JOIN brand ON product.brand_id = brand.brand_id INNER JOIN user ON product.product_enter_by = user.user_id")
	cursor.execute(
		"SELECT * FROM inventory.product INNER JOIN inventory.category ON product.category_id = category.category_id INNER JOIN inventory.brand ON product.brand_id = brand.brand_id INNER JOIN inventory.user ON product.product_enter_by = user.user_id ORDER BY product_id;")
	products = cursor.fetchall()
	categories = Category.objects.all()
	brands = Brand.objects.all()
	paginator = Paginator(products, 10)
	page = request.GET.get("page")
	paginated_products = paginator.get_page(page)
	return render(request, "product.html",
				  {"products": paginated_products, "categories": categories, "brands": brands, "User": User})


def status_change_product(request, id):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	cursor.execute("SELECT * FROM inventory.product WHERE product_id=%s" % id)
	product = cursor.fetchone()
	if product[11] == "active":
		cursor.execute("UPDATE inventory.product SET product_status='inactive' WHERE product_id=%s" % id)
	else:
		cursor.execute("UPDATE inventory.product SET product_status='active' WHERE product_id=%s" % id)
	referer = request.META["HTTP_REFERER"]
	return redirect(referer)


def add_product(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	elif request.session.get("user_type") != "master":
		return redirect("/")
	if request.method == "POST":
		cursor.execute("SELECT * FROM inventory.category WHERE category_id=" + request.POST["category_id"])
		# category = Category.objects.get(category_id=request.POST["category_id"])
		category = cursor.fetchone()
		cursor.execute("SELECT * FROM inventory.brand WHERE brand_id=" + request.POST["brand_id"])
		brand = cursor.fetchone()
		cursor.execute(
			"INSERT INTO inventory.product(category_id, brand_id, product_name, product_description, product_quantity, product_unit, product_base_price, product_tax, product_enter_by, product_status, product_date) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
			request.POST["category_id"], request.POST["brand_id"], request.POST["product_name"],
			request.POST["product_description"], request.POST["product_quantity"], request.POST["product_unit"],
			request.POST["product_base_price"], request.POST["product_tax"], request.session["user_id"], "active",
			date.today().strftime("%Y-%m-%d")))
		return redirect("/product/")


def order_management(request):
	print(request.session["user_id"])
	query = "SELECT * FROM inventory.order INNER JOIN inventory.user ON order.user_id = user.user_id"
	if request.session["user_type"] == "user":
		query += " WHERE order.user_id='%s' ORDER BY inventory_order_id ASC" % request.session["user_id"]
	else:
		query += " ORDER BY inventory_order_id ASC"
	cursor.execute(query)
	orders = cursor.fetchall()
	paginator = Paginator(orders, 10)
	page = request.GET.get("page")
	paginated_orders = paginator.get_page(page)
	cursor.execute("SELECT product_id, product_name FROM inventory.product WHERE product_status = 'active' ")
	products = cursor.fetchall
	return render(request, "order.html", {"orders": paginated_orders, "products": products})


def add_order(request):
	if not request.session.get("user_id"):
		return redirect("/login/")
	if request.method == "POST":
		cursor.execute(
			"INSERT INTO inventory.order (user_id, inventory_order_total, inventory_order_date, inventory_order_name, inventory_order_address, payment_status, inventory_order_status, inventory_order_created_date) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
			request.session["user_id"], 0, request.POST["inventory_order_date"], request.POST["inventory_order_name"],
			request.POST["inventory_order_address"], request.POST["payment_status"], 'active',
			date.today().strftime("%Y-%m-%d")))
		order = cursor.lastrowid
		total_amount = 0
		for i in range(len(dict(request.POST)["product_id"])):
			cursor.execute(
				"SELECT * FROM inventory.product WHERE product_id = '%s'" % dict(request.POST)["product_id"][i])
			product = cursor.fetchone()
			cursor.execute(
				"INSERT INTO inventory.order_product (inventory_order_id, product_id, quantity, price, tax) VALUES ('%s', '%s', '%s', '%s', '%s')" % (
				order, product[0], dict(request.POST)["quantity"][i], product[7], product[8]))
			base_price = product[7] * int(dict(request.POST)["quantity"][i])
			tax = (base_price / 100) * float(product[8])
			total_amount = total_amount + (base_price + tax)
			available_quantity = (int(product[5]) - int(request.POST["quantity"]))
			if available_quantity < 1:
				cursor.execute(
					"UPDATE inventory.product SET product_quantity = '%s', product_status = '%s' WHERE product_id = '%s'" % (
					available_quantity, 'inactive', product[0]))
			else:
				cursor.execute("UPDATE inventory.product SET product_quantity = '%s' WHERE product_id = '%s'" % (
				available_quantity, product[0]))
		cursor.execute(
			"UPDATE inventory.order SET inventory_order_total = '%s', discount = '%s' WHERE inventory_order_id = '%s'" % (
			total_amount, request.POST["discount"], order))
		return redirect("/order/")


def status_change_order(request, id):
	if not request.session.get("user_id"):
		return redirect("/login/")
	cursor.execute("SELECT * FROM inventory.order WHERE inventory_order_id = %s" % id)
	order = cursor.fetchone()
	if order[7] == "active":
		cursor.execute(
			"UPDATE inventory.order SET order_complete_date = '%s', inventory_order_status = 'inactive' WHERE inventory_order_id = %s" % (
			date.today().strftime("%Y-%m-%d"), id))
	else:
		cursor.execute(
			"UPDATE inventory.order SET inventory_order_status = 'active' WHERE inventory_order_id = %s" % id)
	referer = request.META["HTTP_REFERER"]
	return redirect(referer)


def invoce_maker(request, id):
	cursor.execute(
		"SELECT * FROM inventory.order INNER JOIN inventory.user ON order.user_id = user.user_id WHERE inventory_order_id = '%s'" % id)
	order = cursor.fetchone()
	cursor.execute(
		"SELECT * FROM inventory.order_product INNER JOIN inventory.product ON order_product.product_id = product.product_id  WHERE inventory_order_id='%s'" % id)
	items = cursor.fetchall()
	return render(request, "sample-invoice.html", {"order": order, "items": items})
