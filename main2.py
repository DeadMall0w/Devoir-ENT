import pronotepy
import datetime
from pronotepy.ent import ent_hdf
import json
import re

days_french = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"}
month_french = {"January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"}
month_french_liste = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

file = "devoirs.md"
username = ""
password = ""

def format_date_in_french(date):
    day_english = date.strftime("%A")
    month_english = date.strftime("%B")
    day = days_french[day_english]
    month = month_french[month_english]

    return f"{day} {date.day} {month} {date.year}"

def get_homeworks_pronote():
    print("Connexion a pronote pronote....")
    client = pronotepy.Client("https://0620052v.index-education.net/pronote/eleve.html",
                          username=username,
                          password=password,
                          ent=ent_hdf)
    homeworks = []
    if client.logged_in:
        print("Connecte a pronote !")
        print("Recuperation des devoirs")
        for i in range(0,15):
            date = datetime.date.today() + datetime.timedelta(days=i)

            homework = client.homework(date, date)

            if len(homework) >= 1:
                for home in homework:
                    current_homework = {
                        'date': format_date_in_french(date),
                        'subject': home.subject.name,
                        'title': home.description,
                        'done': False
                    }
                    homeworks.append(current_homework)
        print("Devoirs recupere !")
        return homeworks
    
def get_homeworks():
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    r = []
    for line in lines:
        if line.startswith("***"):
            break
        if line.startswith("- ["):
            r.append(line)
    return r

def conv_to_date(date_to_convert):
    date_splited = date_to_convert.split(' ')
    day = int(date_splited[1])
    month = month_french_liste.index(date_splited[2])+1
    year = int(date_splited[3])
    d = "" if day >= 10 else "0"
    m = "" if month >= 10 else "0"

    return f'{d}{day}-{m}{month}-{year}'

def conv_homework_to_string(homework):
    date = conv_to_date(homework['date'])
    s = f"- [ ] {homework['subject']} : {homework['title']} @" + "{" + date + "} \n"
    return s

def is_homework_already_present(homework, homeworks):
    s = conv_homework_to_string(homework)
    for h in homeworks:
        if h[4:].strip() == s[4:].strip():
            return True
    return False

def add_line(section, ligne):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    index_section = lines.index('## ' + section + '\n') + 1

    index_next_section = len(lines)
    for i in range(index_section, len(lines)):
        if lines[i].startswith('## '):
            index_next_section = i
            break

    lines.insert(index_next_section, ligne + '\n')

    with open(file, 'w', encoding='utf-8') as f:
        f.writelines(lines)


homeworks_pronote = get_homeworks_pronote()
homeworks = get_homeworks()

for h in homeworks_pronote:
    if is_homework_already_present(h, homeworks) == False:
        s = conv_homework_to_string(h)
        add_line('Homeworks', s)
        print(s, 'ajoute !')

