#!/usr/bin/env python3

from modules import pg8000
from random import randint
import configparser


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Create a connection to the database
    connection = None
    try:
        '''
        This is doing a couple of things in the back
        what it is doing is:

        connect(database='y12i2120_unikey',
            host='soit-db-pro-2.ucc.usyd.edu.au,
            password='password_from_config',
            user='y19i2120_unikey')
        '''
        
        connection = pg8000.connect(database="y22s2i2120_asur3329",
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as e:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(e)
    except pg8000.ProgrammingError as e:
        print("""Error, config file incorrect: check your password and username""")
        print(e)
    except Exception as e:
        print(e)

    # Return the connection to use
    return connection


################################################################################
# Login Function
#   - This function performs a "SELECT" from the database to check for the
#       student with the same unikey and password as given.
#   - Note: This is only an exercise, there's much better ways to do this
################################################################################

def check_login(sid, pwd):
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                 FROM unidb.student
                 WHERE studid=%s AND password=%s"""
        cur.execute(sql, (sid, pwd))
        r = cur.fetchone()              # Fetch the first row
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Error Invalid Login")
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


################################################################################
# List Staff
#   - This function performs a "SELECT" from the database to get the 
#       information of all academic staff.
################################################################################

def list_staff():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try getting all the information returned from the query
        # NOTE: column ordering is IMPORTANT
        cur.execute("""SELECT id, name, deptid, address
                        FROM UniDB.academicstaff""")
        val = cur.fetchall()
    except Exception as e:
        # If there were any errors, return a NULL row printing an error to the debug
        print(e)

    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return val


################################################################################
# Search Staff
#   - This function performs a "SELECT" from the database to get the 
#       information of academic staff in a particular department.
################################################################################

def search_staff(department):
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    
    # Check for bad input
    if len(department) != 3:
        return "Unsuccessful - Department must be a string of exactly length 3"
    
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT id, name, deptid, address
                 FROM UniDB.academicstaff 
                 WHERE deptid=%s"""
        params = (department,) # Comma required to make tuple
        cur.execute(sql, params)
        val = cur.fetchall()  
        
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return val
    except Exception as e:
        # If there were any errors, return a NULL row printing an error to the debug
        print(e)
        
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


################################################################################
# Report Staff
#   - This function performs a "SELECT" from the database to show
#       the number of academic staff existing in each department.
################################################################################

def report_staff():
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT deptid, count(id)
                 FROM UniDB.academicstaff 
                 GROUP BY deptid"""
        cur.execute(sql)
        val = cur.fetchall()            
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return val
    except Exception as e:
        # If there were any errors, return a NULL row printing an error to the debug
        print(e)
        
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


################################################################################
# ADD Staff
#   - This function performs a "INSERT" into the database to add
#       a new academic staff member.
################################################################################

def add_staff(name, password, password_check, department, address, salary):
    # Check for bad inputs
    if len(name) > 20:
        return "Unsuccessful - Full name must be less than or equal to 20 characters long"
    if password != password_check:
        return "Unsuccessful - Passwords dont match"
    if len(password) > 10:
        return "Unsuccessful - Password must be less than or equal to 10 characters long"
    if len(department) != 3:
        return "Unsuccessful - Department must be a string of exactly length 3"
    if len(address) > 50:
        return "Unsuccessful - Address must be less than or equal to 50 characters long"
    try:
        if len(salary) > 0:
            salary = int(salary)
    except:
        return "Unsuccessful - Salary must be an integer"
   
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try: # Try executing the SQL to get from & insert into database

        cur.execute("SELECT id FROM UniDB.academicstaff")
        existing_ids = cur.fetchall()
        staffid = str(randint(1000000,9999999)) + ' '
        while [staffid] in existing_ids: # Assign Unique ID
             staffid = str(randint(1000000,9999999)) + ' '
        
        sql = """INSERT INTO UniDB.academicstaff 
                 VALUES (%s, %s, %s, %s, %s, %s);"""
        params = (staffid, name, department, password, address, salary)
        cur.execute(sql, params)
        
        cur.close()                     # Close the cursor
        conn.commit()                   # Commit changes
        conn.close()                    # Close the connection to the db
        return "Successfully Added"
    except Exception as e:
        # If there were any errors, return a NULL row printing an error to the debug
        print(e)
    
    
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return "Unsuccessful - Error with SQL Query"


################################################################################
# List Posts
#   - This function performs a "SELECT" from the database to get the 
#       information of all discussion posts.
################################################################################

def list_posts():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT *
                 FROM UniDB.posts"""
        cur.execute(sql)
        val = cur.fetchall()  
        for post in val: # Formatting DateTime values for aesthetics
            post[3] = post[3].replace(microsecond=0)
        
        ordered_posts = reversed(val) # Most recently added post is displayed first    
                
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
                
        return ordered_posts
    except Exception as e:
        # If there were any errors, return a NULL row printing an error to the debug
        print(e)
        
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

################################################################################
# ADD Post
#   - This function performs a "INSERT" into the database to add
#       a new discussion post.
################################################################################

def add_post(author, content):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    try: # Try executing the SQL to get from & insert into database

        cur.execute("SELECT postid FROM UniDB.posts")
        existing_ids = cur.fetchall()
        postid = str(randint(1000000,9999999)) + ' '
        while [postid] in existing_ids: # Assign Unique ID
             postid = str(randint(1000000,9999999)) + ' '
        
        sql = """INSERT INTO UniDB.posts 
                 VALUES (%s, %s, %s, CURRENT_TIMESTAMP);"""
        params = (postid, author, content)
        cur.execute(sql, params)
        
        cur.close()                     # Close the cursor
        conn.commit()                   # Commit changes
        conn.close()                    # Close the connection to the db
        return "Successfully Added"
    except Exception as e:
        # If there were any errors, return a NULL row printing an error to the debug
        print(e)
    
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return "Unsuccessful - Error with SQL Query"

################################################################################
# DELETE Post
#   - This function performs a "DELETE" from the database to delete
#       a specific post by postid.
################################################################################

def delete_post(postid):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        return None
    # Sets up the rows as a dictionary
    cur = conn.cursor()
    val = None
    try: # Try executing the SQL to delete from database
        sql = """DELETE FROM UniDB.posts 
                 WHERE postid=%s;"""
        params = (postid,)
        cur.execute(sql, params)
        
        cur.close()                     # Close the cursor
        conn.commit()                   # Commit changes
        conn.close()                    # Close the connection to the db
        return "Successfully Deleted"
    except Exception as e:
        # If there were any errors, return a NULL row printing an error to the debug
        print(e)
    
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return "Unsuccessful - Error with SQL Query"


if (__name__ == '__main__'):
    print("{}\n{}\n{}".format("=" * 50, "Welcome to the 2-Tier Python Database", "=" * 50))