import csv
import time
import random
import pyttsx3
import threading

questionPool = []

allQuestion = []
        
with open("question.csv", encoding='utf-8') as questionFile:
    csvContent = csv.reader(questionFile, delimiter=';')

    for row in csvContent:
        allQuestion.append(row)

random.seed(time.time())

for index in range(0, 3, 1):
    questionNo = random.randint(0, allQuestion.__len__())
    questionPool.append(allQuestion[questionNo-1])

engine = pyttsx3.init()

engine.setProperty('volume', 0.5)

voices = engine.getProperty('voices')

for voice in voices:
    if "French" in voice.name:
        engine.setProperty("voice", voice.id)
        break

for question in questionPool:
    engine.say(question[1] + question[2] + ", " + question[3] + ", " + question[4] + " ou " + question[5] + " ?")
    

def speak():
    engine.runAndWait()

t = threading.Thread(target=speak)
t.start()

print("yolo")
#engine.say("vouvou")

t.join()