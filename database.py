import sqlite3


def create_database():
    # Create a connection to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('gymers.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Create the "gymers" table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gymers (
            account_no INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            dob DATE,
            gender TEXT,
            height REAL,
            weight REAL,
            exercise_name TEXT,
            high_score INTEGER
        )
        ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def insert_data():
    # Create a connection to the database
    conn = sqlite3.connect('gymers.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Insert sample data into the "gymers" table
    cursor.execute("INSERT INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (1, 'John', 'Doe', '1990-05-10', 'Male', 180, 75, 'Push-ups', 100)")
    cursor.execute("INSERT INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (2, 'Jane', 'Smith', '1985-12-15', 'Female', 165, 62, 'Squats', 150)")
    cursor.execute("INSERT INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (3, 'Michael', 'Johnson', '1992-07-20', 'Male', 175, 80, 'Deadlifts', 200)")

    cursor.execute("INSERT INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (4, 'Johna', 'Doea', '1990-05-10', 'Male', 180, 75, 'Push-ups', 120)")
    cursor.execute("INSERT INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (5, 'Janea', 'Smitha', '1985-12-15', 'Female', 165, 62, 'Squats', 130)")
    cursor.execute("INSERT INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (6, 'Michaela', 'Johnsona', '1992-07-20', 'Male', 175, 80, 'Deadlifts', 190)")

    cursor.execute("INSERT INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (7, 'Johnb', 'Doeb', '1990-05-10', 'Male', 180, 75, 'Push-ups', 130)")
    cursor.execute("INSERT INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (8, 'Jane', 'Smith', '1985-12-15', 'Female', 165, 62, 'Squats', 170)")
    cursor.execute("INSERT INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (9, 'Michael', 'Johnson', '1992-07-20', 'Male', 175, 80, 'Deadlifts', 210)")

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()


def insert_new(account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score):
    # Create a connection to the database
    conn = sqlite3.connect('gymers.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Check if the person already exists in the database
    cursor.execute(
        "SELECT high_score FROM gymers WHERE account_no = ?", (account_no,))
    previous_score = cursor.fetchone()

    # Insert the values if the person doesn't exist or if the previous score is lower
    if previous_score is None or high_score > previous_score[0]:
        cursor.execute("INSERT OR REPLACE INTO gymers (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (account_no, first_name, last_name, dob, gender, height, weight, exercise_name, high_score))
        print("Data inserted successfully.")
    else:
        print("Previous score is higher. Skipping insertion.")

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()


def get_high_scores():
    # Create a connection to the database
    conn = sqlite3.connect('gymers.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Retrieve the top 2 scores for each exercise category
    cursor.execute('''
        SELECT exercise_name, first_name, last_name, high_score
        FROM gymers
        WHERE account_no IN (
            SELECT account_no
            FROM gymers AS g2
            WHERE g2.exercise_name = gymers.exercise_name
            ORDER BY high_score DESC
            LIMIT 1
        )
        ORDER BY exercise_name, high_score DESC
    ''')

    # Fetch all the rows returned by the query
    data = cursor.fetchall()

    # Close the connection
    conn.close()
    return list(data)


def get_top_scores():
    # Create a connection to the database
    conn = sqlite3.connect('gymers.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Retrieve the top 5 scores for each exercise category
    cursor.execute('''
        SELECT exercise_name, first_name, last_name, high_score
        FROM (
            SELECT exercise_name, first_name, last_name, high_score,
            ROW_NUMBER() OVER(PARTITION BY exercise_name ORDER BY high_score DESC) AS rank
            FROM gymers
        ) AS ranked_scores
        WHERE rank <= 5
        ORDER BY exercise_name, high_score DESC
    ''')

    # Fetch all the rows returned by the query
    data = cursor.fetchall()
    # Close the connection
    conn.close()

    return list(data)


if __name__ == '__main__':
    # create_database()
    # insert_data()
    # insert_new(10, 'John', 'Doe', '1990-05-10','Male', 180, 75, 'Push-ups', 120)
    # insert_new(11, 'Jane', 'Smith', '1985-12-15','Female', 165, 62, 'Squats', 180)
    # insert_new(12, 'Michael', 'Johnson', '1992-07-20','Male', 175, 80, 'Deadlifts', 190)

    #data = get_high_scores()
    # print(data)
    #data = get_top_scores()
    # print(data)
    pass
