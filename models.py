from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Manager(db.Model):
    __tablename__ = 'manager'
    __table_args__ = {'extend_existing': True}
    managerid = db.Column(db.Integer, primary_key=True)
    manageremail = db.Column(db.String, nullable=False)

class Publisher(db.Model):
    __tablename__ = 'publisher'
    __table_args__ = {'extend_existing': True}
    idpublisher = db.Column(db.String, primary_key=True)
    namepublisher = db.Column(db.String, nullable=False)
    citypublisher = db.Column(db.String, nullable=False)
    telephonepublisher = db.Column(db.String, nullable=False)
    countrypublisher = db.Column(db.String, nullable=False)

class Book(db.Model):
    __tablename__ = 'book'
    __table_args__ = {'extend_existing': True}
    isbn = db.Column(db.String, primary_key=True)
    bookname = db.Column(db.String, nullable=False)
    publicationyear = db.Column(db.Integer, nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    idpublisher = db.Column(db.String, db.ForeignKey('publisher.idpublisher'))

class BookStore(db.Model):
    __tablename__ = 'bookstore'
    __table_args__ = {'extend_existing': True}
    storeid = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String, nullable=False)
    managerid = db.Column(db.Integer, db.ForeignKey('manager.managerid'))

class Author(db.Model):
    __tablename__ = 'author'
    __table_args__ = {'extend_existing': True}
    authornumber = db.Column(db.Integer, primary_key=True)
    authorname = db.Column(db.String, nullable=False)
    yearborn = db.Column(db.Integer, nullable=False)
    biography = db.Column(db.Text, nullable=False)

class BookAuthors(db.Model):
    __tablename__ = 'bookauthors'
    __table_args__ = {'extend_existing': True}
    isbn = db.Column(db.String, db.ForeignKey('book.isbn'), primary_key=True)
    authornumber = db.Column(db.Integer, db.ForeignKey('author.authornumber'), primary_key=True)

class BookGenre(db.Model):
    __tablename__ = 'bookgenre'
    __table_args__ = {'extend_existing': True}
    genreid = db.Column(db.Integer, primary_key=True)
    genretype = db.Column(db.String, nullable=False)
    genredescription = db.Column(db.String, nullable=False)

class BookBookGenre(db.Model):
    __tablename__ = 'bookbookgenre'
    __table_args__ = {'extend_existing': True}
    isbn = db.Column(db.String, db.ForeignKey('book.isbn'), primary_key=True)
    genreid = db.Column(db.Integer, db.ForeignKey('bookgenre.genreid'), primary_key=True)

class Supplier(db.Model):
    __tablename__ = 'supplier'
    __table_args__ = {'extend_existing': True}
    supplierid = db.Column(db.Integer, primary_key=True)
    suppliername = db.Column(db.String, nullable=False)
    suppliercontactinfo = db.Column(db.String, nullable=False)
    supplieraddress = db.Column(db.String, nullable=False)

class SupplierBooks(db.Model):
    __tablename__ = 'supplierbooks'
    __table_args__ = {'extend_existing': True}
    supplierid = db.Column(db.Integer, db.ForeignKey('supplier.supplierid'), primary_key=True)
    isbn = db.Column(db.String, db.ForeignKey('book.isbn'), primary_key=True)

class OrderSupplies(db.Model):
    __tablename__ = 'ordersupplies'
    __table_args__ = {'extend_existing': True}
    ordersuppliesid = db.Column(db.Integer, primary_key=True)
    supplierid = db.Column(db.Integer, db.ForeignKey('supplier.supplierid'))
    suppliesorderdate = db.Column(db.Date, nullable=False)
    ordersupplyquantity = db.Column(db.Integer, nullable=False)
    storeid = db.Column(db.Integer, db.ForeignKey('bookstore.storeid'))

class Customer(db.Model):
    __tablename__ = 'customer'
    __table_args__ = {'extend_existing': True}
    customernumber = db.Column(db.Integer, primary_key=True)
    customername = db.Column(db.String, nullable=False)
    customeraddress = db.Column(db.String, nullable=False)

class OnlineAccount(db.Model):
    __tablename__ = 'onlineaccount'
    __table_args__ = {'extend_existing': True}
    accountid = db.Column(db.Integer, primary_key=True)
    customernumber = db.Column(db.Integer, db.ForeignKey('customer.customernumber'))
    customeremail = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    accountstatus = db.Column(db.String, nullable=False)

class BookReviews(db.Model):
    __tablename__ = 'bookreviews'
    __table_args__ = {'extend_existing': True}
    reviewid = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, db.ForeignKey('book.isbn'))
    customernumber = db.Column(db.Integer, db.ForeignKey('customer.customernumber'))
    rating = db.Column(db.Integer, nullable=False)
    reviewdate = db.Column(db.Date, nullable=False)

class CustomerFeedback(db.Model):
    __tablename__ = 'customerfeedback'
    __table_args__ = {'extend_existing': True}
    feedbackid = db.Column(db.Integer, primary_key=True)
    customernumber = db.Column(db.Integer, db.ForeignKey('customer.customernumber'))
    feedbackdate = db.Column(db.Date, nullable=False)
    feedbacktext = db.Column(db.Text, nullable=False)

class Staff(db.Model):
    __tablename__ = 'staff'
    __table_args__ = {'extend_existing': True}
    staffid = db.Column(db.Integer, primary_key=True)
    staffname = db.Column(db.String, nullable=False)
    position = db.Column(db.String, nullable=False)
    staffdateadded = db.Column(db.Date, nullable=False)
    staffemail = db.Column(db.String, nullable=False)
    staffaddress = db.Column(db.String, nullable=False)
    storeid = db.Column(db.Integer, db.ForeignKey('bookstore.storeid'))

class Inventory(db.Model):
    __tablename__ = 'inventory'
    __table_args__ = {'extend_existing': True}
    inventoryid = db.Column(db.Integer, primary_key=True)
    bookid = db.Column(db.String, db.ForeignKey('book.isbn'))
    quantity = db.Column(db.Integer, nullable=False)
    supplierid = db.Column(db.Integer, db.ForeignKey('supplier.supplierid'))
    storeid = db.Column(db.Integer, db.ForeignKey('bookstore.storeid'))

class Contracts(db.Model):
    __tablename__ = 'contracts'
    __table_args__ = {'extend_existing': True}
    contractid = db.Column(db.Integer, primary_key=True)
    supplierid = db.Column(db.Integer, db.ForeignKey('supplier.supplierid'))
    idpublisher = db.Column(db.String, db.ForeignKey('publisher.idpublisher'))
    startdate = db.Column(db.Date, nullable=False)
    enddate = db.Column(db.Date, nullable=False)
    contractdetails = db.Column(db.Text, nullable=False)

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    __table_args__ = {'extend_existing': True}
    wishlistitemid = db.Column(db.Integer, primary_key=True)
    customernumber = db.Column(db.Integer, db.ForeignKey('customer.customernumber'))
    totalprice = db.Column(db.Float, nullable=False)
    wishlistquantity = db.Column(db.Integer, nullable=False)

class WishlistItems(db.Model):
    __tablename__ = 'wishlistitems'
    __table_args__ = {'extend_existing': True}
    wishlistitemid = db.Column(db.Integer, db.ForeignKey('wishlist.wishlistitemid'), primary_key=True)
    isbn = db.Column(db.String, db.ForeignKey('book.isbn'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)


def init_db():
    db.create_all()

def to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Manager.to_dict = to_dict
Publisher.to_dict = to_dict
Book.to_dict = to_dict
BookStore.to_dict = to_dict
Author.to_dict = to_dict
BookAuthors.to_dict = to_dict
BookGenre.to_dict = to_dict
BookBookGenre.to_dict = to_dict
Supplier.to_dict = to_dict
SupplierBooks.to_dict = to_dict
OrderSupplies.to_dict = to_dict
Customer.to_dict = to_dict
OnlineAccount.to_dict = to_dict
BookReviews.to_dict = to_dict
CustomerFeedback.to_dict = to_dict
Staff.to_dict = to_dict
Inventory.to_dict = to_dict
Contracts.to_dict = to_dict
Wishlist.to_dict = to_dict
WishlistItems.to_dict = to_dict
