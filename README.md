# Nutrition
This is a tool that randomizes menu for a week based on json file that stores dishes

example:
./diet.py -rORa add -ct kolacja -n "GRZANKI Z JAJKIEM SADZONYM" -d "Ziemniaka obieramy i kroimy w plastry grubości około ½ cm i gotujemy przez około 10-12 minut w wodzie. Białą część pora kroimy w talarki, solimy i szklimy na niewielkiej ilości oliwy. Do pora dodajemy ulubione przyprawy i oczyszczone kurki. Smażymy przez 2 minuty, po czym wyłączamy ogień i układamy plasterki ziemniaka. W misce mieszamy jajka z pietruszką i pieprzem. Masę jajeczną wlewamy na patelnię i wstawiamy do piekarnika rozgrzanego do temperatury 200° C na około 10-15 minut." -ing "Chleb razowy",3,kromka "Jajka",3,sztuka "Awokado",0.25,sztuka "Serek bieluch",2,łyżka "Cebula",0.25,sztuka "Oliwa z oliwek",1,łyżka

./diet.py -rORa randomize -ds 1 -cr 3
