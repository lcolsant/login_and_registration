from flask import Flask, request, redirect, render_template, flash, session
from mysqlconnection import MySQLConnector
import md5
import os, binascii 
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
mysql = MySQLConnector(app,'login_and_registration')
app.secret_key = 'secretKey'

@app.route('/')
def index():
    if 'id' in session.keys():
        return redirect('/success')
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def create():

    if '_flashes' in session:
        session.pop('_flashes', None)
    
    errors = 0

    if len(request.form['fname']) < 3:
        flash('First name must be at least 2 characters!')
        errors+=1
    elif not request.form['fname'].isalpha():
        flash("First name should be alpha only")
        errors+=1
    else:
        fname = request.form['fname']
    if len(request.form['lname']) < 3:
        flash('Last name must be at least 2 characters!')
        errors+=1
    elif not request.form['lname'].isalpha():
        flash("First name should be alpha only")
        errors+=1
    else:
        lname = request.form['lname']
    if len(request.form['email']) < 1:
        flash('Email cannot be empty!')
        errors+=1
    elif not EMAIL_REGEX.match(request.form['email']):
        flash('Invalid Email Address!')
        errors+=1
    else:
        email = request.form['email']
    if len(request.form['pass']) < 8:
        flash('Password should be at least 8 characters!')
        errors+=1
    else:
        password = request.form['pass']
        salt = binascii.b2a_hex(os.urandom(15))
        hashed_pw = md5.new(password + salt).hexdigest()        
    if len(request.form['pass_confirm']) < 8:
        flash('Password confirm should be at least 8 characters!')
        errors+=1
    else:
        pass_confirm = request.form['pass_confirm']
    
    if request.form['pass'] != request.form['pass_confirm']:
        flash('Password does not match password confirmation')
        errors+=1

    if errors > 0:
        print "Number of errors:",errors
        return redirect('/')
    else:
        # return render_template('showData.html', email = email,fname = fname, lname = lname)
        session['fname'] = fname
        session['lname'] = lname
        session['email'] = email
        session['pass'] = hashed_pw
        # session['pass_confirm'] = pass_confirm
        #  query = "INSERT INTO emails (email, created_at, updated_at) VALUES (:email, NOW(), NOW() )"
        query = 'INSERT INTO `login_and_registration`.`users` (`first_name`, `last_name`, `email`, `password`, `salt`, `created_at`, `updated_at`) VALUES (:fname, :lname, :email, :pass, :salt, NOW(), NOW() );'
        # We'll then create a dictionary of data from the POST data received.
        data = {
                #'email': request.form['email'],
                'fname': session['fname'],
                'lname': session['lname'],
                'email': session['email'],
                'pass': session['pass'],
                'salt': salt,

            }
        # Run query, with dictionary values injected into the query.

        mysql.query_db(query, data)
        flash('Registered successfully. Please login')

        #now run query to retrieve all emails

        ##############################
        # query = "SELECT * FROM users"
        # users = mysql.query_db(query)
        # print users
        # return render_template('success.html', all_users=users)
        ###############################

    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    
    # if '_flashes' in session:
    #     session.pop('_flashes', None)

    email = request.form['email']
    password = request.form['pass']
    #  query = 'INSERT INTO `login_and_registration`.`users` (`first_name`, `last_name`, `email`, `password`, `password_confirm`, `created_at`, `updated_at`) VALUES (:fname, :lname, :email, :pass, :pass_confirm, NOW(), NOW() );'
    query = 'SELECT * FROM users WHERE email=:email'
        # We'll then create a dictionary of data from the POST data received.
    data = {
            #'email': request.form['email'],
            'email': email,

        }
    # Run query, with dictionary values injected into the query.
    user = mysql.query_db(query, data)
    if len(user) == 0:
        flash("User not recognized")
        return redirect('/')
    else:
        encrypted_password = md5.new(password + user[0]['salt']).hexdigest()
        if user[0]['password'] == encrypted_password:
            flash("User logged in")
            session['id'] = user[0]['id']  #set current user id in session
            return redirect('/success')
        else:
            flash("Invalid password.")
            return redirect('/')

@app.route('/success')
def success():
    query = "SELECT * FROM users WHERE id=:one"
    data = {
        'one':session['id']
    }
    logged_user = mysql.query_db(query,data)[0]
    # return logged_user['first_name']

    
    return render_template('success.html',logged_user_data=logged_user)


@app.route('/message')
def message_():
    message = request.form['message']
    print message

    #add insert post query here
    return redirect('/')

@app.route('/logout')
def logout_():
    session.clear()
    return redirect('/')


app.run(debug=True)