import os
import sys

from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''

#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['GET'])
@requires_auth('get:drinks')
def get_drinks(p):
    try:
        drinks = Drink.query.all()
        result = {}
        for d in drinks:
            result[d.title] = d.short()
        return jsonify(result)
    except:
        print(sys.exc_info())
        abort(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(p):
    try:
        drinks = Drink.query.all()
        result = {}
        for d in drinks:
            result[d.title] = d.long()
        return jsonify(result)
    except:
        print(sys.exc_info())
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def create_drink(p):
    try:
        data = json.loads(request.data)
        drink = Drink(title=data['title'],recipe=json.dumps(data['recipe']))
        drink.insert()
        return jsonify({
            'success':True,
            'drinks':[{
                'id':drink.id,
                'title':drink.title,
                'recipe':drink.recipe
            }]
        })
    except:
        print(sys.exc_info())
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(p,id):
    try:
        data = json.loads(request.data)
        drink = Drink.query.filter_by(id=id).first()
        drink.title = drink.title if not data['title'] else data['title']
        drink.recipe = drink.recipe if not data['recipe'] else json.dumps(data['recipe'])
        drink.update()
        return jsonify({
            'success':True,
            'drinks':{
                'title':drink.title,
                'recipe':drink.recipe
            }
        })
    except:
        print(sys.exc_info())
        abort(404)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(p,id):
    try:
        drink = Drink.query.filter_by(id=id).first()
        drink.delete()
        return jsonify({'success':True,'delete':id})
    except:
        print(sys.exc_info())
        abort (404)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':'not found'
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    #e = error.get_response()
    return jsonify({
        'success':False,
        'error':error.status_code,
        'message':error.error
    }), error.status_code