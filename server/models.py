from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt
from sqlalchemy.ext.hybrid import hybrid_property


# naming convention for db constraints (fixes an alembic bug)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


# init sqlalchemy object
db = SQLAlchemy(metadata=MetaData(naming_convention=convention))

# init bcrypt
bcrypt = Bcrypt()


class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    __table_args__ = (db.CheckConstraint('name != ""', name='ck_name_not_blank'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    # relationship to review table created. 
    # customer.reviews gives list of reviews
    # one customer can have multiple reviews
    # cascade arg will delete reviews that are orphaned when customer is deleted
    reviews = db.relationship('Review', back_populates='customer', cascade='all, delete-orphan')

    # creates a link btw cusomer and item
    # customer.item can be called
    items = association_proxy('reviews', 'item')
    
    # to prevent a reccursive loop, the customer object is excluded from the Serializer
    # this is becasue the customer object contains reviews, which contain the customer. 
    serialize_rules = ['-reviews.customer']

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'
    
class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    # Join table, needs foreign keys because a review has 1 customer and 1 item, each with an ID
    # foreign key references table name
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

    # relationship created btw Review table and Customer and Item tables
    # review.customer or item will give the customer or item object 
    # each review only has one item or customer
    # app layer relationship 
    # backpopulates arg looks for variable(column name) in table/class with relationship
    customer = db.relationship('Customer', back_populates='reviews')
    # Item class/table back populates reviews attribute on item
    # this is invisable in the DB but exists in app layer
    item = db.relationship('Item', back_populates='reviews')

    # exclude item and customer reviews from serializaton because each review would contain reviews, and so on
    serialize_rules = ['-customer.reviews', '-item.reviews']

    @validates('comment')
    def validate_comment(self, key, new_comment):
        print(key)
        if len(new_comment) <= 0:
            
            raise ValueError("need to leave a comment")
        return new_comment


    def __repr__(self):
        return f'<Review {self.id}, {self.comment}, {self.customer_id}, {self.item_id}>'


class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    # relationship created to Review
    # item.reviews will give the item's reviews
    # one item can have multiple reviews
    # if item is deleted, reviews (now orphaned, no item), will be deleted 
    reviews = db.relationship('Review', back_populates='item', cascade='all, delete-orphan')

    serialize_rules = ['-reviews.item']

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'
    

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String)

    # kind of like getter function
    # user.password calls password(self) and returns password_hash
    @hybrid_property
    def password(self):
        """return pw hash"""
        return self.password_hash
    
    # kind of like setter function
    #  takes a plain text pw and sets self.password_hash to the hashed pw 
    @password.setter
    def password(self, plain_text_pw):
        """hashes the plain text pw"""
        bytes = plain_text_pw.encode('utf-8') # convert pt_pw into raw bytes
        self.password_hash = bcrypt.generate_password_hash(bytes) #hash the bytes

    
    # this function is used to test if a given password matches the user's pw
    # if user.authenticate("pw") returns true, then the password hash matches the one in the DB
    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self.password_hash, #hashed pw
            password.encode('utf-8') # plain text pw
        )