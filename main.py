from flask import Flask,render_template,request,redirect,session
import pymongo
import re
app = Flask(__name__)
app.config["DEBUG"] = True
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
item = mydb["item"]
myregis = mydb["myregi"]
app.config['SECRET_KEY'] = 'Thisisasecret'


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    s=""
    passMsg=""
    emailMsg=""
    nameMsg=""
    successMsg=""
    
    
    if request.method =="POST":
        d=dict()
        d["name"]= request.form["name"]
        d["email"] = request.form["email"]
        d["password1"]=request.form["password1"]
        d["password2"] = request.form["password2"]
        
        

        if d["password1"]==d["password2"] and re.fullmatch(regex,d["email"]):
            successMsg="Registration Successful"
            myregis.insert_one(d)
            return render_template("login.html", successMsg=successMsg)
        
        elif d["password1"]!=d["password2"] :
            passMsg="Password Are not same ,please enter same password"
            return render_template("registration.html", passMsg=passMsg)
        else:
            emailMsg = "please enter correct email"
            return render_template("registration.html", emailMsg=emailMsg)


    return render_template("registration.html" , **locals())



@app.route('/login', methods=['GET', 'POST'])
def login():
    s =""
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydatabase"]
    myregis = mydb["myregi"]
    if request.method == "POST":

        d = request.form["name"]
        p = request.form["password"]
        for i in myregis.find({"name":d}):
            if p==i["password1"]:
                s="Login successful"
                session["name"]=d
                print(session["name"])
                #return render_template("login.html", s=s)
                return redirect('/home')
            elif p!=i["password1"]:
                s="Login Unsuccessful"
                return render_template("login.html", s=s)
            else:
                s="User Not Found"
                return render_template("login.html", s=s)

    return render_template("login.html", s=s)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logoutMsg = "You are logged out"
    #session.clear()
    session.pop("name",None)
    print(session)
    return render_template('login.html',s=logoutMsg) 


@app.route('/item',methods=['GET', 'POST'])
def item_page():
    user = myregis.find_one({"name":session['name']})
    current_user=session["name"]
    if request.method =="POST":
        d=dict()
       
        d["name"] = request.form["name"]
        d["email"] = request.form["email"]
        d["type"] = request.form["type"]
        d["description"] = request.form["description"]
        
        item.insert_one(d)
    return render_template("itemAdd.html",message="Item added successfully",**locals())


@app.route('/')
@app.route('/home')
def homepage():
    if "name" in session:
        user = myregis.find_one({"name":session['name']})
        current_user=session["name"]
        return render_template("home.html",**locals())
    else:
        user='Unknown'
        current_user='Unknown'
        return render_template("home.html",**locals())


@app.route('/profile')
def profile():
    if "name" in session:
        user = myregis.find_one({"name":session['name']})
        current_user=session["name"]
        return render_template('userprofile.html',owns=owned.find(),**locals())
    else:
        user='Unknown'
        current_user='Unknown'
        return render_template('userprofile.html',**locals())

if __name__ == '__main__':
    app.run()