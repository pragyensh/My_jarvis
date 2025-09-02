# Import required libraries
from AppOpener import close, open as appopen  # Import functions to open and close apps.
from webbrowser import open as webopen  # Import web browser functionality.
from pywhatkit import search, playonyt  # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values  # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML content.
from rich import print  # Import rich for styled console output.
from groq import Groq  # Import Groq for AI chat functionalities.
import webbrowser  # Import webbrowser for opening URLs.
import subprocess  # Import subprocess for interacting with the system.
import requests  # Import requests for making HTTP requests.
import keyboard  # Import keyboard for keyboard-related actions.
import asyncio  # Import asyncio for asynchronous programming.
import os  # Import os for operating system functionalities.

# Load environment variables from the .env file.
env_vars = dotenv_values('.env')
GroqAPIkey = env_vars.get("GroqAPIKey")  # Retrieve the Groq API key.
Username = env_vars.get("Username", "User")  # Retrieve the username

# Define CSS classes for parsing specific elements in HTML content.
classes = [
    "Zclubnf", "HgKELc", "LIKOO sY7rlc", "ZQLCW", "gsrt vk_bk FzvwSb YwPhnf", 
    "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "OSuRdd LIKOO", 
    "VLY6d", "webanswers-webanswers_table__webanswers-table", "dDoMo ikbd8b gsrt", 
    "sXLa0e", "LMKKe", "VQF4g", "qv3mpe", "kno-rdesc", "SPZz6b"
]

# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize the Groq client with the API key.
if GroqAPIkey:
    client = Groq(api_key=GroqAPIkey)
else:
    client = None
    print("Groq API key not found. AI features disabled.")

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = {'role': "system", "content": f"Hello, I am {Username}, You're a content writer. You have to write content like letters, articles, and other documents."}

# Function to perform a Google search.
def GoogleSearch(Topic):
    try:
        search(Topic)  # Use pywhatkit's search function to perform a Google search.
        return True  # Indicate success
    except Exception as e:
        print(f"Google search error: {e}")
        # Fallback: open browser directly
        webbrowser.open(f"https://www.google.com/search?q={Topic}")
        return True

# Function to generate content using AI and save it to a file.
def Content(Topic):
    if not client:
        return "AI features disabled. Please set GroqAPIKey in .env file."
    
    # Nested function to open a file in Notepad.
    def OpenNotepad(file):
        try:
            subprocess.Popen(['notepad.exe', file])  # Open the file in Notepad.
        except Exception as e:
            print(f"Error opening notepad: {e}")

    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append({'role': 'user', "content": f"{prompt}"})  # Add the user's prompt to messages.

        try:
            # Use a current model instead of the deprecated one
            completion = client.chat.completions.create(
                model="llama3-70b-8192",  # Updated to a current model
                messages=[SystemChatBot] + messages,  # Include system instructions and chat history.
                max_tokens=2048,  # Limit the maximum tokens in the response.
                temperature=0.7,  # Adjust response randomness.
                top_p=1,  # Use nucleus sampling for response diversity.
                stream=True,  # Enable streaming response.
                stop=None  # Allow the model to determine stopping conditions.
            )

            Answer = ""  # Initialize an empty string for the response.

            # Process streamed response chunks.
            for chunk in completion:
                if chunk.choices[0].delta.content:  # Check for content in the current chunk.
                    Answer += chunk.choices[0].delta.content  # Append the content to the answer.

            Answer = Answer.replace("</s>", "")  # Remove unwanted tokens from the response.
            messages.append({'role': 'assistant', 'content': Answer})  # Add the AI's response to messages.
            return Answer
        except Exception as e:
            return f"Error generating content: {e}"

    Topic = Topic.replace("Content ", "")  # Remove "Content " from the topic.
    ContentByAI = ContentWriterAI(Topic)  # Generate content using AI.

    # Save the generated content to a text file.
    try:
        os.makedirs("Data", exist_ok=True)
        filename = f"Data\\{Topic.lower().replace(' ', '')}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(ContentByAI)  # Write the content to the file.

        OpenNotepad(filename)  # Open the file in Notepad.
        return True
    except Exception as e:
        return f"Error saving content: {e}"

# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    try:
        Uri4Search = f"https://www.youtube.com/results?search_query={Topic}"  # Construct the YouTube search URL.
        webbrowser.open(Uri4Search)  # Open the search URL in a web browser.
        return True  # Indicate success.
    except Exception as e:
        print(f"YouTube search error: {e}")
        return False

# Function to play a video on YouTube.
def PlayYoutube(query):
    try:
        playonyt(query)  # Use pywhatkit's playonyt function to play the video.
        return True  # Indicate success.
    except Exception as e:
        print(f"YouTube play error: {e}")
        # Fallback: open YouTube search
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return True

# Function to open an application or a relevant webpage.
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)  # Attempt to open the app.
        return True  # Indicate success.
    except Exception as e:
        print(f"Error opening app {app}: {e}")
        # Fallback: search for the app online
        webbrowser.open(f"https://www.google.com/search?q={app}")
        return True

# Function to close an application.
def CloseApp(app):
    if "chrome" in app.lower():
        # Special handling for Chrome
        try:
            if os.name == 'nt':  # Windows
                os.system('taskkill /f /im chrome.exe')
            else:  # Linux/Mac
                os.system('pkill chrome')
            return True
        except Exception as e:
            print(f"Error closing Chrome: {e}")
            return False
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)  # Attempt to close the app.
            return True  # Indicate success.
        except Exception as e:
            print(f"Error closing app {app}: {e}")
            return False
 

# Function to execute system-level commands.
def System(command):
    if not KEYBOARD_AVAILABLE:
        return "Keyboard module not available. System controls disabled."
    
    # Nested function to mute the system volume.
    def mute():
        try:
            keyboard.press_and_release("volume mute")  # Simulate the mute key press.
        except Exception as e:
            print(f"Error muting: {e}")

    # Nested function to unmute the system volume.
    def unmute():
        try:
            keyboard.press_and_release("volume mute")  # Simulate the unmute key press.
        except Exception as e:
            print(f"Error unmuting: {e}")

    # Nested function to increase the system volume.
    def volume_up():
        try:
            keyboard.press_and_release("volume up")  # Simulate the volume up key press.
        except Exception as e:
            print(f"Error increasing volume: {e}")

    # Nested function to decrease the system volume.
    def volume_down():
        try:
            keyboard.press_and_release("volume down")  # Simulate the volume down key press.
        except Exception as e:
            print(f"Error decreasing volume: {e}")

    # Execute the appropriate command.
    try:
        if command == "mute":
            mute()
        elif command == "unmute":
            unmute()
        elif command == "volume up":
            volume_up()
        elif command == "volume down":
            volume_down()
        else:
            return f"Unknown system command: {command}"

        return True  # Indicate success
    except Exception as e:
        return f"Error executing system command: {e}"

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):
    funcs = []  # List to store asynchronous tasks.

    for command in commands:
        command = command.strip()
        if not command:
            continue
            
        if command.startswith("open "):  # Handle "open" commands.
            if "open it" in command:  # Ignore "open it" commands.
                pass
            elif "open file" == command:  # Ignore "open file" commands.
                pass
            else:
                app_name = command.removeprefix("open ").strip()
                fun = asyncio.to_thread(OpenApp, app_name)
                funcs.append(fun)  # Schedule app opening.
                
        elif command.startswith("general "):
            pass  # Placeholder for general commands.
            
        elif command.startswith("realtime "):
            pass  # Placeholder for real-time commands.
            
        elif command.startswith("close "):
            app_name = command.removeprefix("close ").strip()
            fun = asyncio.to_thread(CloseApp, app_name)
            funcs.append(fun)  # Schedule app closing.
            
        elif command.startswith("play "):
            query = command.removeprefix("play ").strip()
            fun = asyncio.to_thread(PlayYoutube, query)
            funcs.append(fun)  # Schedule YouTube playback.
            
        elif command.startswith("content "):
            topic = command.removeprefix("content ").strip()
            fun = asyncio.to_thread(Content, topic)
            funcs.append(fun)  # Schedule content creation.
            
        elif command.startswith("google search "):
            query = command.removeprefix("google search ").strip()
            fun = asyncio.to_thread(GoogleSearch, query)
            funcs.append(fun)  # Schedule Google search.
            
        elif command.startswith("youtube search "):
            query = command.removeprefix("youtube search ").strip()
            fun = asyncio.to_thread(YouTubeSearch, query)
            funcs.append(fun)  # Schedule YouTube search.
            
        elif command.startswith("system "):
            sys_command = command.removeprefix("system ").strip()
            fun = asyncio.to_thread(System, sys_command)
            funcs.append(fun)  # Schedule system command.
            
        else:
            print(f"No Function Found. For {command}")  # Print an error for unrecognized commands.

    if funcs:
        results = await asyncio.gather(*funcs, return_exceptions=True)  # Execute all tasks concurrently.

        for result in results:  # Process the results.
            if isinstance(result, Exception):
                yield f"Error: {result}"
            elif isinstance(result, str):
                yield result
            else:
                yield str(result)
    else:
        yield "No valid commands to execute."

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    results = []
    async for result in TranslateAndExecute(commands):  # Translate and execute commands.
        results.append(result)
        print(result)

    return True  # Indicate success.

# Check if keyboard is available
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Keyboard module not available. System controls disabled.")

# Example usage
if __name__ == "__main__":
    # Test the automation system
    test_commands = ["open chrome", "google search python programming", "content article about AI"]
    
    try:
        result = asyncio.run(Automation(test_commands))
        print(f"Automation completed: {result}")
    except Exception as e:
        print(f"Error running automation: {e}")
        
        