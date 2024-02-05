# Tyler Sabin
# CNE340 Winter Quarter 2024
# 2/4/2024
# follow instructions here and on Canvas to complete program
# https://rtc.instructure.com/courses/2439016/assignments/31830474?module_item_id=79735018
# code below modified by Tyler Sabin and Brian Huang
# https://github.com/profproix/cne340_jobhunter

# import required libraries and install packages
import mysql.connector
import time
import json
import requests
import datetime # why isn't this lighting up
import html2text


# Connect to database
# You may need to edit the connect function based on your local settings.#I made a password for my database because it is important to do so. Also make sure MySQL server is running or it will not connect
def connect_to_sql():
    conn = mysql.connector.connect(user='root', password='',
                                   host='127.0.0.1', database='cne340test')
    return conn


# Create the table structure
def create_tables(cursor):
    # Creates table
    # Must set Title to CHARSET utf8 unicode Source: http://mysql.rjweb.org/doc.php/charcoll.
    # Python is in latin-1 and error (Incorrect string value: '\xE2\x80\xAFAbi...') will occur if Description is not in unicode format due to the json data
    # cursor.execute("ALTER TABLE jobs CHANGE company company VARCHAR(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;") with help
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (id INT PRIMARY KEY auto_increment, Job_id varchar(50) , 
    company varchar (300), Created_at DATE, url varchar(30000), Title LONGBLOB, Description LONGBLOB ); ''')
    cursor.execute("ALTER TABLE jobs CHANGE company company VARCHAR(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")


# Query the database.
# You should not need to edit anything in this function
def query_sql(cursor, query):
    cursor.execute(query)
    return cursor


# Add a new job
def add_new_job(cursor, jobdetails):
    # extract all required columns
    description = html2text.html2text(jobdetails['description'])
    date = jobdetails['publication_date'][0:10]


    print(description)
    print(type(description))
    print()
    print(date)
    print(type(date))

    print()
    print()

    print(jobdetails)

    # isn't inserting all the data, see table
    query = cursor.execute("INSERT INTO jobs( Description, Created_at " ") "
                        "VALUES(%s,%s)", (description, date))
     # %s is what is needed for Mysqlconnector as SQLite3 uses ? the Mysqlconnector uses %s
    return query_sql(cursor, query)


# Check if new job
def check_if_job_exists(cursor, jobdetails):
    ##Add your code here
    job_id_variable = html2text.html2text(jobdetails['Job_id'])
    query = "SELECT * FROM jobs WHERE Description = \"%s\"" % job_id_variable
    # query = "UPDATE" why was the code written this way
    return query_sql(cursor, query)

# Deletes job
def delete_job(cursor, jobdetails):
    ##Add your code here
    job_id_variable = html2text.html2text(jobdetails['Job_id'])
    query = "DELETE FROM fantasy WHERE Description = \"%s\"" % job_id_variable
    # query = "UPDATE" why was the code written this way
    return query_sql(cursor, query)


# Grab new jobs from a website, Parses JSON code and inserts the data into a list of dictionaries do not need to edit
def fetch_new_jobs():
    query = requests.get("https://remotive.io/api/remote-jobs")
    datas = json.loads(query.text)

    return datas


# Main area of the code. Should not need to edit
def jobhunt(cursor):
    # Fetch jobs from website
    jobpage = fetch_new_jobs()  # Gets API website and holds the json data in it as a list
    # use below print statement to view list in json format
    # print(jobpage)
    add_or_delete_job(jobpage, cursor)


def add_or_delete_job(jobpage, cursor):
    # Add your code here to parse the job page
    for jobdetails in jobpage['jobs']:  # EXTRACTS EACH JOB FROM THE JOB LIST. It errored out until I specified jobs. This is because it needs to look at the jobs dictionary from the API. https://careerkarma.com/blog/python-typeerror-int-object-is-not-iterable/
        # Add in your code here to check if the job already exists in the DB
        check_if_job_exists(cursor, jobdetails)
        is_job_found = len(cursor.fetchall()) > 0  # https://stackoverflow.com/questions/2511679/python-number-of-rows-affected-by-cursor-executeselect
        if is_job_found:
            # I need to return cursor or something like the job name or current job list
            # Do I need to inform the user that the job already exists?
            # return query_sql(cursor, query)
            print("job already exists")
        else:
            # INSERT JOB
            # Add in your code here to notify the user of a new posting. This code will notify the new user
            # add_new_job(cursor, jobdetails)
            print("new job found")
            add_new_job(cursor, jobdetails)

        break

    # getting the difference between two date objects
    # cursor.execute("SELECT * FROM jobs")
    # row = cursor.fetchall() # [ (1,2,3,4) ]
    # print(row[0][3])
    # print(type(row[0][3]))
    # time1 = row[0][3]
    # time2 = datetime.date.today()
    # print(type(time2))
    # diff = time2 - time1
    # print(diff.days)

# Setup portion of the program. Take arguments and set up the script
# You should not need to edit anything here.
def main():
    # Important, rest are supporting functions
    # Connect to SQL and get cursor
    conn = connect_to_sql()
    cursor = conn.cursor()
    create_tables(cursor)

    while True:  # Infinite Loops. Only way to kill it is to crash or manually crash it. We did this as a background process/passive scraper
        jobhunt(cursor)
        # check job expired
        time.sleep(21600)  # Sleep for 6h, this is ran every hour because API or web interfaces have request limits. Your reqest will get blocked.


# Sleep does a rough cycle count, system is not entirely accurate
# If you want to test if script works change time.sleep() to 10 seconds and delete your table in MySQL
if __name__ == '__main__':
    main()