## Title

Finding most match universities and faculties for CS PhD application

## Purpose

We built a dashboard for CS PhD applications to search for most suitable universities and faculties based on their research interests **(R1)**. Our dashboard also empowers PhD applicants to explore trending research interests over the years, as well as relative strength of the research topic from given school and faculty over years **(R2)**.

## Demo

<https://mediaspace.illinois.edu/media/t/1_lrcgy4qf>

## Installation

We only used existing datasets from MPs. To run the code, simply enter in terminal:
`python3 app.py`

## Usage

- Widget 1: user will select a time range in years, and the top 10 most popular research keywords along with total publication counts will be displayed.
- Widget 2: user will enter a given keyword and select a time frame in years, and the top 10 universities with most publications counts will be displayed.
- Widget 3: user will enter a given university name, and a pie chart with keyword score percentages of top 10 keywords will be displayed. For a given keyword, keyword score is calculated as sum of individual faculty's score of that keyword.
- Widget 4: user will enter a faculty name and select a time range in years, and the top 10 keywords with highest keyword-relevant citation will be displayed. For this widget, we define the keyword-relevant citation of a faculty member F for a keyword K as: The sum of S\*C for each publication P of F’s publications such that P contains K with score S and P’s citation is C. Note S refers to the score of K in the publication P. This is consistent with MP5.
- Widget 5: user will first enter/modify a number of favorite keywords. The top 10 faculties with highest relavance to the favorite keywords will be displayed. For a given faculty, relavance score is caulcalated as the sum of his/her keyword scores for those keywords overlaping with given favorites.
- Widget 6: user will first enter/modify a number of favorite keywords. The top 10 universites with highest relavance to the favorite keywords will be displayed. For a given university, relavance score is calcuated as the sum of all faculties' individual keyword scores for those keywords overlaping with given favorites.
- In summary, we have 6 widgets that take inputs from users **(R6, R8)**. We designed widgets in a rectangular spaces **(R9)**.

## Design

Similar to sample project demos in the Project Instruction, we have one main app.py with frontend implemention using Dash, along with three files of mongodb_utils.py, mysql_utils.py, neo4j_utils.py to perform query and interact with each database's API.

## Implementation

- Widget 1 is implemented with MongoDB **(R4)**.
- Widget 2 to 4 are implemented with Neo4j **(R5)**.
- Widget 5 to 6 are implemented with MySQL **(R3)** and perform updates of a backend databases **(R7)**. Users may add or delete favorite database, which will cause update in the _favorite_keywords_ table in MySQL database.
  from neo4j import GraphDatabase
- We used dash and dash_bootstrap_components for frontend. We used respective APIs of MySQL (mysql.connector), MongoDB (pymongo) and Neo4j(neo4j) to access database.

## Database Techniques

- All techniques are implemented in Mysql database.
- We added index to the name variable in keyword table **(R10)**.
- We added foreign key constraint to the faculty_keyword table on keyword_id **(R11)**.
- We added trigger on faculty_keyword to make sure score is non-negative **(R12)**.

## Extra-Credit Capabilities

N/A

## Contributions

- Hanyin wrote codes for backend database queries, did the video demo and contributed to README. Total time spent 20 hours.
- Chun wrote codes for frontend/dash, intergrated frondend and backend codes and contributed to README. Total time spent 20 hours.
