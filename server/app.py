# remember to import request
from flask import Flask, request
from flask_migrate import Migrate
from sqlalchemy_serializer import SerializerMixin
from models import db, Customer, Item, Review


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Flask SQLAlchemy Lab 2</h1>'

@app.route('/customer', methods=['GET', 'POST'])
def customers():
    if request.method == 'GET':
        customers = Customer.query.all()
        customer_list=[]
        for customer in customers:
            customer_list.append(customer.to_dict())
        return customer_list
    if request.method == 'POST':
        data = request.get_json()
        new_customer = Customer(
            name=data.get('name'),
        )
        db.session.add(new_customer)
        db.session.commit()
        return new_customer.to_dict(), 200
    
@app.route('/customer/<int:id>', methods=['GET','PATCH', 'DELETE'])
def one_customer(id):
    customer = Customer.query.filter(Customer.id == id).first()
    if request.method == 'GET':
        return customer.to_dict()
    elif request.method == 'PATCH':
        data = request.get_json()
        # print(customer.name)
        for field in data:
            setattr(customer, field, data[field])
        db.session.add(customer)
        db.session.commit()
        return customer.to_dict(), 200
    elif request.method == 'DELETE':
        db.session.delete(customer)
        db.session.commit()
        return {}, 200
    
@app.route('/reviews', methods=['GET', 'POST'])
def get_reviews():
    reviews = Review.query.all()
    if request.method == 'GET':
        review_list = []
        for review in reviews:
            review_list.append(review.to_dict())
        return review_list, 200
    if request.method == 'POST':
        data = request.get_json()
        new_review = Review(
            comment=data.get('comment'),
            customer_id=data.get('customer_id'),
            item_id=data.get('item_id')
        )
        db.session.add(new_review)
        db.session.commit()
        return new_review.to_dict(), 200
    
# get all items, new syntax for single request type
@app.get('/items')
def get_all_items():
    items = Item.query.all()
    # to_dict takes serialization rules as an arg
    return [item.to_dict(rules=['-reviews']) for item in items], 200

# post item
@app.post('/items')
def post_items():
    data = request.get_json()
    new_item =  Item(
        name=data.get('name'),
        price=data.get('price')
    )
    db.session.add(new_item)
    db.session.commit()
    return new_item.to_dict(), 201
# get item by id
@app.get('/items/<int:id>')
def get_item_by_id(id):
    item = Item.query.filter(Item.id == id).first()

    if item is None:
        return {'error' : 'item not found'}, 404
    else:
        return item.to_dict(), 200

# patch item by id
@app.patch('/items/<int:id>')
def patch_item_by_id(id):
    item = Item.query.filter(Item.id == id).first()
    data = request.get_json()
    # grab json data, loop through json data, set attribute on item using json data
    for attr in data:
        if attr not in ['id']:
            setattr(item, attr, data[attr])
    db.session.add(item)
    db.session.commit()
    return item.to_dict(), 200
    

# delete item by id
@app.delete('/items/<int:id>')
def delete_item(id):
    item = Item.query.filter(Item.id == id).first()
    if item is None:
        return {'error' : "item does not exits"}, 404
    else:
        db.session.delete(item)
        db.session.commit()
        return {}, 200




if __name__ == '__main__':
    app.run(port=5555, debug=True)
