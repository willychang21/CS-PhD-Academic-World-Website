import mysql.connector
import logging

config = {
    'user': 'root',
    'password': 'Fcaa0134',
    'host': 'zhangjunjiedeMacBook-Air.local',
    'database': 'academicworld',
    'raise_on_warnings': True
}


class MySQLDatabase:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor(buffered=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.exception("Exception occurred")
        self.cursor.close()
        self.connection.close()

    def execute_query(self, query, values=None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            logging.exception(f"Failed to execute query: {error}")
            self.connection.rollback()
            return False

    def fetch_data(self, query, values=None):
        self.cursor.execute(query, values)
        return self.cursor.fetchall()


def fetch_all_keywords():
    with MySQLDatabase(config) as db:
        query = "SELECT name FROM keyword"
        result = db.fetch_data(query)
        keywords = [row[0] for row in result]

    return keywords


def fetch_all_favorite_keywords():
    with MySQLDatabase(config) as db:
        if not favorite_keywords_table_exists(db):
            create_favorite_keywords_table(db)

        query = "SELECT name FROM favorite_keywords"
        result = db.fetch_data(query)
        favorite_keywords = [row[0] for row in result]

    return favorite_keywords


def favorite_keywords_table_exists(db):
    query = "SHOW TABLES LIKE 'favorite_keywords'"
    return bool(db.fetch_data(query))


def create_favorite_keywords_table(db):
    query = ("CREATE TABLE `favorite_keywords` ("
             "`name` varchar(512) NOT NULL,"
             "PRIMARY KEY (`name`))")
    if db.execute_query(query):
        logging.info("Table created successfully")


def add_favorite_keyword(keyword):
    with MySQLDatabase(config) as db:
        query = "INSERT INTO favorite_keywords (name) VALUES (%s)"
        values = (keyword, )
        if db.execute_query(query, values):
            logging.info("Keyword added to favorite table successfully")


def delete_favorite_keyword(keyword):
    with MySQLDatabase(config) as db:
        if not favorite_keywords_table_exists(db):
            logging.error("Error: favorite_keywords table does not exist")
            return
        query = "DELETE FROM favorite_keywords WHERE name = %s"
        values = (keyword, )
        if db.execute_query(query, values):
            logging.info("Keyword deleted from favorite table successfully")

# Query 5. based on the favorite keywords, find the top 10 faculty related to the keywords. Will display both the number of keyword counts and total keyword scores by faculty.
# Total keyword score calcuated by the sum of individual keyword scores.
# note: the score is the sum of the count of the keywords;
#       the count is the number of keywords that the faculty has
#     the faculty with the highest score is the top faculty


def top10_faculty_related_favorite_keywords():
    with MySQLDatabase(config) as db:
        if not favorite_keywords_table_exists(db):
            logging.error("Error: favorite_keywords table does not exist")
            return
        query = ("SELECT faculty.name AS name, count(*) AS count, SUM(score) AS score "
                 "FROM faculty_keyword, faculty, favorite_keywords, keyword "
                 "WHERE faculty_id = faculty.id AND keyword_id = keyword.id AND keyword.name = favorite_keywords.name "
                 "GROUP BY name "
                 "ORDER BY score DESC "
                 "LIMIT 10")
        result = db.fetch_data(query)
        top10_faculty_related_favorite_keywords = [row[0] for row in result]

    return top10_faculty_related_favorite_keywords

# Query 6. based on the favorite keywords, find the top 10 schools related to the keywords. Will display both the number of keyword counts and total keyword scores by school. Counts calculated as the number of faculty with overlapping keywords.
# Total keyword score calcuated by the sum of individual keyword scores of all overlapping faculties.


def top10_unversity_related_favorite_keywords():
    with MySQLDatabase(config) as db:
        if not favorite_keywords_table_exists(db):
            logging.error("Error: favorite_keywords table does not exist")
            return
        query = ("SELECT university.name AS university, count(*) AS count, SUM(score) AS score "
                 "FROM university, faculty_keyword, faculty, favorite_keywords, keyword "
                 "WHERE university.id = faculty.university_id AND faculty_id = faculty.id AND keyword_id = keyword.id AND keyword.name = favorite_keywords.name "
                 "GROUP BY university "
                 "ORDER BY score DESC "
                 "LIMIT 10")
        result = db.fetch_data(query)
        top10_unversity_related_favorite_keywords = [row[0] for row in result]

    return top10_unversity_related_favorite_keywords

# R10: added index to the keyword table


def add_index_to_keyword_table():
    with MySQLDatabase(config) as db:
        query = "ALTER TABLE keyword ADD INDEX idx_keyword_name (name);"
        if db.execute_query(query):
            logging.info("Index added to keyword table successfully")

# R11: added foreign key constraint to the faculty_keyword table on keyword_id


def add_foreign_key_constraint_to_faculty_keyword_table():
    with MySQLDatabase(config) as db:
        query = "ALTER TABLE faculty_keyword ADD CONSTRAINT fk_keyword_id FOREIGN KEY (keyword_id) REFERENCES keyword (id);"
        if db.execute_query(query):
            logging.info(
                "Foreign key constraint added to faculty_keyword table successfully")

# R12: added trigger on faculty_keyword to make sure score is non-negative


def add_trigger_to_faculty_keyword_table():
    with MySQLDatabase(config) as db:
        query = ("CREATE TRIGGER faculty_keyword_score_check BEFORE INSERT ON faculty_keyword "
                 "FOR EACH ROW "
                 "BEGIN "
                 "IF NEW.score < 0 THEN "
                 "SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'score cannot be negative'; "
                 "END IF; "
                 "END")
        if db.execute_query(query):
            logging.info("Trigger added to faculty_keyword table successfully")
