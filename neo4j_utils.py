from neo4j import GraphDatabase
import pandas as pd


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(
                database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


# Need to open neo4j local server first before running this command
# change user and pwd to your own
conn = Neo4jConnection(uri="bolt://localhost:7687",
                       user="neo4j", pwd="cs411project")


# Query 2: Input keywords and given year,
#          run query to generate top 10 schools with most publications containing that keyword


def get_top_10_schools_by_keyword_and_year(keyword, start_year, end_year):
    query = f'''
        MATCH (i1:INSTITUTE) <- [:AFFILIATION_WITH] - (f1:FACULTY) -[:PUBLISH] -> (p:PUBLICATION) - [l:LABEL_BY] -> (k:KEYWORD)
        WHERE p.year >= {start_year} AND p.year <= {end_year} AND k.name = "{keyword}"
        RETURN i1.name, COUNT(Distinct p) AS count
        ORDER BY count DESC
        LIMIT 10
    '''
    result = conn.query(query, db='academicworld')
    df = pd.DataFrame([dict(_) for _ in result]).rename(
        columns={'i1.name': 'university', 'count': 'count'})
    return df


# Query 3: Input name of schools, generate breakdowns of keywords scores in bar charts.
#          Keyword scores is calculated as the sum of score of all faculties with given keyword.


def get_keyword_scores_by_school(school):
    query = f'''
        MATCH (i1:INSTITUTE) <- [:AFFILIATION_WITH] - (f1:FACULTY) -[i:INTERESTED_IN] -> (k:KEYWORD)
        WHERE i1.name = "{school}"
        RETURN k.name, SUM(i.score) AS total_score
        ORDER BY total_score DESC
        LIMIT 10
    '''
    result = conn.query(query, db='academicworld')
    df = pd.DataFrame([dict(_) for _ in result]).rename(
        columns={'k.name': 'keyword', 'total_score': 'total score'})
    return df


# Query 4: Input name of faculty and given year, run query to generate keywords scores.
#          Keyword score here is calculed as publication score timed by citation, similar to MP5.


def get_keyword_scores_by_faculty_and_year(faculty, start_year, end_year):
    query = f'''
        MATCH (k1:KEYWORD) <- [i:INTERESTED_IN]- (f1:FACULTY) -[:PUBLISH] -> (p:PUBLICATION) - [l:LABEL_BY] -> (k2:KEYWORD)
        WHERE f1.name = "{faculty}" AND p.year >= {start_year} AND p.year <= {end_year} AND k2.name = k1.name
        RETURN k2.name, SUM(l.score * p.numCitations) AS total_score
        ORDER BY total_score DESC
        LIMIT 10
    '''
    result = conn.query(query, db='academicworld')
    df = pd.DataFrame([dict(_) for _ in result]).rename(
        columns={'k2.name': 'Keyword', 'total_score': 'Total Score'})
    return df


# get all the keywords


def get_all_keywords():
    query = '''
        MATCH (n:KEYWORD)
        RETURN n.name as name
        ORDER BY name
    '''
    result = conn.query(query, db='academicworld')
    keywords = [record['name'] for record in result]
    return keywords

# get all the universities' names


def get_all_universities():
    query = '''
        MATCH (n:INSTITUTE)
        RETURN n.name as name
        ORDER BY name
    '''
    result = conn.query(query, db='academicworld')
    universities = [record['name'] for record in result]
    return universities

# get all the faculties' names


def get_faculties():
    query = '''
        MATCH (f:FACULTY)
        RETURN f.name as name
        ORDER BY name
    '''
    result = conn.query(query, db='academicworld')
    faculties = [record['name'] for record in result]
    return faculties
