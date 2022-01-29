#!/bin/python3

import json
import argparse
import sys
import random
import csv

class ingridient:
    unit = None
    amount = None
    name = None

    def __init__(self, name, amount, unit):
        self.name = name.lower()
        self.amount = amount
        self.unit = unit

    def getAmount(self):
       return self.amount

    def getUnit(self):
       return self.unit
    
    def getName(self):
        return self.name

    def getIngridient(self):
        return {self.name: {'amount':self.amount, 'unit':self.unit}}

    def getIngridientNAmount(self, N):
        return {self.name:{'amount':self.amount*N, 'unit':self.unit}}

class Course:

    name = None
    description = None
    ingridients = {}
    courseType = None

    def __init__(self, name, courseType):
        self.name = name.lower()
        self.courseType = courseType.lower()

    def setDescription(self, description):
        self.description = description

    def addIngridient(self, name, amount, unit):
        self.ingridients.update(ingridient(name, int(amount), unit).getIngridient())

    def storeCourse(self):
        course = {'description':self.description, 'ingridients':self.ingridients}

        try:
            fp = open("courses.json",'r')
        except FileNotFoundError:
            fp = open("courses.json", 'w+')

        try:
            courses = json.load(fp)
        except json.decoder.JSONDecodeError:
            courses = {}

        courses[self.courseType][self.name] = course

        fp = open('courses.json', 'w')
        json.dump(courses, fp)
        fp.close()


def randomize(number_of_dishes, course_repeat):
    try:
        fp = open('courses.json', 'r')
    except FileNotFoundError:
        print('No courses file')
        sys.exit(1)

    courses = json.load(fp)
    
    fp.close()

    menu = {}
    for course_type in courses:

        # Initializing menu course type
        menu[course_type] = {}

        for n in range(number_of_dishes):

            # Listing all dishes within one course type
            dishes = list(courses[course_type].keys())
            
            # Drawing one dish out of all dishes
            dish = random.choice(dishes)

            # Updating menu for the next week
            menu[course_type][dish] = courses[course_type][dish]

            # Increasing repeats of single dish within i.e. breakfasts by course_repeat times.
            for ingridient in menu[course_type][dish]['ingridients']:
                menu[course_type][dish]['ingridients'][ingridient]['amount'] = menu[course_type][dish]['ingridients'][ingridient]['amount']*course_repeat
                 
            # Deleting the dish to avoid randomizing the same one several times
            del courses[course_type][dish]

    fp = open('menu.json', 'w+')
    json.dump(menu, fp)
    fp.close()

def prepareListOfIngridients():
    fp = open('menu.json', 'r')
    menu = json.load(fp)
    ingridient_list = []

    header = ['Ingridient', 'Amount', 'Unit']

    # open the file in the write mode
    f = open('list_of_ingridients.csv', 'w+')
    
    # create the csv writer
    writer = csv.writer(f)
    
    # write a header to the csv file
    writer.writerow(header)
    
    data = []

    for course_type in menu:
        for dish in menu[course_type]:
            for ingridient in menu[course_type][dish]['ingridients']:

                # we found ingridient to add to list!
                # now we need to check if that type already exist!
                found = False
                for idx, item in enumerate(data):
                    if ingridient in item:
                        found = True
                        break
                    else:
                        found = False

                # If found then add additional amount
                if found == True:
                    item = [item[0], item[1] + menu[course_type][dish]['ingridients'][ingridient]['amount'], item[2]]
                    data[idx] = item
                else:
                    data.append([ingridient, menu[course_type][dish]['ingridients'][ingridient]['amount'], menu[course_type][dish]['ingridients'][ingridient]['unit']])
    writer.writerows(data)
    f.close()    



def main(args):
    
    parser = argparse.ArgumentParser(description='This is diet scheduler, type -h, --help to see options.')
    parser.add_argument('-rORa', help='Add course or randomize, type randomize or add', required=True)
    parser.add_argument('-ct', help='Course type: breakfast, secondBreakfast, lunch, dinner', required=False)
    parser.add_argument('-n', help='Course name, please type name of the course', required=False)
    parser.add_argument('-d', help='Description, please type steps to follow in order to prepare the meal', required=False)
    parser.add_argument('-ing', nargs='+', help='Please type ingridients: [name,amount,unit] [...]', required=False)
    parser.add_argument('-ds', '--days', help='In case of randomizing please type amount of days')
    parser.add_argument('-cr', '--course_repeat', help='In case of randomizing, please type how many times one course should repeat')

    args = parser.parse_args()

    if args.rORa == 'randomize':
        randomize(int(args.days), int(args.course_repeat))
        prepareListOfIngridients()
    elif args.rORa == 'add':
        course = Course(args.n, args.ct)
        course.setDescription(args.d)
        for ing in args.ing:
            ing = ing.split(',')
            course.addIngridient(ing[0], ing[1], ing[2])
        course.storeCourse()


if __name__ == '__main__':
    main(sys.argv)
