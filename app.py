from email.policy import default
from flask import Flask,  request, jsonify, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from datetime import timedelta

# create an instance of flask
app = Flask(__name__)
# creating an API object
api = Api(app)
# create database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emp.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#sqlalchemy mapper
db = SQLAlchemy(app)

# Table to store user data
class User(db.Model):
    userName = db.Column(db.String(80), primary_key=True)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    lastContributionDate = db.Column(db.String(80), default = None)
    streak = db.Column(db.Integer,default = 0)

    def __repr__(self):
        return f"{self.userName} | {self.firstName} | {self.lastName} | {self.lastContributionDate} | {self.streak}"



#To get all user data
class GetUser(Resource):
    def get(self):
        users = User.query.all()
        user_list = []
        for user in users:
            user_data = {'UserName': user.userName, 'FirstName': user.firstName, 'LastName': user.lastName, 'LastContributionDate': user.lastContributionDate,
                        'Streak': user.streak}
            user_list.append(user_data)
        return {"Users": user_list}, 200

#Add user to USER table 
class AddUser(Resource):
    def post(self):
        if request.is_json:
            user = User(userName=request.json['UserName'], firstName=request.json['FirstName'], lastName=request.json['LastName'])
            db.session.add(user)
            db.session.commit()
            # return a json response
            return make_response(jsonify({'UserName': user.userName, 'FirstName': user.firstName, 'LastName': user.lastName,
                                          'LastContributionDate': user.lastContributionDate, 'Streak': user.streak}), 201)
        else:
            return {'error': 'Request must be JSON'}, 400

#Uodate contribution date of user
class AddContribution(Resource):
    def put(self, userName):
        user = User.query.get(userName)
        if user is None:
            return {'error': 'user not found'}, 404
        else:
            today = date.today()
            yesterday = today - timedelta(days = 1)
            today = str(today)
            yesterday = str(yesterday)
            lastContributionDate = user.lastContributionDate
            user.lastContributionDate = today
            # print(today,flush=True)
            if lastContributionDate == today:
                return 'Updated', 200
            elif lastContributionDate == yesterday:
                user.streak += 1
            else:
                user.streak = 1
            db.session.commit()
            return 'Updated', 200

class GetStreak(Resource):
    def get(self, userName):
        user = User.query.get(userName)
        if user is None:
            return {'error': 'user not found'}, 404
        else:
            streak = 0
            today = date.today()
            yesterday = today - timedelta(days = 1)
            lastContributionDate = str(user.lastContributionDate)
            today = str(today)
            yesterday = str(yesterday)
            print(today,flush=True)
            if lastContributionDate == today or lastContributionDate == yesterday:
                streak = user.streak
            else:
                streak = 0
            user_data = {'UserName': user.userName,'Streak': streak}
            return user_data, 200


api.add_resource(GetUser, '/')
api.add_resource(AddUser, '/addUser')
api.add_resource(AddContribution, '/addContribution/<string:userName>')
api.add_resource(GetStreak, '/getStreak/<string:userName>')

#
if __name__ == '__main__':
    app.run(debug=True)
 