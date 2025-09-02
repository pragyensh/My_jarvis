from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import asyncio

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")

DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# Performance monitoring
DEBUG_MODE = True
performance_data = {
    'speech_recognition': [],
    'decision_making': [],
    'response_generation': [],
    'total_execution': []
}

def debug_print(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

def log_performance(stage, time_taken):
    performance_data[stage].append(time_taken)
    if len(performance_data[stage]) > 10:
        performance_data[stage].pop(0)
    
    avg_time = sum(performance_data[stage]) / len(performance_data[stage]) if performance_data[stage] else 0
    debug_print(f"{stage} avg: {avg_time:.2f}s")

# Async timeout decorator
def async_timeout(seconds=10):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                debug_print(f"⚠️ {func.__name__} timed out after {seconds} seconds")
                return None
        return wrapper
    return decorator

@async_timeout(8)
async def async_speech_recognition():
    return SpeechRecognition()

def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                    file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                    file.write(DefaultMessage)
    except Exception as e:
        debug_print(f"Error in ShowDefaultChatIfNoChats: {e}")
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except Exception as e:
        debug_print(f"Error reading ChatLog.json: {e}")
        return []

def ChatLogIntegration():
    try:
        json_data = ReadChatLogJson()
        formatted_chatlog = ""
        for entry in json_data:
            if entry["role"] == "user":
                formatted_chatlog += f"User: {entry['content']} \n"
            elif entry["role"] == "assistant":
                formatted_chatlog += f"Assistant: {entry['content']} \n"
        formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
        formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(AnswerModifier(formatted_chatlog))
    except Exception as e:
        debug_print(f"Error in ChatLogIntegration: {e}")

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as File:
            Data = File.read()
        if len(str(Data)) > 0:
            lines = Data.split('\n')
            result = '\n'.join(lines)
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as File:
                File.write(result)
    except Exception as e:
        debug_print(f"Error in ShowChatsOnGUI: {e}")

def InitialExecution():
    debug_print("Starting Initial Execution...")
    SetMicrophoneStatus("True")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()
    debug_print("Initial Execution completed.")

InitialExecution()

def handle_image_generation(decision):
    """Handle image generation in background thread"""
    try:
        for query in decision:
            if "generate" in query:
                image_query = query.replace("generate image ", "")
                debug_print(f"Starting image generation: {image_query}")
                
                # Write to trigger file
                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write(f"{image_query},True")
                
                # Start image generation in background
                subprocess.Popen(['python', r'Backend\ImageGeneration.py'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                return True
    except Exception as e:
        debug_print(f"Image generation setup error: {e}")
    return False

def handle_exit():
    """Handle exit command"""
    debug_print("Exit command received")
    QueryFinal = "Okay, Bye!"
    Answer = ChatBot(QueryModifier(QueryFinal))
    ShowTextToScreen(f"{Assistantname} : {Answer}")
    SetAssistantStatus("Answering ...")
    TextToSpeech(Answer)
    SetAssistantStatus("Shutting down...")
    os._exit(1)

def process_commands(decision, original_query):
    """Process all commands with priority handling"""
    start_time = time.time()
    
    # Check for exit first
    if any("exit" in q for q in decision):
        handle_exit()
        return True
    
    # Handle image generation in background (non-blocking)
    image_generated = handle_image_generation(decision)
    
    G = any([i for i in decision if i.startswith("general")])
    R = any([i for i in decision if i.startswith("realtime")])
    
    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in decision if i.startswith("general") or i.startswith("realtime")]
    )
    
    # Handle automation tasks
    task_executed = False
    for queries in decision:
        if not task_executed:
            if any(queries.startswith(func) for func in Functions):
                debug_print(f"Running automation for: {queries}")
                run(Automation(list(decision)))
                task_executed = True
    
    # Process queries
    if G and R or R:
        debug_print("Processing realtime search...")
        SetAssistantStatus("Searching ...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        debug_print(f"Realtime search answer: {Answer}")
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering ...")
        TextToSpeech(Answer)
        log_performance('response_generation', time.time() - start_time)
        return True
    else:
        for Queries in decision:
            if "general" in Queries:
                debug_print(f"Processing general query: {Queries}")
                SetAssistantStatus("Thinking ...")
                QueryFinal = Queries.replace("general ", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                debug_print(f"ChatBot answer: {Answer}")
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                log_performance('response_generation', time.time() - start_time)
                return True
            elif "realtime" in Queries:
                debug_print(f"Processing realtime query: {Queries}")
                SetAssistantStatus("Searching ...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                debug_print(f"Realtime search answer: {Answer}")
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                log_performance('response_generation', time.time() - start_time)
                return True
    
    return False

def MainExecution():
    total_start_time = time.time()
    try:
        debug_print("Starting MainExecution...")
        SetAssistantStatus("Listening...")
        
        # Speech recognition with timeout
        speech_start = time.time()
        try:
            Query = asyncio.run(async_speech_recognition())
        except Exception as e:
            debug_print(f"Async speech recognition failed: {e}")
            Query = SpeechRecognition()  # Fallback
            
        if not Query or len(Query.strip()) < 2:
            SetAssistantStatus("Ready...")
            return False
            
        speech_time = time.time() - speech_start
        log_performance('speech_recognition', speech_time)
        debug_print(f"Speech recognition took: {speech_time:.2f}s")
        
        ShowTextToScreen(f"{Username} : {Query}")
        SetAssistantStatus("Thinking...")
        
        # Decision making
        decision_start = time.time()
        Decision = FirstLayerDMM(Query)
        decision_time = time.time() - decision_start
        log_performance('decision_making', decision_time)
        debug_print(f"Decision making took: {decision_time:.2f}s")
        debug_print(f"Decision: {Decision}")
        
        if not Decision:
            debug_print("No decision made, using general query...")
            Decision = [f"general {Query}"]
        
        # Process commands
        result = process_commands(Decision, Query)
        
        total_time = time.time() - total_start_time
        log_performance('total_execution', total_time)
        debug_print(f"Total execution took: {total_time:.2f}s")
        
        return result
        
    except Exception as e:
        debug_print(f"Error in MainExecution: {e}")
        SetAssistantStatus("Error occurred...")
        return False

def FirstThread():
    debug_print("First thread started...")
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()
            debug_print(f"Current Mic Status: {CurrentStatus}")
            
            if CurrentStatus == "False":  # Mic is active/listening
                start_time = time.time()
                result = MainExecution()
                execution_time = time.time() - start_time
                
                debug_print(f"Full execution took: {execution_time:.2f} seconds")
                
                if result:
                    SetAssistantStatus("Ready...")
                
                # Adaptive cooldown based on execution time
                cooldown = 0.3 if execution_time < 1.5 else 0.8
                sleep(cooldown)
            else:
                # Mic is off, check status less frequently
                AIStatus = GetAssistantStatus()
                if "Ready..." not in AIStatus and "Available..." not in AIStatus:
                    SetAssistantStatus("Ready...")
                sleep(1.0)
                
        except Exception as e:
            debug_print(f"FirstThread error: {e}")
            sleep(2.0)

def SecondThread():
    debug_print("Starting GUI...")
    GraphicalUserInterface()

if __name__ == "__main__":
    debug_print("Starting application...")
    
    # Ensure required directories exist
    os.makedirs("temp", exist_ok=True)
    os.makedirs("Data", exist_ok=True)
    os.makedirs("Frontend/Files", exist_ok=True)
    
    # Start the first thread for processing
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    
    # Start the GUI (this blocks until GUI is closed)
    SecondThread()
    
    