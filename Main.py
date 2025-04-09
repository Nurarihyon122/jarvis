from Frontend.GUI import (
GraphicalUserInterface,
SetAssistantStatus,
ShowTextToScreen,
TempDirectoryPath,
SetMicrophoneStatus,
AnswerModifier,
QueryModifier,
GetMicrophoneStatus,
GetAssistantStatus )
from Backend. Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend. Automation import Automation
from Backend. SpeechToText import SpeechRecognition
from Backend. Chatbot import ChatBot
from Backend. TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

def StartImageDaemon():
    try:
        p = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=False)
        subprocesses.append(p)
        print("[🚀] Image generation process started.")
    except Exception as e:
        print(f"[❌] Error starting image generator: {e}")



env_vars=dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocesses =[]
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]


def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
            
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)


def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""  # <-- Initialize it here
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'),"r", encoding='utf-8')
    Data = File.read()
    if len(str(Data))>0:
        lines = Data.split('\n')
        result = '\n' .join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'),"w", encoding='utf-8')
        File.write(result)
        File.close()






def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()
    StartImageDaemon()
    intro_message = f"Hello {Username}, I’m {Assistantname}, your personal AI assistant. I’m online and ready to help you."
    ShowTextToScreen(f"{Assistantname} : {intro_message}")
    SetAssistantStatus("Introducing...")
    TextToSpeech(intro_message)
    SetAssistantStatus("Available ...")
InitialExecution()    

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking....")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"[🧠] Decision : {Decision}")
    print("")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    # ✅ Detect and clean image generation query
    for queries in Decision:
        if queries.startswith("generate "):
            ImageGenerationQuery = queries.replace("generate ", "").strip()
            ImageExecution = True
            print(f"[🖼️] Detected Image Generation Query: {ImageGenerationQuery}")

    # ✅ Handle automation tasks
    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            run(Automation(list(Decision)))
            TaskExecution = True

    # ✅ Write prompt to file to trigger ImageGeneration.py
    if ImageExecution:
        image_data_path = os.path.join("Frontend", "Files", "ImageGeneration.data")
        try:
            with open(image_data_path, "w", encoding="utf-8") as file:
                file.write(f"{ImageGenerationQuery},True")
            print(f"[📄] Wrote to {image_data_path}: {ImageGenerationQuery},True")
        except Exception as e:
            print(f"[❌] Failed to write image generation data: {e}")
        return  # Exit to avoid running chatbot too

    # ✅ Handle Realtime + General
    if G and R or R:
        SetAssistantStatus("Searching....")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                os._exit(1)


def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available ... " in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available ... ")

def SecondThread():
    
    GraphicalUserInterface()
    
    
if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()



