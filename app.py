from flask import Flask,render_template,request,redirect,session,flash
import psycopg2
from urllib.parse import urlparse
app= Flask(__name__)


def get_db_connection():
    # Construct your database URL
    database_url = "postgresql://zense_website_user:6h9qYaF9mSoMDog85k0ErtH2PZGWczYu@dpg-d2asj6buibrs73f0n81g-a.singapore-postgres.render.com/zense_website"
    
    # Parse the URL
    parsed_url = urlparse(database_url)
    
    conn = psycopg2.connect(
        host=parsed_url.hostname,
        database=parsed_url.path[1:],  # Remove the leading '/'
        user=parsed_url.username,
        password=parsed_url.password,
        port=parsed_url.port
    )
    return conn
app.secret_key="kkeyur"
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
    mydb = get_db_connection()
    cursor = mydb.cursor()
    sql="insert into landing (userid,password) values(%s,%s)"
    values=(request.form["id"],request.form["pass"])
    cursor.execute(sql,values)
    mydb.commit()
    

    cursor.execute("SELECT num, userid FROM landing WHERE userid = %s AND password = %s", (request.form["id"], request.form["pass"]))
    user = cursor.fetchone()

    session['user_num'] = user[0]
    cursor.close()
    mydb.close()
        
    print(f"New user registered with num: {session['user_num']}")

    cursor.close()
    mydb.close()

    return redirect("/landing")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/loginclick', methods=['POST'])
def ogclick():
    if request.method == 'POST':
        user_id = request.form['user_id'].strip()
        password = request.form['password'].strip()
        
        conn = get_db_connection()
        cur = conn.cursor()
            # Check if user exists
        cur.execute('SELECT num,userid, password FROM landing WHERE userid = %s', (user_id,))
        user = cur.fetchone()

        if user is None:
                # Case 2: User doesn't exist at all
            flash('No user found with these credentials. Please sign up if you haven\'t already.')
            return render_template('login.html')
            
        elif user[2] != password:
                # Case 1: User exists but password is wrong
            flash('Wrong User ID or Password. Please try again.')
            return render_template('login.html')
            
        else:
                # Case 3: Both match - successful login
            session['user_num'] = user[0]
            return redirect("/landing")

@app.route("/logout")
def logout():
    user_num = session['user_num']
    mydb = get_db_connection()
    cursor = mydb.cursor()
    sql="delete from landing where num = %s"

    cursor.execute(sql,(user_num,))
    mydb.commit()

    cursor.close()
    mydb.close()

    return redirect("/")
@app.route("/logout2")
def log():
    session.pop("user_num")
    return redirect("/")
@app.route("/landing")
def land():
    return render_template("landing.html")


@app.route("/bill")
def finance():
    user_num = session['user_num']
    
    mydb = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT id, date, description, amount FROM finance_tracker WHERE user_num = %s ORDER BY date", (user_num,))
    bills = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM finance_tracker where user_num = %s",(user_num,))

    total = cursor.fetchone()
    print(total)
    cursor.close()
    mydb.close()

    return render_template("finance.html",expenses=bills,total=total)

@app.route("/addexpense",methods=["post"])
def click2():
    user_num = session['user_num']
    
    mydb = get_db_connection()
    cursor = mydb.cursor()
    sql="Insert into finance_tracker (user_num,date, description, amount) values(%s,%s,%s,%s)"

    cursor.execute(sql,(user_num,request.form["trans-date"],request.form["trans-desc"],request.form["trans-amount"]))
    mydb.commit()

    cursor.close()
    mydb.close()

    return redirect("/bill")

@app.route("/delexrow",methods=["post"])
def delex():

    user_num = session['user_num']
    id=request.form["row_id"]
    mydb = get_db_connection()
    cursor = mydb.cursor()
    sql="delete from finance_tracker where user_num = %s AND id= %s"

    cursor.execute(sql,(user_num,id))
    mydb.commit()

    cursor.close()
    mydb.close()
    return redirect("/bill")

@app.route("/password")
def password():
    user_num = session['user_num']
    
    mydb = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT id, website_name,login_id,password FROM password_manager WHERE user_num = %s", (user_num,))
    passwords = cursor.fetchall()

    cursor.close()
    mydb.close()

    return render_template("password.html",passwords=passwords)

@app.route("/addpassword",methods=["post"])
def click3():
    user_num = session['user_num']
    
    mydb = get_db_connection()
    cursor = mydb.cursor()
    sql="Insert into password_manager (user_num,website_name,login_id,password) values(%s,%s,%s,%s)"

    cursor.execute(sql,(user_num,request.form["website"],request.form["loginid"],request.form["password"]))
    mydb.commit()

    cursor.close()
    mydb.close()

    return redirect("/password")

@app.route("/delpasrow",methods=["post"])
def delpas():
    user_num = session['user_num']
    id=request.form["row_id"]
    mydb = get_db_connection()
    cursor = mydb.cursor()
    sql="delete from password_manager where user_num = %s AND id= %s"

    cursor.execute(sql,(user_num,id))
    mydb.commit()

    cursor.close()
    mydb.close()
    return redirect("/password")

@app.route("/time")
def time():
    return render_template("time.html")

@app.route("/deadline")
def deadline():
    user_num = session['user_num']
    
    mydb = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT id, name,status,date,time FROM deadline_tracker WHERE user_num = %s ORDER BY date", (user_num,))
    deadlines = cursor.fetchall()

    cursor.close()
    mydb.close()

    return render_template("deadlines.html",deadlines=deadlines)

@app.route("/adddeadline",methods=["post"])
def click4():
    user_num = session['user_num']
    
    mydb = get_db_connection()
    cursor = mydb.cursor()
    sql="Insert into deadline_tracker (user_num,name,status,date,time) values(%s,%s,%s,%s,%s)"

    cursor.execute(sql,(user_num,request.form["name"],request.form["status"],request.form["date"],request.form["time"]))
    mydb.commit()
    
    cursor.close()
    mydb.close()

    return redirect("/deadline")

@app.route("/deldlrow",methods=["post"])
def deldl():
    user_num = session['user_num']
    id=request.form["row_id"]
    mydb = get_db_connection()
    cursor = mydb.cursor()
    sql="delete from deadline_tracker where user_num = %s AND id= %s"

    cursor.execute(sql,(user_num,id))
    mydb.commit()

    cursor.close()
    mydb.close()
    return redirect("/deadline")

if __name__=="__main__":
    app.run()