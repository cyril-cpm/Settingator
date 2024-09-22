import csv
import time
import random
import pyttsx3
import threading
import multiprocessing


queue = multiprocessing.Queue()

def onStart(name, truc):
    print(name)

def speakingProcessFunction(queue):
    engine = pyttsx3.init()
    engine.setProperty('volume', 0.5)

    engine.connect('started-utterance', lambda name : onStart(name, 5))

    voices = engine.getProperty('voices')

    for voice in voices:
        if "French" in voice.name:
            engine.setProperty("voice", voice.id)
            break

    while True:
        sentence = queue.get()
        engine.say(sentence)
        engine.runAndWait()

if __name__ == "__main__":
    speakingProcess = multiprocessing.Process(target=speakingProcessFunction, args=(queue,))
    speakingProcess.start()

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

    for question in questionPool:
        queue.put(question[1] + question[2] + ", " + question[3] + ", " + question[4] + " ou " + question[5] + " ?")
        print("yolo")
        


    speakingProcess.join()

