from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

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
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

    # relationship created btw Review table and Customer and Item tables
    # review.customer or item will give the customer or item object 
    # each review only has one item or customer
    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')

    # exclude item and customer reviews from serializaton because each review would contain reviews, and so on
    serialize_rules = ['-customer.reviews', '-item.reviews']

    def __repr__(self):
        return f'<Review {self.id}>'


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
