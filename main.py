import pronotepy
import datetime
from pronotepy.ent import ent_hdf
import json
import re

filePath = "Travail/Listes devoirs.md"
username = ''
password = ''

days_french = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"}
month_french = {"January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"}
month_french_liste = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

def format_date_in_french(date):
    day_english = date.strftime("%A")
    month_english = date.strftime("%B")
    day = days_french[day_english]
    month = month_french[month_english]

    return f"{day} {date.day} {month} {date.year}"

def conv_to_date(date_to_convert):
    date_splited = date_to_convert.split(' ')
    day = int(date_splited[1])
    month = month_french_liste.index(date_splited[2])+1
    year = int(date_splited[3])
    return datetime.date(year, month, day)

def convertir_date(devoir):
    return conv_to_date(devoir['date'])

def get_homeworks_file():
    print(f'Ouverture de {filePath}...')
    with open(filePath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f'{filePath} ouvert !')
    homeworks = []
    current_date = ''
    for line in lines:

        if line.startswith('#'):#if it's a date
            current_date = line[2:].strip()
        elif line.startswith('-'):#if it's an homework
            done = line[3] == 'x'
            subject, title = re.split(':', line[6:], maxsplit=1)
            devoir = {
                'date': current_date,
                'subject': subject.strip(),
                'title': title.strip(),
                'done': done
            }
            homeworks.append(devoir)
    print(f'{filePath} analyse !')
    return homeworks
    
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

def merge_json(json1, json2):
    file = {(d['date'], d['subject'], d['title']): d for d in json1}
    print("Détection des nouveaux devoirs...")
    for devoir in json2:
        cle = (devoir['date'], devoir['subject'], devoir['title'])
        if cle not in file:
            file[cle] = devoir
    file = list(file.values())
    devoirs_tries = sorted(file, key=convertir_date)
    return devoirs_tries


def write_homeworks(homeworks):
    s = ""
    last_date = None
    print("Ecriture des nouveaux devoirs...")
    for homework in homeworks:
        date = homework['date']
        if date != last_date:
            last_date = date
            s += f"# {date}\n"
            done = 'x' if homework['done'] else ' '
        s += f"- [{done}] {homework['subject']} : {homework['title']}" + '\n'
    with open(filePath, 'w', encoding='utf-8') as f:
        f.write(s)
    print("Nouveau devoirs ecrit !")

def update_homeworks():
    file1 = get_homeworks_file()
    file2 = get_homeworks_pronote()
    file = merge_json(file1, file2)
    write_homeworks(file)

if __name__ == '__main__':
    update_homeworks()
    pass