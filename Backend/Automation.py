# Import required libraries
from AppOpener.features import AppNotFound  # <-- This is needed to catch the specific error
from Backend.TextToSpeech import TextToSpeech  # Optional: if you're using TTS


from AppOpener import close, open as appopen # Import functions to open and close apps.
from webbrowser import open as webopen # Import web browser functionality.
from pywhatkit import search, playonyt # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup #Import BeautifulSoup for parsing HTML content.
from rich import print # Import rich for styled console output.
from groq import Groq # Import Groq for AI chat functionalities.
import webbrowser # Import webbrowser for opening URLS.
import subprocess # Import subprocess for interacting with the system.
import requests # Import requests for making HTTP requests.
import keyboard #Import keyboard for keyboard-related actions.
import asyncio # Import asyncio for asynchronous programming.
import os # Import os for operating system Functionalities.

# Load environment variables from the .env file.
env_vars=dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey") # Retrieve the Groq API key

# Define CSS classes for parsing specific elements in HTML content.
classes = ["zCubwf", "hgKElc", "LTK00 SY7ric", "ZOLCW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
            "IZ6rdc", "05uR6d LTK00", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
            "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]
# Define a user-agent for making web requests.
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]

messages =[]

def fetch_search_html(query):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(
        f"https://www.google.com/search?q={query}",
        headers=headers
    )
    return response.text

def extract_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/url?q="):
            clean_link = href.split("/url?q=")[1].split("&")[0]
            if not clean_link.startswith("https://www.google.com"):
                links.append(clean_link)

    return links

# System message to provide context to the chatbot.
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like lettrs, codes, applications, essays, notes, songs, poems etc."}]
# Function to perform a Google search.
def GoogleSearch(Topic):
    search (Topic) # Use pywhatkit's search function to perform a Google search.
    return True # Indicate success.
# Function to generate content using AI and save it to a file.
def Content (Topic):





# Nested function to open file in Notepad.
    def OpenNotepad (File):
        default_text_editor = 'notepad.exe' # Default text editor.
        subprocess.Popen([default_text_editor, File]) # Open the file in notepad.
    
    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI (prompt):
        messages.append({"role": "user", "content": f"{prompt}"}) # Add the user's prompt to messages.
        completion = client.chat.completions.create(
            model="llama3-8b-8192", # Specify the AI model.
            messages=SystemChatBot + messages, # Include system instructions and chat history.
            max_tokens=2048, # Limit the maximum tokens in the response.
            temperature=0.7, # Adjust response randomness.
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""
        
        # Process streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content: # Check for content in the current chunk.
                Answer += chunk.choices[0].delta.content # Append the content to the answer.
        
        Answer = Answer.replace("</s>", "") # Remove unwanted tokens from the response.
        messages.append({"role": "assistant", "content": Answer}) # Add the AI's response to messages.
        return Answer

    Topic: str = Topic.replace("Content", "") # Remove "Content" from the topic.
    ContentByAI = ContentWriterAI(Topic) # Generate content using AI.
    # Save the generated content to a text file.
    with open(rf"Data\{Topic. lower().replace('','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI) # Write the content to the file.
        file.close()
    OpenNotepad (rf"Data\{Topic.lower().replace('','')}.txt") # Open the file in Notepad.
    return True # Indicate success.





# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}" # Construct the YouTube search URL.
    webbrowser.open(Url4Search) # Open the search URL in a web browser.
    return True # Indicate success.
# Function to play a video on YouTube.
def PlayYoutube (query):
    playonyt (query) # Use pywhatkit's playonyt function to play the video.
    return True # Indicate success.



# Function to open an application or a relevant webpage.
def OpenApp(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"[+] Opened {app} as a local application.")
    except AppNotFound as e:
        print(f"[!] App not found: {app}. Attempting fallback via browser. Error: {e}")

        if app.lower() == "youtube":
            webbrowser.open("https://www.youtube.com")
            TextToSpeech("Opening YouTube in your browser.")
            return

        try:
            html = fetch_search_html(app)
            links = extract_links(html)
            if links:
                link = links[0]
                webbrowser.open(link)
                TextToSpeech(f"Opening {app} in your browser.")
            else:
                webbrowser.open(f"https://www.google.com/search?q={app}")
                TextToSpeech(f"I couldn't find a direct link, but opened search results for {app}.")
        except Exception as e:
            print(f"[!] Failed to fetch/search. Error: {e}")
            webbrowser.open(f"https://www.google.com/search?q={app}")
            TextToSpeech(f"I had trouble opening {app}, so I opened Google search instead.")


def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True) # Attempt to close the app.
            return True # Indicate success.
        except:
            return False # Indicate failure.
        
def System(command):
    def mute():
        keyboard.press_and_release("volume mute")
    
    def unmute():
        keyboard.press_and_release("volume mute")
    
    def volume_up():
        keyboard.press_and_release("volume up")
        
    def volume_down():
        keyboard.press_and_release("volume down")
        
        
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True


# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):
    funcs = [] # List to store asynchronous tasks.
    for command in commands:
        if command.startswith("open "): # Handle "open" commands.
            if "open it" in command: # Ignore "open it" commands.
                pass
            
            if "open file" == command:
                pass
            else:
                fun= asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
        elif command.startswith("general "):
            pass
        
        elif command.startswith("realtime "):
            pass 
        
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
            
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
            
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
            
        else:
            print(f"No function found. For {command}")
    
    results = await asyncio.gather(*funcs)
    
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result


async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True       


if __name__ =="__main__":
    asyncio.run(Automation([]))