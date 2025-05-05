import sqlite3


def init_db():
    conn = sqlite3.connect('jobsearch.db')
    cursor = conn.cursor()

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS vacancies
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       title
                       TEXT,
                       link
                       TEXT
                       UNIQUE,
                       scraped_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       processed
                       BOOLEAN
                       DEFAULT
                       0
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS job_details
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       vacancy_id
                       INTEGER,
                       company_name
                       TEXT,
                       position
                       TEXT,
                       salary
                       TEXT,
                       location
                       TEXT,
                       description
                       TEXT,
                       requirements
                       TEXT,
                       posted_date
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       vacancy_id
                   ) REFERENCES vacancies
                   (
                       id
                   )
                       )
                   ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()