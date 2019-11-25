# dataset can be downloaded from is from https://www.kaggle.com/tunguz/200000-jeopardy-questions
# (todo) database
# (todo) voice speech
# (todo) running totals
# (todo) multiple players
# (todo) save progress
# (todo) GUI
# (todo) save database
# query database
import csv
import random

def main():
    # read file in
    questions = {}

    with open('JEOPARDY_CSV.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        # 0 = airdate
        # 1 = category
        # 2 = value
        # 3 = question
        for i, row in enumerate(reader):
            questions[i] = {'date': str(row[' Air Date']),
                            'category': row[' Category'],
                            'value': row[' Value'],
                            'question': row[' Question'],
                            'answer': row[' Answer']
                            }
        question_limit = len(questions)

    playing = True
    question_number = 0
    while playing:
        question_number = random.randint(0, question_limit)
        # question_number = int(input('question number:'))
        date = str(questions[question_number]['date'])
        category = str(questions[question_number]['category'])
        value = str(questions[question_number]['value'])
        question = str(questions[question_number]['question'])
        answer = str(questions[question_number]['answer']).strip('"')
        print('\nQuestion Number: ' + str(question_number))
        print(str('From the date: {}, category {}.\n for {}, please answer the question:\n{}').format(
            date,
            category,
            value,
            question))
        user_response = str(input('What/Who is: '))
        if user_response.lower() in answer.lower():
            print(('CORRECT!, please add {} to your total').format(value))
        else:
            print(('INCORRECT, the answer is {}, please deduct {} from your total').format(answer, value))

if __name__ == '__main__':
    main()
