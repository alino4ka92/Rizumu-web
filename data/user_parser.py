from flask_restful import reqparse
parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('email')
parser.add_argument('created_date')
parser.add_argument('avatar')