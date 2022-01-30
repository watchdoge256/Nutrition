# Nutrition
This is a tool that randomizes menu for a week based on json file that stores dishes

## Usage: diet.py [-h] -rORa RORA [-ct CT] [-n N] [-d D] [-ing ING [ING ...]] [-ds DAYS] [-cr COURSE_REPEAT]

This is diet scheduler, type -h, --help to see options.

optional arguments:
  -h, --help            show this help message and exit
  -rORa RORA            Add course or randomize, type randomize or add
  -ct CT                Course type: breakfast, secondBreakfast, lunch, dinner
  -n N                  Course name, please type name of the course
  -d D                  Description, please type steps to follow in order to prepare the meal
  -ing ING [ING ...]    Please type ingridients: [name,amount,unit] [...]
  -ds DAYS, --days DAYS
                        In case of randomizing please type amount of days
  -cr COURSE_REPEAT, --course_repeat COURSE_REPEAT
                        In case of randomizing, please type how many times one course should repeat


### Example:
Add grzanki z jajkiem sadzonym as dinner, with description and ingridients.

./diet.py -rORa add -ct kolacja -n "GRZANKI Z JAJKIEM SADZONYM" -d "Ziemniaka obieramy i kroimy w plastry grubości około ½ cm i gotujemy przez około 10-12 minut w wodzie. Białą część pora kroimy w talarki, solimy i szklimy na niewielkiej ilości oliwy. Do pora dodajemy ulubione przyprawy i oczyszczone kurki. Smażymy przez 2 minuty, po czym wyłączamy ogień i układamy plasterki ziemniaka. W misce mieszamy jajka z pietruszką i pieprzem. Masę jajeczną wlewamy na patelnię i wstawiamy do piekarnika rozgrzanego do temperatury 200° C na około 10-15 minut." -ing "Chleb razowy",3,kromka "Jajka",3,sztuka "Awokado",0.25,sztuka "Serek bieluch",2,łyżka "Cebula",0.25,sztuka "Oliwa z oliwek",1,łyżka

### Example:
To randomize menu for 3 days - one dish that is going to repeat for 3 days.

./diet.py -rORa randomize -ds 1 -cr 3
