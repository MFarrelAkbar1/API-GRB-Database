from flask import Flask, jsonify, request, render_template_string
from sqlalchemy.exc import SQLAlchemyError
from config import Config
from models import db, Manager, Publisher, Book, BookStore, Author, BookAuthors, BookGenre, BookBookGenre, Supplier, SupplierBooks, OrderSupplies, Customer, OnlineAccount, BookReviews, CustomerFeedback, Staff, Inventory, Contracts, Wishlist, WishlistItems, init_db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route('/')
def index():
    buttons = [
        {"name": "Managers", "endpoint": "/managers"},
        {"name": "Publishers", "endpoint": "/publishers"},
        {"name": "Books", "endpoint": "/books"},
        {"name": "Bookstores", "endpoint": "/bookstores"},
        {"name": "Authors", "endpoint": "/authors"},
        {"name": "Book Authors", "endpoint": "/bookauthors"},
        {"name": "Book Genres", "endpoint": "/bookgenres"},
        {"name": "Book Book Genres", "endpoint": "/bookbookgenres"},
        {"name": "Suppliers", "endpoint": "/suppliers"},
        {"name": "Supplier Books", "endpoint": "/supplierbooks"},
        {"name": "Order Supplies", "endpoint": "/ordersupplies"},
        {"name": "Customers", "endpoint": "/customers"},
        {"name": "Online Accounts", "endpoint": "/onlineaccounts"},
        {"name": "Book Reviews", "endpoint": "/bookreviews"},
        {"name": "Customer Feedback", "endpoint": "/customerfeedback"},
        {"name": "Staff", "endpoint": "/staff"},
        {"name": "Inventory", "endpoint": "/inventory"},
        {"name": "Contracts", "endpoint": "/contracts"},
        {"name": "Wishlist", "endpoint": "/wishlist"},
        {"name": "Wishlist Items", "endpoint": "/wishlistitems"},
    ]
    template = '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Bookstore API</title>
        <style>
          .button-container {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
          }
          .button-container button {
            margin: 5px 0;
            padding: 10px 20px;
            font-size: 16px;
          }
        </style>
      </head>
      <body>
        <h1>Welcome to the GRB Bookstore API!</h1>
        <div class="button-container">
          {% for button in buttons %}
            <button onclick="openInNewTab('{{ button.endpoint }}')">{{ button.name }}</button>
          {% endfor %}
        </div>
        <script>
          function openInNewTab(url) {
            window.open(url, '_blank');
          }
        </script>
      </body>
    </html>
    '''
    return render_template_string(template, buttons=buttons)

# Function to convert query results to dictionaries
def query_to_dict(result):
    return [item.to_dict() for item in result]

# SQL Builder
def sql_builder(table, filters):
    query = f"SELECT * FROM {table} WHERE "
    conditions = []
    for key, value in filters.items():
        conditions.append(f"{key}='{value}'")
    query += " AND ".join(conditions)
    return query

# Endpoint to run the SQL builder query
@app.route('/sql_builder', methods=['GET'])
def run_sql_builder():
    table = request.args.get('table')
    filters = request.args.to_dict(flat=True)
    filters.pop('table', None)
    query = sql_builder(table, filters)
    result = db.session.execute(query)
    return jsonify([dict(row) for row in result])

# Endpoint to select books by author
@app.route('/books/author/<author_id>', methods=['GET'])
def get_books_by_author(author_id):
    books = db.session.query(Book).join(BookAuthors).filter(BookAuthors.AuthorNumber == author_id).all()
    return jsonify(query_to_dict(books))

# Endpoint to search books based on keywords
@app.route('/books/search', methods=['GET'])
def search_books():
    keywords = request.args.get('keywords')
    books = Book.query.filter(Book.BookName.ilike(f'%{keywords}%')).all()
    return jsonify(query_to_dict(books))

# Endpoint to wishlist a book
@app.route('/wishlist/add', methods=['POST'])
def add_to_wishlist():
    data = request.get_json()
    wishlist_item = WishlistItems(
        wishlistitemid=data['wishlistitemid'],
        isbn=data['isbn'],
        quantity=data['quantity']
    )
    db.session.add(wishlist_item)
    db.session.commit()
    return jsonify({'message': 'Book added to wishlist successfully'}), 201

# DML: Update Book Price
@app.route('/books/update/<isbn>', methods=['PUT'])
def update_book(isbn):
    data = request.get_json()
    book = Book.query.filter_by(isbn=isbn).first()
    if not book:
        return jsonify({'message': 'Book not found'}), 404

    book.price = data['price']
    db.session.commit()
    return jsonify({'message': 'Book price updated successfully'})

# TCL: Combine Several SQL Statements
@app.route('/transaction', methods=['POST'])
def perform_transaction():
    try:
        data = request.get_json()

        # Update book price
        book = Book.query.filter_by(isbn=data['isbn']).first()
        if not book:
            return jsonify({'message': 'Book not found'}), 404
        book.price = data['price']

        # Add to wishlist
        wishlist_item = WishlistItems(
            wishlistitemid=data['wishlistitemid'],
            isbn=data['isbn'],
            quantity=data['quantity']
        )
        db.session.add(wishlist_item)

        # Commit the transaction
        db.session.commit()

        return jsonify({'message': 'Transaction completed successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Existing endpoints to get data from tables
@app.route('/managers', methods=['GET', 'POST', 'PUT'])
def manage_managers():
    if request.method == 'GET':
        managers = Manager.query.all()
        return jsonify([manager.to_dict() for manager in managers])
    if request.method == 'POST':
        data = request.get_json()
        manager = Manager(
            managerid=data['managerid'],
            manageremail=data['manageremail']
        )
        db.session.add(manager)
        db.session.commit()
        return jsonify({'message': 'Manager added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        manager = Manager.query.filter_by(managerid=data['managerid']).first()
        if not manager:
            return jsonify({'message': 'Manager not found'}), 404
        manager.manageremail = data['manageremail']
        db.session.commit()
        return jsonify({'message': 'Manager updated successfully'})

@app.route('/managers/<int:managerid>', methods=['DELETE'])
def delete_manager(managerid):
    manager = Manager.query.filter_by(managerid=managerid).first()
    if not manager:
        return jsonify({'message': 'Manager not found'}), 404
    db.session.delete(manager)
    db.session.commit()
    return jsonify({'message': 'Manager deleted successfully'})

@app.route('/publishers', methods=['GET', 'POST', 'PUT'])
def manage_publishers():
    if request.method == 'GET':
        publishers = Publisher.query.all()
        return jsonify([publisher.to_dict() for publisher in publishers])
    if request.method == 'POST':
        data = request.get_json()
        publisher = Publisher(
            idpublisher=data['idpublisher'],
            namepublisher=data['namepublisher'],
            citypublisher=data['citypublisher'],
            telephonepublisher=data['telephonepublisher'],
            countrypublisher=data['countrypublisher']
        )
        db.session.add(publisher)
        db.session.commit()
        return jsonify({'message': 'Publisher added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        publisher = Publisher.query.filter_by(idpublisher=data['idpublisher']).first()
        if not publisher:
            return jsonify({'message': 'Publisher not found'}), 404
        publisher.namepublisher = data['namepublisher']
        publisher.citypublisher = data['citypublisher']
        publisher.telephonepublisher = data['telephonepublisher']
        publisher.countrypublisher = data['countrypublisher']
        db.session.commit()
        return jsonify({'message': 'Publisher updated successfully'})

@app.route('/publishers/<string:idpublisher>', methods=['DELETE'])
def delete_publisher(idpublisher):
    publisher = Publisher.query.filter_by(idpublisher=idpublisher).first()
    if not publisher:
        return jsonify({'message': 'Publisher not found'}), 404
    db.session.delete(publisher)
    db.session.commit()
    return jsonify({'message': 'Publisher deleted successfully'})

@app.route('/books', methods=['GET', 'POST', 'PUT'])
def manage_books():
    if request.method == 'GET':
        books = Book.query.all()
        return jsonify([book.to_dict() for book in books])
    if request.method == 'POST':
        data = request.get_json()
        book = Book(
            isbn=data['isbn'],
            bookname=data['bookname'],
            publicationyear=data['publicationyear'],
            pages=data['pages'],
            price=data['price'],
            idpublisher=data['idpublisher']
        )
        db.session.add(book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        book = Book.query.filter_by(isbn=data['isbn']).first()
        if not book:
            return jsonify({'message': 'Book not found'}), 404
        book.bookname = data['bookname']
        book.publicationyear = data['publicationyear']
        book.pages = data['pages']
        book.price = data['price']
        book.idpublisher = data['idpublisher']
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'})

@app.route('/books/<string:isbn>', methods=['DELETE'])
def delete_book(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

@app.route('/bookstores', methods=['GET', 'POST', 'PUT'])
def manage_bookstores():
    if request.method == 'GET':
        bookstores = BookStore.query.all()
        return jsonify([bookstore.to_dict() for bookstore in bookstores])
    if request.method == 'POST':
        data = request.get_json()
        bookstore = BookStore(
            storeid=data['storeid'],
            location=data['location'],
            managerid=data['managerid']
        )
        db.session.add(bookstore)
        db.session.commit()
        return jsonify({'message': 'Bookstore added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        bookstore = BookStore.query.filter_by(storeid=data['storeid']).first()
        if not bookstore:
            return jsonify({'message': 'Bookstore not found'}), 404
        bookstore.location = data['location']
        bookstore.managerid = data['managerid']
        db.session.commit()
        return jsonify({'message': 'Bookstore updated successfully'})

@app.route('/bookstores/<int:storeid>', methods=['DELETE'])
def delete_bookstore(storeid):
    bookstore = BookStore.query.filter_by(storeid=storeid).first()
    if not bookstore:
        return jsonify({'message': 'Bookstore not found'}), 404
    db.session.delete(bookstore)
    db.session.commit()
    return jsonify({'message': 'Bookstore deleted successfully'})

@app.route('/authors', methods=['GET', 'POST', 'PUT'])
def manage_authors():
    if request.method == 'GET':
        authors = Author.query.all()
        return jsonify([author.to_dict() for author in authors])
    if request.method == 'POST':
        data = request.get_json()
        author = Author(
            authornumber=data['authornumber'],
            authorname=data['authorname'],
            yearborn=data['yearborn'],
            biography=data['biography']
        )
        db.session.add(author)
        db.session.commit()
        return jsonify({'message': 'Author added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        author = Author.query.filter_by(authornumber=data['authornumber']).first()
        if not author:
            return jsonify({'message': 'Author not found'}), 404
        author.authorname = data['authorname']
        author.yearborn = data['yearborn']
        author.biography = data['biography']
        db.session.commit()
        return jsonify({'message': 'Author updated successfully'})

@app.route('/authors/<int:authornumber>', methods=['DELETE'])
def delete_author(authornumber):
    author = Author.query.filter_by(authornumber=authornumber).first()
    if not author:
        return jsonify({'message': 'Author not found'}), 404
    db.session.delete(author)
    db.session.commit()
    return jsonify({'message': 'Author deleted successfully'})

@app.route('/bookauthors', methods=['GET', 'POST', 'PUT'])
def manage_bookauthors():
    if request.method == 'GET':
        bookauthors = BookAuthors.query.all()
        return jsonify([bookauthor.to_dict() for bookauthor in bookauthors])
    if request.method == 'POST':
        data = request.get_json()
        bookauthor = BookAuthors(
            isbn=data['isbn'],
            authornumber=data['authornumber']
        )
        db.session.add(bookauthor)
        db.session.commit()
        return jsonify({'message': 'Book Author added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        bookauthor = BookAuthors.query.filter_by(isbn=data['isbn'], authornumber=data['authornumber']).first()
        if not bookauthor:
            return jsonify({'message': 'Book Author not found'}), 404
        bookauthor.isbn = data['isbn']
        bookauthor.authornumber = data['authornumber']
        db.session.commit()
        return jsonify({'message': 'Book Author updated successfully'})

@app.route('/bookauthors/<string:isbn>/<int:authornumber>', methods=['DELETE'])
def delete_bookauthor(isbn, authornumber):
    bookauthor = BookAuthors.query.filter_by(isbn=isbn, authornumber=authornumber).first()
    if not bookauthor:
        return jsonify({'message': 'Book Author not found'}), 404
    db.session.delete(bookauthor)
    db.session.commit()
    return jsonify({'message': 'Book Author deleted successfully'})

@app.route('/bookgenres', methods=['GET', 'POST', 'PUT'])
def manage_bookgenres():
    if request.method == 'GET':
        bookgenres = BookGenre.query.all()
        return jsonify([bookgenre.to_dict() for bookgenre in bookgenres])
    if request.method == 'POST':
        data = request.get_json()
        bookgenre = BookGenre(
            genreid=data['genreid'],
            genretype=data['genretype'],
            genredescription=data['genredescription']
        )
        db.session.add(bookgenre)
        db.session.commit()
        return jsonify({'message': 'Book Genre added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        bookgenre = BookGenre.query.filter_by(genreid=data['genreid']).first()
        if not bookgenre:
            return jsonify({'message': 'Book Genre not found'}), 404
        bookgenre.genretype = data['genretype']
        bookgenre.genredescription = data['genredescription']
        db.session.commit()
        return jsonify({'message': 'Book Genre updated successfully'})

@app.route('/bookgenres/<int:genreid>', methods=['DELETE'])
def delete_bookgenre(genreid):
    bookgenre = BookGenre.query.filter_by(genreid=genreid).first()
    if not bookgenre:
        return jsonify({'message': 'Book Genre not found'}), 404
    db.session.delete(bookgenre)
    db.session.commit()
    return jsonify({'message': 'Book Genre deleted successfully'})

@app.route('/bookbookgenres', methods=['GET', 'POST', 'PUT'])
def manage_bookbookgenres():
    if request.method == 'GET':
        bookbookgenres = BookBookGenre.query.all()
        return jsonify([bookbookgenre.to_dict() for bookbookgenre in bookbookgenres])
    if request.method == 'POST':
        data = request.get_json()
        bookbookgenre = BookBookGenre(
            isbn=data['isbn'],
            genreid=data['genreid']
        )
        db.session.add(bookbookgenre)
        db.session.commit()
        return jsonify({'message': 'Book Book Genre added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        bookbookgenre = BookBookGenre.query.filter_by(isbn=data['isbn'], genreid=data['genreid']).first()
        if not bookbookgenre:
            return jsonify({'message': 'Book Book Genre not found'}), 404
        bookbookgenre.isbn = data['isbn']
        bookbookgenre.genreid = data['genreid']
        db.session.commit()
        return jsonify({'message': 'Book Book Genre updated successfully'})

@app.route('/bookbookgenres/<string:isbn>/<int:genreid>', methods=['DELETE'])
def delete_bookbookgenre(isbn, genreid):
    bookbookgenre = BookBookGenre.query.filter_by(isbn=isbn, genreid=genreid).first()
    if not bookbookgenre:
        return jsonify({'message': 'Book Book Genre not found'}), 404
    db.session.delete(bookbookgenre)
    db.session.commit()
    return jsonify({'message': 'Book Book Genre deleted successfully'})

@app.route('/suppliers', methods=['GET', 'POST', 'PUT'])
def manage_suppliers():
    if request.method == 'GET':
        suppliers = Supplier.query.all()
        return jsonify([supplier.to_dict() for supplier in suppliers])
    if request.method == 'POST':
        data = request.get_json()
        supplier = Supplier(
            supplierid=data['supplierid'],
            suppliername=data['suppliername'],
            suppliercontactinfo=data['suppliercontactinfo'],
            supplieraddress=data['supplieraddress']
        )
        db.session.add(supplier)
        db.session.commit()
        return jsonify({'message': 'Supplier added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        supplier = Supplier.query.filter_by(supplierid=data['supplierid']).first()
        if not supplier:
            return jsonify({'message': 'Supplier not found'}), 404
        supplier.suppliername = data['suppliername']
        supplier.suppliercontactinfo = data['suppliercontactinfo']
        supplier.supplieraddress = data['supplieraddress']
        db.session.commit()
        return jsonify({'message': 'Supplier updated successfully'})

@app.route('/suppliers/<int:supplierid>', methods=['DELETE'])
def delete_supplier(supplierid):
    supplier = Supplier.query.filter_by(supplierid=supplierid).first()
    if not supplier:
        return jsonify({'message': 'Supplier not found'}), 404
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier deleted successfully'})

@app.route('/supplierbooks', methods=['GET', 'POST', 'PUT'])
def manage_supplierbooks():
    if request.method == 'GET':
        supplierbooks = SupplierBooks.query.all()
        return jsonify([supplierbook.to_dict() for supplierbook in supplierbooks])
    if request.method == 'POST':
        data = request.get_json()
        supplierbook = SupplierBooks(
            supplierid=data['supplierid'],
            isbn=data['isbn']
        )
        db.session.add(supplierbook)
        db.session.commit()
        return jsonify({'message': 'Supplier Book added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        supplierbook = SupplierBooks.query.filter_by(supplierid=data['supplierid'], isbn=data['isbn']).first()
        if not supplierbook:
            return jsonify({'message': 'Supplier Book not found'}), 404
        supplierbook.supplierid = data['supplierid']
        supplierbook.isbn = data['isbn']
        db.session.commit()
        return jsonify({'message': 'Supplier Book updated successfully'})

@app.route('/supplierbooks/<int:supplierid>/<string:isbn>', methods=['DELETE'])
def delete_supplierbook(supplierid, isbn):
    supplierbook = SupplierBooks.query.filter_by(supplierid=supplierid, isbn=isbn).first()
    if not supplierbook:
        return jsonify({'message': 'Supplier Book not found'}), 404
    db.session.delete(supplierbook)
    db.session.commit()
    return jsonify({'message': 'Supplier Book deleted successfully'})

@app.route('/ordersupplies', methods=['GET', 'POST', 'PUT'])
def manage_ordersupplies():
    if request.method == 'GET':
        ordersupplies = OrderSupplies.query.all()
        return jsonify([ordersupply.to_dict() for ordersupply in ordersupplies])
    if request.method == 'POST':
        data = request.get_json()
        ordersupply = OrderSupplies(
            ordersuppliesid=data['ordersuppliesid'],
            supplierid=data['supplierid'],
            suppliesorderdate=data['suppliesorderdate'],
            ordersupplyquantity=data['ordersupplyquantity'],
            storeid=data['storeid']
        )
        db.session.add(ordersupply)
        db.session.commit()
        return jsonify({'message': 'Order Supply added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        ordersupply = OrderSupplies.query.filter_by(ordersuppliesid=data['ordersuppliesid']).first()
        if not ordersupply:
            return jsonify({'message': 'Order Supply not found'}), 404
        ordersupply.supplierid = data['supplierid']
        ordersupply.suppliesorderdate = data['suppliesorderdate']
        ordersupply.ordersupplyquantity = data['ordersupplyquantity']
        ordersupply.storeid = data['storeid']
        db.session.commit()
        return jsonify({'message': 'Order Supply updated successfully'})

@app.route('/ordersupplies/<int:ordersuppliesid>', methods=['DELETE'])
def delete_ordersupply(ordersuppliesid):
    ordersupply = OrderSupplies.query.filter_by(ordersuppliesid=ordersuppliesid).first()
    if not ordersupply:
        return jsonify({'message': 'Order Supply not found'}), 404
    db.session.delete(ordersupply)
    db.session.commit()
    return jsonify({'message': 'Order Supply deleted successfully'})

@app.route('/customers', methods=['GET', 'POST', 'PUT'])
def manage_customers():
    if request.method == 'GET':
        customers = Customer.query.all()
        return jsonify([customer.to_dict() for customer in customers])
    if request.method == 'POST':
        data = request.get_json()
        customer = Customer(
            customernumber=data['customernumber'],
            customername=data['customername'],
            customeraddress=data['customeraddress']
        )
        db.session.add(customer)
        db.session.commit()
        return jsonify({'message': 'Customer added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        customer = Customer.query.filter_by(customernumber=data['customernumber']).first()
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404
        customer.customername = data['customername']
        customer.customeraddress = data['customeraddress']
        db.session.commit()
        return jsonify({'message': 'Customer updated successfully'})

@app.route('/customers/<int:customernumber>', methods=['DELETE'])
def delete_customer(customernumber):
    customer = Customer.query.filter_by(customernumber=customernumber).first()
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'})

@app.route('/onlineaccounts', methods=['GET', 'POST', 'PUT'])
def manage_onlineaccounts():
    if request.method == 'GET':
        onlineaccounts = OnlineAccount.query.all()
        return jsonify([onlineaccount.to_dict() for onlineaccount in onlineaccounts])
    if request.method == 'POST':
        data = request.get_json()
        onlineaccount = OnlineAccount(
            accountid=data['accountid'],
            customernumber=data['customernumber'],
            customeremail=data['customeremail'],
            username=data['username'],
            password=data['password'],
            accountstatus=data['accountstatus']
        )
        db.session.add(onlineaccount)
        db.session.commit()
        return jsonify({'message': 'Online Account added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        onlineaccount = OnlineAccount.query.filter_by(accountid=data['accountid']).first()
        if not onlineaccount:
            return jsonify({'message': 'Online Account not found'}), 404
        onlineaccount.customernumber = data['customernumber']
        onlineaccount.customeremail = data['customeremail']
        onlineaccount.username = data['username']
        onlineaccount.password = data['password']
        onlineaccount.accountstatus = data['accountstatus']
        db.session.commit()
        return jsonify({'message': 'Online Account updated successfully'})

@app.route('/onlineaccounts/<int:accountid>', methods=['DELETE'])
def delete_onlineaccount(accountid):
    onlineaccount = OnlineAccount.query.filter_by(accountid=accountid).first()
    if not onlineaccount:
        return jsonify({'message': 'Online Account not found'}), 404
    db.session.delete(onlineaccount)
    db.session.commit()
    return jsonify({'message': 'Online Account deleted successfully'})

@app.route('/bookreviews', methods=['GET', 'POST', 'PUT'])
def manage_bookreviews():
    if request.method == 'GET':
        bookreviews = BookReviews.query.all()
        return jsonify([bookreview.to_dict() for bookreview in bookreviews])
    if request.method == 'POST':
        data = request.get_json()
        bookreview = BookReviews(
            reviewid=data['reviewid'],
            isbn=data['isbn'],
            customernumber=data['customernumber'],
            rating=data['rating'],
            reviewdate=data['reviewdate']
        )
        db.session.add(bookreview)
        db.session.commit()
        return jsonify({'message': 'Book Review added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        bookreview = BookReviews.query.filter_by(reviewid=data['reviewid']).first()
        if not bookreview:
            return jsonify({'message': 'Book Review not found'}), 404
        bookreview.isbn = data['isbn']
        bookreview.customernumber = data['customernumber']
        bookreview.rating = data['rating']
        bookreview.reviewdate = data['reviewdate']
        db.session.commit()
        return jsonify({'message': 'Book Review updated successfully'})

@app.route('/bookreviews/<int:reviewid>', methods=['DELETE'])
def delete_bookreview(reviewid):
    bookreview = BookReviews.query.filter_by(reviewid=reviewid).first()
    if not bookreview:
        return jsonify({'message': 'Book Review not found'}), 404
    db.session.delete(bookreview)
    db.session.commit()
    return jsonify({'message': 'Book Review deleted successfully'})

@app.route('/customerfeedback', methods=['GET', 'POST', 'PUT'])
def manage_customerfeedback():
    if request.method == 'GET':
        customerfeedback = CustomerFeedback.query.all()
        return jsonify([feedback.to_dict() for feedback in customerfeedback])
    if request.method == 'POST':
        data = request.get_json()
        feedback = CustomerFeedback(
            feedbackid=data['feedbackid'],
            customernumber=data['customernumber'],
            feedbackdate=data['feedbackdate'],
            feedbacktext=data['feedbacktext']
        )
        db.session.add(feedback)
        db.session.commit()
        return jsonify({'message': 'Customer Feedback added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        feedback = CustomerFeedback.query.filter_by(feedbackid=data['feedbackid']).first()
        if not feedback:
            return jsonify({'message': 'Customer Feedback not found'}), 404
        feedback.customernumber = data['customernumber']
        feedback.feedbackdate = data['feedbackdate']
        feedback.feedbacktext = data['feedbacktext']
        db.session.commit()
        return jsonify({'message': 'Customer Feedback updated successfully'})

@app.route('/customerfeedback/<int:feedbackid>', methods=['DELETE'])
def delete_customerfeedback(feedbackid):
    feedback = CustomerFeedback.query.filter_by(feedbackid=feedbackid).first()
    if not feedback:
        return jsonify({'message': 'Customer Feedback not found'}), 404
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({'message': 'Customer Feedback deleted successfully'})

@app.route('/staff', methods=['GET', 'POST', 'PUT'])
def manage_staff():
    if request.method == 'GET':
        staff = Staff.query.all()
        return jsonify([member.to_dict() for member in staff])
    if request.method == 'POST':
        data = request.get_json()
        staff = Staff(
            staffid=data['staffid'],
            staffname=data['staffname'],
            position=data['position'],
            staffdateadded=data['staffdateadded'],
            staffemail=data['staffemail'],
            staffaddress=data['staffaddress'],
            storeid=data['storeid']
        )
        db.session.add(staff)
        db.session.commit()
        return jsonify({'message': 'Staff added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        staff = Staff.query.filter_by(staffid=data['staffid']).first()
        if not staff:
            return jsonify({'message': 'Staff not found'}), 404
        staff.staffname = data['staffname']
        staff.position = data['position']
        staff.staffdateadded = data['staffdateadded']
        staff.staffemail = data['staffemail']
        staff.staffaddress = data['staffaddress']
        staff.storeid = data['storeid']
        db.session.commit()
        return jsonify({'message': 'Staff updated successfully'})
    
@app.route('/staff/<int:staffid>', methods=['DELETE'])
def delete_staff(staffid):
    staff = Staff.query.filter_by(staffid=staffid).first()
    if not staff:
        return jsonify({'message': 'Staff not found'}), 404
    db.session.delete(staff)
    db.session.commit()
    return jsonify({'message': 'Staff deleted successfully'})

@app.route('/inventory', methods=['GET', 'POST', 'PUT'])
def manage_inventory():
    if request.method == 'GET':
        inventory = Inventory.query.all()
        return jsonify([item.to_dict() for item in inventory])
    if request.method == 'POST':
        data = request.get_json()
        item = Inventory(
            inventoryid=data['inventoryid'],
            bookid=data['bookid'],
            quantity=data['quantity'],
            supplierid=data['supplierid'],
            storeid=data['storeid']
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({'message': 'Inventory item added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        item = Inventory.query.filter_by(inventoryid=data['inventoryid']).first()
        if not item:
            return jsonify({'message': 'Inventory item not found'}), 404
        item.bookid = data['bookid']
        item.quantity = data['quantity']
        item.supplierid = data['supplierid']
        item.storeid = data['storeid']
        db.session.commit()
        return jsonify({'message': 'Inventory item updated successfully'})

@app.route('/inventory/<int:inventoryid>', methods=['DELETE'])
def delete_inventory(inventoryid):
    item = Inventory.query.filter_by(inventoryid=inventoryid).first()
    if not item:
        return jsonify({'message': 'Inventory item not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Inventory item deleted successfully'})

@app.route('/contracts', methods=['GET', 'POST', 'PUT'])
def manage_contracts():
    if request.method == 'GET':
        contracts = Contracts.query.all()
        return jsonify([contract.to_dict() for contract in contracts])
    if request.method == 'POST':
        data = request.get_json()
        contract = Contracts(
            contractid=data['contractid'],
            supplierid=data['supplierid'],
            idpublisher=data['idpublisher'],
            startdate=data['startdate'],
            enddate=data['enddate'],
            contractdetails=data['contractdetails']
        )
        db.session.add(contract)
        db.session.commit()
        return jsonify({'message': 'Contract added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        contract = Contracts.query.filter_by(contractid=data['contractid']).first()
        if not contract:
            return jsonify({'message': 'Contract not found'}), 404
        contract.supplierid = data['supplierid']
        contract.idpublisher = data['idpublisher']
        contract.startdate = data['startdate']
        contract.enddate = data['enddate']
        contract.contractdetails = data['contractdetails']
        db.session.commit()
        return jsonify({'message': 'Contract updated successfully'})

@app.route('/contracts/<int:contractid>', methods=['DELETE'])
def delete_contract(contractid):
    contract = Contracts.query.filter_by(contractid=contractid).first()
    if not contract:
        return jsonify({'message': 'Contract not found'}), 404
    db.session.delete(contract)
    db.session.commit()
    return jsonify({'message': 'Contract deleted successfully'})

@app.route('/wishlist', methods=['GET', 'POST', 'PUT'])
def manage_wishlist():
    if request.method == 'GET':
        wishlist = Wishlist.query.all()
        return jsonify([item.to_dict() for item in wishlist])
    if request.method == 'POST':
        data = request.get_json()
        wishlist = Wishlist(
            wishlistitemid=data['wishlistitemid'],
            customernumber=data['customernumber'],
            totalprice=data['totalprice'],
            wishlistquantity=data['wishlistquantity']
        )
        db.session.add(wishlist)
        db.session.commit()
        return jsonify({'message': 'Wishlist item added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        wishlist = Wishlist.query.filter_by(wishlistitemid=data['wishlistitemid']).first()
        if not wishlist:
            return jsonify({'message': 'Wishlist item not found'}), 404
        wishlist.customernumber = data['customernumber']
        wishlist.totalprice = data['totalprice']
        wishlist.wishlistquantity = data['wishlistquantity']
        db.session.commit()
        return jsonify({'message': 'Wishlist item updated successfully'})

@app.route('/wishlist/<int:wishlistitemid>', methods=['DELETE'])
def delete_wishlist(wishlistitemid):
    wishlist = Wishlist.query.filter_by(wishlistitemid=wishlistitemid).first()
    if not wishlist:
        return jsonify({'message': 'Wishlist item not found'}), 404
    db.session.delete(wishlist)
    db.session.commit()
    return jsonify({'message': 'Wishlist item deleted successfully'})

@app.route('/wishlistitems', methods=['GET', 'POST', 'PUT'])
def manage_wishlistitems():
    if request.method == 'GET':
        wishlistitems = WishlistItems.query.all()
        return jsonify([item.to_dict() for item in wishlistitems])
    if request.method == 'POST':
        data = request.get_json()
        wishlistitem = WishlistItems(
            wishlistitemid=data['wishlistitemid'],
            isbn=data['isbn'],
            quantity=data['quantity']
        )
        db.session.add(wishlistitem)
        db.session.commit()
        return jsonify({'message': 'Wishlist Item added successfully'}), 201
    if request.method == 'PUT':
        data = request.get_json()
        wishlistitem = WishlistItems.query.filter_by(wishlistitemid=data['wishlistitemid'], isbn=data['isbn']).first()
        if not wishlistitem:
            return jsonify({'message': 'Wishlist Item not found'}), 404
        wishlistitem.isbn = data['isbn']
        wishlistitem.quantity = data['quantity']
        db.session.commit()
        return jsonify({'message': 'Wishlist Item updated successfully'})

@app.route('/wishlistitems/<int:wishlistitemid>/<string:isbn>', methods=['DELETE'])
def delete_wishlistitem(wishlistitemid, isbn):
    wishlistitem = WishlistItems.query.filter_by(wishlistitemid=wishlistitemid, isbn=isbn).first()
    if not wishlistitem:
        return jsonify({'message': 'Wishlist Item not found'}), 404
    db.session.delete(wishlistitem)
    db.session.commit()
    return jsonify({'message': 'Wishlist Item deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
