# JEOPARDY_CSV.csv can be downloaded from https://www.kaggle.com/tunguz/200000-jeopardy-questions
# Completed in this release
# (todo) database DONE
# (todo) running totals DONE
# (todo) implement custom value query DONE
# (todo) implement today's date DONE
# (todo) check database integrity before starting DONE

# Planned for future releases
# (todo) multiple players
# (todo) save progress
# (todo) implement last week's winner / winstreaks
# (todo) implement speech recognition
# (todo) GUI
# (todo) buzzers
# (todo) Implement Jeopardy Game format (introductions, daily double, final jeopardy)
# (todo) with Proper number of questions / values, rounds etc.
# (todo) implement a way for images to be seen when there's a URL in the question
# (todo) custom games with date ranges
# (todo) winstreaks for returning players


import csv
import random
import pyttsx3
from datetime import datetime as dt
from sqlite3 import connect
import os
import hashlib

hasher = hashlib.md5()

class Player:
    def __init__(self, name='test_player', money=0, winstreak=0, hometown='Anywhere, USA', fact='Grows Peppers'):
        self.name = name
        self.money = money
        self.winstreak = winstreak
        self.hometown = hometown
        self.fact = fact
        self.date_joined = dt.now().date()

    def add_funds(self, value):
        self.money += value


class Talker:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.original_rate = self.engine.getProperty('rate')
        self.rate = self.original_rate
        self.engine.setProperty('rate', self.rate)
        self.voiceID = 0

    def say_fast(self, phrase):
        print(phrase)
        self.rate = 250
        self.engine.setProperty('rate', self.rate)
        # set volume to 40%
        self.engine.setProperty('volume', .40)
        self.engine.say(phrase)
        self.engine.runAndWait()

    def slow(self, phrase):
        print(phrase)
        self.rate = 130
        self.engine.setProperty('rate', self.rate)
        # set volume to 40%
        self.engine.setProperty('volume', .40)
        self.engine.say(phrase)
        self.engine.runAndWait()

class Game:
    def __init__(self):
        players = []
        self.dbpath = './game.db'
        self.db_md5 = '43ae111c4301b26a695f0c109118fa70'
        self.conn = connect(self.dbpath)
        self.cursor = self.conn.cursor()
        self.questions = {}
        self.query_questions = {}
        self.question_limit = 0
        self.todays_date = dt.now().date()
        self.last_weeks_winner = None

    def deletedb(self):
        self.conn.close()
        if os.path.exists('./game.db'):
            os.remove('./game.db')

    def opendb(self):
        self.conn = connect(self.dbpath)
        self.cursor = self.conn.cursor()

    def check_db_integrity(self):
        if os.path.exists('./game.db'):
            with open('./game.db', 'rb') as afile:
                buf = afile.read()
                hasher.update(buf)
            print(hasher.hexdigest())
            if hasher.hexdigest() == self.db_md5:
                print('Database Matches Hash')
            else:
                print('Database Doesn\'t match Hash')
                self.deletedb()
                self.setupdb()
        else:
            print('database does not exist')

    def setupdb(self):
        self.opendb()
        # JEOPARDY_CSV.csv can be downloaded from https://www.kaggle.com/tunguz/200000-jeopardy-questions
        with open('JEOPARDY_CSV.csv', newline='', encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile)
            self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS jeopardy_questions (i INT, date TEXT, category TEXT, value INT, question TEXT, answer TEXT)''')
            for i, row in enumerate(reader):
                # replaces all blank values with 200
                value = 200 if (row[' Value'] is None or row[' Value'].lower() == "none") else row[' Value'].strip(
                    '$').strip(',').strip('\'')
                self.questions[i] = {'date': str(row[' Air Date']), 'category': row[' Category'], 'value': value,
                                     'question': row[' Question'], 'answer': row[' Answer']}
                self.cursor.execute('INSERT INTO jeopardy_questions VALUES (?,?,?,?,?,?);',
                                    [i,
                                     str(row[' Air Date']),
                                     row[' Category'],
                                     value,
                                     row[' Question'],
                                     row[' Answer']])

            self.conn.commit()
            self.question_limit = len(self.questions)

    # (todo) retrieve_questions needs to build a custom SQL query for question filtering
    def question_query(self, date=None, value=None):
        d = '' if date is None else 'date = {}'.format(date)
        v = '' if value in [None, 'None'] else 'value = {}'.format(value)
        and_chain = ' AND ' if d and v else ''
        where = ' WHERE ' if d or v else ''
        end = ';'
        query = """SELECT * FROM jeopardy_questions{}{}{}{}{}""".format(where, d, and_chain, v, end)
        print(query)
        self.cursor.execute(query)
        desc = self.cursor.description
        column_names = [col[0] for col in desc]
        print(column_names)
        self.query_questions = [dict(zip(column_names, row)) for row in self.cursor.fetchall()]
        self.question_limit = len(self.query_questions)

    def standard_questions(self):
        two_hundred = []

def main():
    player_1 = Player('Colin B', 0)
    # read file in
    talker = Talker()
    talker.say_fast(str('Welcome to Jeopardy. I\'m your host, HAL. Today\'s date is {}'.format(dt.now().date())))
    game = Game()
    game.check_db_integrity()
    # here is where you input the values that go into the sql query.
    game.question_query(value=200) #, date='2004-12-31')
    playing = True
    question_number = 0
    while playing:
        question_number = random.randint(0, game.question_limit)
        # question_number = int(input('question number:'))
        date = str(game.query_questions[question_number]['date'])
        category = str(game.query_questions[question_number]['category'])
        value = int(game.query_questions[question_number]['value'])
        question = str(game.query_questions[question_number]['question'])
        answer = str(game.query_questions[question_number]['answer']).strip('"')
        talker.say_fast('\nQuestion Number: ' + str(question_number))
        talker.say_fast(str('From the date: {}, category {}.\n for ${}, please answer the question:\n').format(
            date,
            category,
            value))
        talker.say_fast('{}'.format(question))
        user_response = str(input('What/Who is: '))
        if user_response.lower() in answer.lower():
            talker.say_fast(('CORRECT!, the answer is {}, we add ${} to your total').format(answer, value))
            player_1.add_funds(value)
        else:
            talker.say_fast(('INCORRECT, the answer is {}, we deduct ${} from your total').format(answer, value))
            player_1.add_funds(-value)
        talker.say_fast('${} is the total for {}'.format(player_1.money, player_1.name))
    game.conn.close()

if __name__ == '__main__':
    main()
