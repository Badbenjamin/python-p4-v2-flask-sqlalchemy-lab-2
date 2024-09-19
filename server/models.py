from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin


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


class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    __table_args__ = (db.CheckConstraint('name != ""', name='ck_name_not_blank'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    # relationship to review table created. 
    # customer.reviews gives list of reviews
    # one customer can have multiple reviews
    reviews = db.relationship('Review', back_populates='customer')

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
    reviews = db.relationship('Review', back_populates='item')

    serialize_rules = ['-reviews.item']

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'
