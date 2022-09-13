from flask import Flask,render_template,request,redirect,session
import pymongo
import re
app = Flask(__name__)
app.config["DEBUG"] = True
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
item = mydb["item"]
owned = mydb["owned"]
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
        d["budget"]=1500
        


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
######LOGIN ##########################

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
        d["id"] = request.form["id"]
        d["name2"]= request.form["name"]
        d["name"]=session["name"]
        
        d["price"]=request.form["price"]
        d["barcode"] = request.form["barcode"]
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

    
   
    
@app.route('/purchase',methods=['GET', 'POST'])
def purchase():
    if "name" in session:
        current_user=session["name"]
        if request.method == "POST":
            name2 = request.form["purchased_item"]
            price = 0
            budget=0
            budget2=0
            name=""
            barcode=""
            description=""
            j=0
            k=0
            d=dict()
            for i in item.find({"name2":name2}):
                price = i["price"]
                name2 = i["name2"]
                name = i["name"]
                barcode = i["barcode"]
                description = i["description"]
                price = int(price)
                
            for i in myregis.find({"name":session["name"]}):
                budget = int(i["budget"])
                print(type(budget))
                j=budget-price
            myregis.update_one({"name":session["name"]},{"$set":{"budget":j}})
            d["name"]=session["name"]
            d["price"]=price
            d["name2"]=name2
            d["barcode"]=barcode
            d["description"]=description

            owned.insert_one(d)
            item.delete_one({"name2":name2})
            for i in myregis.find({"name":name}):
                budget2 = int(i["budget"])
                k=budget2+price
            myregis.update_one({"name":name},{"$set":{"budget":k}})


            print(j)
    else:
        return redirect('/login')

    return redirect('/market')

@app.route('/sell',methods=['GET', 'POST'])
def sell():
    if "name" in session:
        current_user=session["name"]
        if request.method == "POST":
            name2 = request.form["sold_item"]
            price = 0
            budget=0
            barcode=""
            description=""
            j=0
            d=dict()
            for i in owned.find({"name2":name2}):
                price = i["price"]
                name2 = i["name2"]
                barcode = i["barcode"]
                description = i["description"]
                price = int(price)
                
            for i in myregis.find({"name":session["name"]}):
                budget = int(i["budget"])
                print(type(budget))
                j=budget+price
            #myregis.update_one({"name":session["name"]},{"$set":{"budget":j}})
            d["name"]=session["name"]
            d["price"]=price
            d["name2"]=name2
            d["barcode"]=barcode
            d["description"]=description
            
            item.insert_one(d)
            owned.delete_one({"name2":name2})
    else:
        return redirect('/login')
    return redirect('/market')

@app.route('/market')
def market():
    if "name" in session:

        user = myregis.find_one({"name":session['name']})
        current_user=session["name"]
        return render_template('market.html',items=item.find(),owns=owned.find(),**locals())
    else:
        user='Unknown'
        current_user='Unknown'
        return render_template('market.html',items=item.find(),owns=owned.find(),**locals())

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