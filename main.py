from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource
from flask_restful import Api
from flask_restful import fields
from flask_restful import marshal_with
from flask_restful import reqparse
from werkzeug.exceptions import HTTPException
from datetime import datetime as d
import os
import json
current_dir = os.path.abspath(os.path.dirname(__file__))

api = None
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "kanban1.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy()
db.init_app(app)
api = Api(app)
app.app_context().push()

#ERROR CLASSES

class Success(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)
        
class listNotFound(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)
        
class listExists(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)
        
class C1e(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)
		
class C2e(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)

class C3e(HTTPException):
    def __init__(self, status_code, error_code, error_msg):
        self.response = make_response('', status_code)

class cardNotFound(HTTPException):
    def __init__(self, status_code, error_msg):
        self.response = make_response('', status_code, {"Content-Type": "application/json"})
        
class cardExists(HTTPException):
    def __init__(self, status_code, error_msg):
        self.response = make_response('', status_code, {"Content-Type": "application/json"})
        
class S1e(HTTPException):
    def __init__(self, status_code, error_code, error_msg):
        message = {"error_code": error_code, "error_message": error_msg}
        self.response = make_response(json.dumps(message), status_code, {"Content-Type": "application/json"})
		
class S2e(HTTPException):
    def __init__(self, status_code, error_code, error_msg):
        message = {"error_code": error_code, "error_message": error_msg}
        self.response = make_response(json.dumps(message), status_code, {"Content-Type": "application/json"})

class S3e(HTTPException):
    def __init__(self, status_code, error_code, error_msg):
        message = {"error_code": error_code, "error_message": error_msg}
        self.response = make_response(json.dumps(message), status_code, {"Content-Type": "application/json"})
        
#LIST API

list_format = {
  "lusername": fields.String,
  "lname": fields.String,
  "ldesc": fields.String
}

list_parser = reqparse.RequestParser()
list_parser.add_argument("lusername")
list_parser.add_argument("lname")
list_parser.add_argument("ldesc")

class Listapi(Resource):
    def get(self,name):
        lists = List.query.filter_by(lusername = name).all()
        if lists:
            listofnames = []
            for li in lists:
                listofnames.append(li.lname)
            return {"listnames" : listofnames}
        else:
            raise listNotFound(status_code=404)
        
    @marshal_with(list_format)
    def put(self,name,listname):
        lists = List.query.filter_by(lusername = name,lname = listname).first()
        if lists:
            args = list_parser.parse_args()
            username = args.get("lusername", None)
            listname1 = args.get("lname", None)
            description = args.get("ldesc", None)
            
            if (type(username) is str) and (username is not None):
                if (type(listname) is str) and (listname is not None) :
                    if (description is None)or(type(description) is str):
                        lists.lname = listname1
                        lists.ldesc = description
                        db.session.commit()
                        lists = List.query.filter_by(lusername = username,lname = listname1).first()
                        return lists, 200
                    else:
                        raise C3e(status_code=400)
                else:
                    raise C2e(status_code=400)
            else:
                raise C1e(status_code=400)
        else:
            raise listNotFound(status_code=404)
            
    @marshal_with(list_format)          
    def post(self,name):
        args = list_parser.parse_args()
        username = args.get("lusername", None)
        listname = args.get("lname", None)
        description = args.get("ldesc", None)
        
        if (type(username) is str) and (name is not None):
            if (type(listname) is str) and (listname is not None) :
                if (description is None) or (type(description) is str):
                    lists = List.query.filter_by(lusername = username,lname = listname).first()
                    if lists:
                        raise listExists(status_code=401)
                    else:   
                        lists = List(lusername = username, lname = listname, ldesc = description )
                        db.session.add(lists)
                        db.session.commit()
                        lists = List.query.filter_by(lusername = username,lname = listname).first()
                        return lists, 201
                else:
                    raise C3e(status_code=400)
            else:
                raise C2e(status_code=400)
        else:
            raise C1e(status_code=400)
        
        
    def delete(self, list_name, name):
        lists = List.query.filter_by(lusername = name,lname = list_name).first()
        cards = Cards.query.filter_by(username = name,l_name = listname).all()
        if lists:
            for card in cards:
                db.session.delete(card)
            db.session.delete(lists)
            db.session.commit()
            raise Success(status_code=200)
        else:
            raise listNotFound(status_code=404)

# CARD API

card_format = {
  "username": fields.String,
  "l_name": fields.String,
  "c_name": fields.String,
  "c_content": fields.String,
  "c_deadline": fields.String,
  "c_off": fields.String
}

card_parser = reqparse.RequestParser()
card_parser.add_argument("username")
card_parser.add_argument("l_name")
card_parser.add_argument("c_name")
card_parser.add_argument("c_content")
card_parser.add_argument("c_deadline")
card_parser.add_argument("c_toggle")
       
class Cardapi(Resource):
    def get(self,name,listname ):
        cards = Cards.query.filter_by(username = name,l_name = listname).all()
        if cards:
            listofcards = []
            for ca in listofcards:
                listofcards.append(ca.c_name)
            return listofcards, 200
        else:
            raise listNotFound(status_code=404, error_msg='list not found')
            
    @marshal_with(card_format)
    def put(self, name,listname,card_name):
        cards = Cards.query.filter_by(username = name,l_name = listname,c_name = card_name).first()
        if cards:
            args = card_parser.parse_args()
            lname = args.get("l_name", None)
            cname = args.get("c_name", None)
            ccontent = args.get("c_content", None)
            cdeadline = args.get("c_deadline", None)
            ctoggle = args.get("c_toggle", None)
            today = d.today().strftime('%Y-%m-%d')
            if (type(lname) is str) and (lname is not None):
                if (type(cname) is str) and (cname is not None) :
                    if (type(ccontent) is str) and (ccontent is not None) :
                        if (type(cdeadline) is str) and (cdeadline is not None) :
                            if (type(ctoggle) is str) and (ctoggle is not None) :
                                cards.l_name = lname
                                cards.c_name = cname
                                cards.c_content = ccontent
                                cards.c_deadline = cdeadline
                                cards.c_toggle = ctoggle
                                cards.c_update = today
                                db.session.commit()
                                cards = Cards.query.filter_by(username = name,l_name = lname,c_name = cname).first()
                                return cards, 200
                    else:
                        raise S3e(status_code=400, error_code=error_dict['S3e'][0], error_msg=error_dict['S3e'][1])
                else:
                    raise S2e(status_code=400, error_code=error_dict['S2e'][0], error_msg=error_dict['S2e'][1])
            else:
                raise S1e(status_code=400, error_code=error_dict['S1e'][0], error_msg=error_dict['S1e'][1])
        else:
            raise listNotFound(status_code=404, error_msg='list not found')
            
    @marshal_with(card_format)
    def post(self,name,listname):
        args = card_parser.parse_args()
        lname = args.get("l_name", None)
        cname = args.get("c_name", None)
        ccontent = args.get("c_content", None)
        cdeadline = args.get("c_deadline", None)
        ctoggle = args.get("c_toggle", None)
        today = d.today().strftime('%Y-%m-%d')
        if (type(lname) is str) and (lname is not None):
            if (type(cname) is str) and (cname is not None) :
                if (type(ccontent) is str) and (ccontent is not None) :
                    if (type(cdeadline) is str) and (cdeadline is not None) :
                        if (type(ctoggle) is str) and (ctoggle is not None) :
                            cards = Cards.query.filter_by(username = name,l_name = listname,c_name = cname).first()
                        if cards:
                            raise cardExists(status_code=409, error_msg='card already exist')
                        else:   
                            cards = Cards(username = name,l_name = lname, c_name = cname,c_content = ccontent, c_deadline = cdeadline,c_toggle = ctoggle,c_update = today)
                            db.session.add(cards)
                            db.session.commit()
                            cards = Cards.query.filter_by(username = name,l_name = listname,c_name = cname).first()
                            return cards, 201
                else:
                    raise S3e(status_code=400, error_code=error_dict['S3e'][0], error_msg=error_dict['S3e'][1])
            else:
                raise S2e(status_code=400, error_code=error_dict['S2e'][0], error_msg=error_dict['S2e'][1])
        else:
            raise S1e(status_code=400, error_code=error_dict['S1e'][0], error_msg=error_dict['S1e'][1])
        
    def delete(self, name,listname,card_name):
        cards = Cards.query.filter_by(username = name,l_name = listname,c_name = card_name).first()
        if cards:
            db.session.delete(cards)
            db.session.commit()
            raise Success(status_code=200)
        else:
            raise cardNotFound(status_code=404, error_msg='Card not found')
        

api.add_resource(Listapi,"/api/home/list/<string:name>", "/api/home/editlist/<name>/<listname>", '/api/delete/<list_name>/<name>')
api.add_resource(Cardapi,"/api/createcard/<string:name>/<string:listname>", "/api/editcard/<string:name>/<string:listname>/<string:card_name>", "/api/deletecard/<string:listname>/<string:card_name>/<string:name>")

    
#sql tables
class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String, primary_key = True)
    password = db.Column(db.String)
    
class List(db.Model):
    __tablename__ = 'list'
    lusername = db.Column(db.String, primary_key = True)
    lname = db.Column(db.String, primary_key = True)
    ldesc = db.Column(db.String)
    lupdate = db.Column(db.String)

class Cards(db.Model):
    __tablename__ = "card"
    username = db.Column(db.String, primary_key = True)
    l_name = db.Column(db.String, primary_key = True)
    c_name = db.Column(db.String, primary_key = True)
    c_content = db.Column(db.String)
    c_deadline = db.Column(db.String)
    c_update = db.Column(db.String)
    c_toggle = db.Column(db.String)

#app routing
@app.route('/', methods = ['GET','POST'])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        name = request.form["user"]
        passw = request.form["pass"]
        dbuser = User.query.filter_by(username = name).first()
        if dbuser == None:
            return render_template("index.html",msg = "*USER DOES NOT EXIST")
        elif dbuser.password == passw:
            return redirect(url_for('home',name = name))
        else:
            return render_template("index.html",msg = "*INCORRECT PASSWORD")
            
@app.route('/signup' , methods = ['GET','POST'])
def sign():
    if request.method == "GET":
        return render_template("sign.html",msg = "")
    elif request.method == "POST":
        name = request.form["name"]
        uname = request.form["uname"]
        newpass = request.form["newpass"]
        repass = request.form["repass"]
        if newpass == repass:
            q = User.query.filter_by(username = name).first()
            if(q != None):
                return render_template("sign.html",msg = "*USER ALREADY EXISTS")
            else:
                newuser = User(username = uname,password = newpass)
                db.session.add(newuser)
                db.session.commit()
            return redirect(url_for("index"))
        else:
            return render_template("sign.html",msg = "*PASSWORDS DOES NOT MATCH")
          
@app.route('/home/<name>' , methods = ['GET','POST'])
def home(name):
    listret = List.query.filter_by(lusername = name).all()
    cards = Cards.query.all()
    return render_template("home.html",name = name,listret = listret,cards = cards)

@app.route('/delete/<list_name>/<name>' ,methods = ['GET','POST'])
def delete(list_name,name):
    dellist = List.query.filter_by(lusername = name,lname = list_name).first()
    delcard = Cards.query.filter_by(username = name,l_name = list_name).all()
    today = d.today().strftime('%Y-%m-%d')
    lists = List.query.filter_by(lusername = name, lname = list_name).first()
    lists.lupdate = today
    for card in delcard:
        db.session.delete(card)
    db.session.delete(dellist)
    db.session.commit()
    return redirect(url_for("home",name=name))

@app.route('/deletecard/<listname>/<card_name>/<name>' ,methods = ['GET','POST'])
def delete_card(card_name,name,listname):
    delcard = Cards.query.filter_by(username = name,l_name = listname, c_name = card_name).first()
    today = d.today().strftime('%Y-%m-%d')
    lists = List.query.filter_by(lusername = name, lname = listname).first()
    lists.lupdate = today
    db.session.delete(delcard)
    db.session.commit()
    return redirect(url_for("home",name=name))    

@app.route('/home/list/<name>' , methods = ['GET','POST'])
def list(name):
    if request.method == "GET":
        return render_template("list.html",name = name,msg = "")
    elif request.method == "POST":
        l_name = request.form["list_name"]
        l_area = request.form["list_area"]
        p = List.query.filter_by(lusername = name,lname = l_name).first()
        if( p != None):
            return render_template("list.html",name = name,msg = "*LIST ALREADY EXISTS")
        today = d.today().strftime('%Y-%m-%d')
        newli = List(lusername = name, lname = l_name, ldesc = l_area,lupdate = today)
        db.session.add(newli)
        db.session.commit()
        return redirect(url_for("home",name = name))

@app.route('/home/editlist/<name>/<listname>' , methods = ['GET','POST'])
def editlist(name,listname):
    if request.method == "GET":
        return render_template("editlist.html",name = name,msg = "",listname = listname)
    elif request.method == "POST":
        l_name = request.form["list_name"]
        l_area = request.form["list_area"]
        p = List.query.filter_by(lusername = name,lname = l_name).first()
        if( p != None):
            return render_template("editlist.html",name = name,msg = "*LIST ALREADY EXISTS",listname = listname)
        today = d.today().strftime('%Y-%m-%d')
        q = List.query.filter_by(lusername = name,lname = listname).first()
        newli = List(lusername = name, lname = l_name, ldesc = l_area,lupdate = today)
        cards = Cards.query.filter_by(username = name,l_name = listname).all()
        for i in cards:
            i.l_name = l_name
        db.session.delete(q)
        db.session.commit()
        db.session.add(newli)
        db.session.commit()
        return redirect(url_for("home",name = name))
    
@app.route('/createcard/<name>/<listname>' , methods = ['GET','POST'])
def createcard(name,listname):
    lists = List.query.filter_by(lusername = name).all()
    if request.method == "GET":
        return render_template("createcard.html",name = name,msg = "",lists = lists,listname = listname)
    if request.method == "POST":
        list_name = request.form["list"]
        title = request.form["title"]
        content = request.form["content"]
        deadline = request.form["deadline"]
        try:
            toggle = request.form["toggle"]
        except:
            toggle = "off"
        today = d.today().strftime('%Y-%m-%d')

        user1 = User.query.filter_by(username = name).first()
        if user1 == None:
            return render_template("createcard.html",name = name,msg = "*USER DOES NOT EXIST",lists = lists,listname = listname)
            
        if deadline >= today:
            new_card = Cards(username = name, l_name = list_name,c_name = title,c_content = content,c_deadline = deadline,c_toggle = toggle,c_update = today)
            lists = List.query.filter_by(lusername = name, lname = listname).first()
            lists.lupdate = today
            cardcheck = Cards.query.filter_by(username = name, l_name = list_name,c_name = title).first()
            if(cardcheck != None):
                return render_template("createcard.html",name = name,msg = "*CARD ALREADY EXISTS",lists = lists,listname = listname)
            db.session.add(new_card)
            db.session.commit()
            return redirect(url_for("home",name = name))
        else:
            return render_template("createcard.html",name = name,msg = "*YOU CANNOT TIMETRAVEL",lists = lists,listname = listname)
            
         
    
@app.route('/editcard/<name>/<listname>/<card_name>' , methods = ['GET','POST'])
def editcard(name,listname,card_name):
    lists = List.query.filter_by(lusername = name).all()
    if request.method == "GET":
        return render_template("editcard.html",name = name,msg = "",lists = lists,listname = listname,cardname = card_name)
    if request.method == "POST":
        list_name = request.form["list"]
        title = request.form["title"]
        content = request.form["content"]
        deadline = request.form["deadline"]
        try:
            toggle = request.form["toggle"]
        except:
            toggle = "off"
        today = d.today().strftime('%Y-%m-%d')
        if deadline >= today:
            new_card = Cards(username = name, l_name = list_name,c_name = title,c_content = content,c_deadline = deadline,c_toggle = toggle,c_update = today)
            lists = List.query.filter_by(lusername = name, lname = listname).first()
            lists.lupdate = today
            cardcheck = Cards.query.filter_by(username = name, l_name = list_name,c_name = title,c_content = content,c_deadline = deadline,c_toggle = toggle).first()
            cardcheck1 = Cards.query.filter_by(username = name, l_name = list_name,c_name = title).first()
            if(cardcheck != None or cardcheck1 != None):
                return render_template("editcard.html",name = name,msg = "*CARD ALREADY EXISTS",lists = lists,listname = listname,cardname = card_name)
            q = Cards.query.filter_by(username = name,l_name = listname,c_name = card_name).first()
            db.session.delete(q)
            db.session.commit()
            db.session.add(new_card)
            db.session.commit()
            return redirect(url_for("home",name = name))
        else:
            return render_template("createcard.html",name = name,msg = "*YOU CANNOT TIMETRAVEL",lists = lists,listname = listname)
             
@app.route('/home/summary/<name>' , methods = ['GET','POST'])
def summary(name):
    cards = Cards.query.all()
    listnames = []
    cardnames = []
    deadlines0 = []
    deadlines1 = []
    for card in cards:
        if card.username == name:
            if card.l_name not in listnames:
                listnames.append(card.l_name)
    for lists in listnames:
        count0 = 0
        count1 = 0
        for card in cards:
            if card.username == name:
                if card.l_name == lists:
                    if card.c_toggle == "off":
                        count0 = count0 + 1
                        
                    else:
                        count1 = count1 + 1
                        
        deadlines0.append(count0)
        deadlines1.append(count1)
        
        
            
    return render_template("summary.html",name = name,listnames=json.dumps(listnames),cardnames=cardnames,deadlines0=json.dumps(deadlines0),deadlines1=json.dumps(deadlines1))


if __name__ == "__main__":
    app.run(debug = True)
