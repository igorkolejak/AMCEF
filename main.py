from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

import requests

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
db.create_all()

post_put_args = reqparse.RequestParser()
post_put_args.add_argument("userId", type=int, help="User ID has to be specified.", required=True)
post_put_args.add_argument("title", type=str, help="Title has to be specified.", required=True)
post_put_args.add_argument("body", type=str, help="Body has to be specified.", required=True)

post_update_args = reqparse.RequestParser()
post_update_args.add_argument("title", type=str, help="Title has to be specified.")
post_update_args.add_argument("body", type=str, help="Body has to be specified.")

post_get_args = reqparse.RequestParser()
post_get_args.add_argument("userId", type=int, help="User ID has to be specified.")

EXTERNAL_API = "https://jsonplaceholder.typicode.com/"

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
    if args['userId']:
      result = PostModel.query.filter_by(userId=args['userId']).all()
      print(result)
    else:
      result = PostModel.query.filter_by(id=post_id).first()
      print(result)
    if not result:
      response = requests.get(EXTERNAL_API + "posts/" + str(post_id))
      if response:
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
      abort(404, message = "Insert failed: Post with id \"" + str(post_id) + '\" already exist.')
    return post

  @marshal_with(resource_fields)
  def patch(self, post_id):
    args = post_update_args.parse_args()
    post = PostModel.query.filter_by(id=post_id).first()
    if not post:
      post = requests.get(EXTERNAL_API + "posts/" + str(post_id))
    try:
      if args['title']:
        post.title = args['title']
      if args['body']:
        post.body = args['body']
      db.session.commit()
    except:
      abort(404, message = "Insert failed: Post with id \"" + str(post_id) + '\" already exist.')
    return post

  def delete(self, post_id):
    post = PostModel.query.filter_by(id=post_id).first()
    if post:
      db.session.delete(post)
      db.session.commit()
    return {'message': 'Delete sucessful.' }, 200

api.add_resource(Post, "/post/<int:post_id>")

if __name__ == "__main__":
  app.run(debug=True)
