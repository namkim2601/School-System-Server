# Importing the Flask Framework

from modules import *
from flask import *
import database
import configparser


page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
unikey = config['DATABASE']['user']
portchoice = config['FLASK']['port']

#####################################################
##  INDEX
#####################################################

# What happens when we go to our website
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['unikey'] = unikey
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

################################################################################
# Login Page
################################################################################

# This is for the login
# Look at the methods [post, get] that corresponds with form actions etc.
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'unikey' : unikey}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['sid'], request.form['password'])

        # If our database connection gave back an error
        if(val == None):
            flash("""Error with the database connection. Please check your terminal
            and make sure you updated your INI files.""")
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))
        # If it was successful, then we can log them in :)
        session['name'] = val[1]
        session['sid'] = request.form['sid']
        session['logged_in'] = True
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)


################################################################################
# Logout Endpoint
################################################################################

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))



################################################################################
# adminstaff Routes
################################################################################
@app.route('/list-staff')
def list_staff():
    if( 'logged_in' not in session or not session['logged_in']):
        flash("You must login before you can access this page")
        return redirect(url_for('login'))
    staff = database.list_staff()
    
    if (staff is None):
        # Set it to an empty list and show error message
        staff = []
        flash('Error, there are no staff')
    page['title'] = 'Staff List'
    return render_template('staff-list.html', page=page, session=session, staff=staff)

@app.route('/search-staff', methods=['POST', 'GET'])
def search_staff():
    if( 'logged_in' not in session or not session['logged_in']):
        flash("You must login before you can access this page")
        return redirect(url_for('login'))
    
    page['title'] = 'Staff Search'
    if(request.method == 'POST'):
        staff = database.search_staff(request.form['department'])
    
        if (staff is None or len(staff) == 0):
            # Set it to an empty list and show error message
            staff = []
            flash('Department has no staff or does not exist')
        elif ("Unsuccessful" in staff):
            flash(staff)
            staff = []
            
        return render_template('staff-search.html', page=page, session=session, staff=staff)
    
    else:
        return render_template('staff-search.html', page=page, session=session, staff=None)

@app.route('/report-staff')
def report_staff():
    if( 'logged_in' not in session or not session['logged_in']):
        flash("You must login before you can access this page")
        return redirect(url_for('login'))
    
    staff = database.report_staff()
    
    if (staff is None) or (len(staff) == 0):
        # Set it to an empty list and show error message
        staff = []
        flash('Error, there are no departments')
    page['title'] = 'Staff Report'
    return render_template('staff-report.html', page=page, session=session, staff=staff)

@app.route('/add-staff', methods=['POST', 'GET'])
def add_staff():
    if( 'logged_in' not in session or not session['logged_in']):
        flash("You must login before you can access this page")
        return redirect(url_for('login'))
    
    page['title'] = 'Staff Add'
    if(request.method == 'POST'): 
        result = database.add_staff(request.form['name'], request.form['password'], request.form['password-check'], request.form['department'], request.form['address'], request.form['salary'])
        
        flash(result)
        return render_template('staff-add.html', page=page, session=session)
    else:
        return render_template('staff-add.html', page=page, session=session)

@app.route('/index-staff')
def index_staff():
    if( 'logged_in' not in session or not session['logged_in']):
        flash("You must login before you can access this page")
        return redirect(url_for('login'))
    
    return render_template('staff-index.html', page=page, session=session)
    

@app.route('/discussion', methods=['POST', 'GET'])
def discussion():
    if( 'logged_in' not in session or not session['logged_in']):
        flash("You must login before you can access this page")
        return redirect(url_for('login'))
    
    page['title'] = 'Discussion'
    if(request.method == 'POST'): 
        result = database.add_post(request.form['username'], request.form['content'])
        flash(result)
    
    posts = database.list_posts()
    if (posts is None):
        # Set it to an empty list and show error message
        posts = []
    return render_template('discussion.html', page=page, session=session, posts=posts)

@app.route('/delete-post', methods=['POST'])
def delete_post():    
    result = database.delete_post(request.form['postid'])
    flash(result)
    return redirect(url_for('discussion'))
        
























