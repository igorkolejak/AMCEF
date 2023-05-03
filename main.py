import requests

from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

EXTERNAL_API = "https://jsonplaceholder.typicode.com/"
SWAGGER_URL = '/apidocs'
API_URL = '/static/swagger.yaml'

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.create_all()

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Test application"
    },
)
app.register_blueprint(swaggerui_blueprint)

post_put_args = reqparse.RequestParser()
post_put_args.add_argument("userId", type=int, help="User ID has to be specified.", required=True)
post_put_args.add_argument("title", type=str, help="Title has to be specified.", required=True)
post_put_args.add_argument("body", type=str, help="Body has to be specified.", required=True)

post_update_args = reqparse.RequestParser()
post_update_args.add_argument("title", type=str, help="Title has to be specified.")
post_update_args.add_argument("body", type=str, help="Body has to be specified.")

post_get_args = reqparse.RequestParser()
post_get_args.add_argument("userId", type=int, help="User ID has to be specified.")

resource_fields = {
    'id': fields.Integer,
    'userId': fields.Integer,
    'title': fields.String,
    'body': fields.String
}

class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Post(id = {self.id}, userId = {self.userId}, title = {self.title}, body = {self.body}"

class Post(Resource):
    @marshal_with(resource_fields)
    def get(self, post_id):
        args = post_get_args.parse_args()
        
        if args['userId'] and post_id == 0:
            result = PostModel.query.filter_by(userId=args['userId']).all()
            if not result:
                abort(404, message = "User ID \"" + str(args['userId']) + '\" not found.')
        else:
            result = PostModel.query.filter_by(id=post_id).first()
            if result is None:
                response = requests.get(EXTERNAL_API + "posts/" + str(post_id))
                if response.json() == {}:
                    abort(400, message = "Get failed: Invalid ID \"" + str(post_id) + '\".')
                else:
                    result = PostModel(id=post_id, userId=response.json()['userId'], title=response.json()['title'], body=response.json()['body'])
                    db.session.add(result)
                    db.session.commit()
        return result

    @marshal_with(resource_fields)
    def put(self, post_id):
        args = post_put_args.parse_args()
        response = requests.get(EXTERNAL_API + "users/" + str(args['userId']))
        if not response:
            abort(404, message = "Insert failed: User ID \"" + str(args['userId']) + '\" does not exist.')
        try:
            post = PostModel(id=post_id, userId=args['userId'], title=args['title'], body=args['body'])
            db.session.add(post)
            db.session.commit()
        except:
            abort(400, message = "Insert failed: Post with id \"" + str(post_id) + '\" already exist.')
        return post

    @marshal_with(resource_fields)
    def patch(self, post_id):
        args = post_update_args.parse_args()
        post = PostModel.query.filter_by(id=post_id).first()

        if post is None:
            abort(400, message = "Update failed: Post with id \"" + str(post_id) + '\" does not exist.')

        if args['title']:
            post.title = args['title']
        if args['body']:
            post.body = args['body']
        try:
            db.session.commit()
        except:
            abort(404, message = "Update failed: Unable to update post with id \"" + str(post_id) + '\".')

        return post

    def delete(self, post_id):
        post = PostModel.query.filter_by(id=post_id).first()
        if post:
            try:
                db.session.delete(post)
                db.session.commit()
            except:
                abort(400, message = "Delete failed: Post with id \"" + str(post_id) + '\" does not exist.')
        return {'message': 'Delete sucessful.' }, 200

api.add_resource(Post, "/post/<int:post_id>")

if __name__ == "__main__":
    app.run(debug=True)
