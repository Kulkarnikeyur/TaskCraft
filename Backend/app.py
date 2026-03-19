from flask import Flask,render_template,request,redirect,session,flash
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
import certifi

app= Flask(__name__, template_folder="../Frontend/templates",static_folder="../Frontend/static")

load_dotenv()
client = MongoClient(
    os.getenv("database_url"),
    tlsCAFile=certifi.where()
)
db = client["taskcraft"]
app.secret_key= os.getenv("secret_key")

@app.route("/")
def hello():
    return render_template("main.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signclick",methods=["post"])
def click1():
    print(request.form["id"])
    print(request.form["pass"])

    users_collection = db["landing"]

    existing_user = users_collection.find_one({
        "userid": request.form["id"]
    })

    if existing_user:
        flash("User ID already exists. Please choose another one.")
        return redirect("/signup")
    
    user = users_collection.insert_one({
        "userid": request.form["id"],
        "password": request.form["pass"]
    })

    session['user_mid'] = str(user.inserted_id)
    
    print(f"New user registered with num: {session['user_mid']}")

    return redirect("/landing")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/loginclick', methods=['POST'])
def ogclick():
    if request.method == 'POST':
        user_id = request.form['user_id'].strip()
        password = request.form['password'].strip()
        
        users_collection = db["landing"]
            # Check if user exists
        user = users_collection.find_one({
            "userid": user_id
        })

        if user is None:
                # Case 2: User doesn't exist at all
            flash('No user found with these credentials. Please sign up if you haven\'t already.')
            return render_template('login.html')
            
        elif str(user["password"]) != password:
                # Case 1: User exists but password is wrong
            flash('Wrong User ID or Password. Please try again.')
            return render_template('login.html')
            
        else:
                # Case 3: Both match - successful login
            session['user_mid'] = str(user["_id"])
            return redirect("/landing")

@app.route("/logout")
def logout():
    user_mid = session['user_mid']
    users_collection = db["landing"]

    users_collection.delete_one({
        "_id" : ObjectId(user_mid)
    })

    return redirect("/")

@app.route("/logout2")
def log():
    try:
        session.pop("user_mid")
    except KeyError:
        pass
    return redirect("/")

@app.route("/landing")
def land():
    user_mid = session['user_mid']
    
    users_collection = db["landing"]

    user = users_collection.find_one({"_id":ObjectId(user_mid)})
    username = user["userid"]
    return render_template("landing.html", username = username)


@app.route("/bill")
def finance():
    user_mid = session['user_mid']
    
    users_collection = db["finance_tracker"]

    bills = list(users_collection.find({"user_mid":ObjectId(user_mid)},{
        "_id" : 1,
        "date": 1,
        "description" : 1, 
        "amount":1

    }).sort("date",1))

    result = list(users_collection.aggregate([
        {
            "$match": {"user_mid": ObjectId(user_mid)}
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]))
    total = result[0]["total"] if result else 0
    print(total)

    return render_template("finance.html",expenses=bills,total=total)

@app.route("/addexpense",methods=["post"])
def click2():
    user_mid = session['user_mid']
    
    users_collection = db["finance_tracker"]

    users_collection.insert_one({
        "user_mid" : ObjectId(user_mid),
        "date" : request.form["trans-date"],
        "description" : request.form["trans-desc"],
        "amount" : float(request.form["trans-amount"])
    })

    return redirect("/bill")

@app.route("/delexrow",methods=["post"])
def delex():

    user_mid = session['user_mid']
    id=request.form["row_id"]

    users_collection = db["finance_tracker"]

    users_collection.delete_one({
        "user_mid" : ObjectId(user_mid),
        "_id" : ObjectId(id)
    })
    
    return redirect("/bill")

@app.route("/password")
def password():
    user_mid = session['user_mid']
    
    users_collection = db["password_manager"]

    passwords = list(users_collection.find({
        "user_mid":ObjectId(user_mid)
    },{
        "_id" : 1, 
        "website_name" : 1,
        "login_id" : 1,
        "password" : 1
    }))

    return render_template("password.html",passwords=passwords)

@app.route("/addpassword",methods=["post"])
def click3():
    user_mid = session['user_mid']
    
    users_collection = db["password_manager"]

    users_collection.insert_one({
        "user_mid" : ObjectId(user_mid),
        "website_name" : request.form["website"],
        "login_id" : request.form["loginid"],
        "password" : request.form["password"]
    })

    return redirect("/password")

@app.route("/delpasrow",methods=["post"])
def delpas():
    user_mid = session['user_mid']
    id=request.form["row_id"]

    users_collection = db["password_manager"]

    users_collection.delete_one({
        "user_mid" : ObjectId(user_mid),
        "_id" : ObjectId(id)
    })

    return redirect("/password")

@app.route("/time")
def time():
    return render_template("time.html")

@app.route("/deadline")
def deadline():
    user_mid = session['user_mid']
    
    users_collection = db["deadline_tracker"]
    
    deadlines = list(users_collection.find({
        "user_mid" : ObjectId(user_mid)
    },
    {
        "_id" : 1,
        "name" : 1,
        "status" : 1,
        "date" : 1,
        "time" : 1
    }).sort("date" , 1))

    return render_template("deadlines.html",deadlines=deadlines)

@app.route("/adddeadline",methods=["post"])
def click4():
    user_mid = session['user_mid']
    
    users_collection = db["deadline_tracker"]
    
    users_collection.insert_one({
        "user_mid" : ObjectId(user_mid),
        "name" : request.form["name"],
        "status" : request.form["status"],
        "date" : request.form["date"],
        "time" : request.form["time"]
    })

    return redirect("/deadline")

@app.route("/deldlrow",methods=["post"])
def deldl():
    user_mid = session['user_mid']
    id=request.form["row_id"]

    users_collection = db["deadline_tracker"]

    users_collection.delete_one({
        "user_mid":ObjectId(user_mid),
        "_id" : ObjectId(id)
    })

    return redirect("/deadline")

if __name__=="__main__":
    app.run(debug=True)
