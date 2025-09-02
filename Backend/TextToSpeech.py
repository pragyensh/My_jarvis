import pygame
import random
import asyncio
import edge_tts
import os
import time
import uuid
import threading
from dotenv import dotenv_values

# Initialize pygame
pygame.init()
pygame.mixer.init()

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# Store references to files that need cleanup
files_to_cleanup = []
cleanup_lock = threading.Lock()

async def TextToAudioFile(text) -> str:
    # Create a unique filename for each speech request
    unique_id = uuid.uuid4().hex
    file_path = os.path.join("Data", f"speech_{unique_id}.mp3")
    
    # Ensure the Data directory exists
    os.makedirs("Data", exist_ok=True)
    
    try:
        communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
        await communicate.save(file_path)
        
        # Verify the file was created and has content
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise Exception("Generated MP3 file is empty or doesn't exist")
            
        return file_path
    except Exception as e:
        # Clean up the potentially corrupted file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise e

def is_valid_mp3(file_path):
    """Check if the MP3 file is valid by trying to load it"""
    try:
        # Try to create a sound object to validate the MP3
        sound = pygame.mixer.Sound(file_path)
        return True
    except:
        return False

def delayed_cleanup(file_path, delay=2.0):
    """Clean up a file after a delay to ensure it's no longer in use"""
    time.sleep(delay)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # If still in use, add to global cleanup list
        with cleanup_lock:
            files_to_cleanup.append(file_path)
        print(f"Warning: Could not remove temporary file: {e}")

def TTS(Text, func=lambda r=None: True):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Generate a new file for each request
            file_path = asyncio.run(TextToAudioFile(Text))
            
            # Wait briefly to ensure file is ready
            time.sleep(0.2)
            
            # Validate the MP3 file before trying to play it
            if not is_valid_mp3(file_path):
                print("Generated MP3 file is corrupt, retrying...")
                retry_count += 1
                try:
                    os.remove(file_path)
                except:
                    pass
                continue
            
            # Load and play the audio
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                if not func():
                    break
                pygame.time.Clock().tick(10)
            
            # Stop the music and unload the file
            pygame.mixer.music.stop()
            
            # Start cleanup in a separate thread after a delay
            cleanup_thread = threading.Thread(target=delayed_cleanup, args=(file_path,))
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
            return True

        except Exception as e:
            print(f"Error in TTS function: {e}")
            retry_count += 1
            time.sleep(1)  # Delay to prevent rapid retry
    
    print(f"Failed to generate valid audio after {max_retries} attempts")
    return False

def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(Data) > 4 and len(Text) >= 250:
        success = TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    else:
        success = TTS(Text, func)
    
    if not success:
        print("Could not generate audio for the given text")

def cleanup_old_files():
    """Clean up any old speech files that might be left over"""
    data_dir = "Data"
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.startswith("speech_") and file.endswith(".mp3"):
                try:
                    os.remove(os.path.join(data_dir, file))
                except:
                    pass  # Ignore errors during cleanup

def cleanup_all_files():
    """Clean up all temporary files, including those that couldn't be deleted earlier"""
    global files_to_cleanup
    
    # Clean up regular files
    cleanup_old_files()
    
    # Clean up files that previously failed to delete
    with cleanup_lock:
        for file_path in files_to_cleanup:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass  # Ignore any errors during final cleanup
        files_to_cleanup = []

if __name__ == "__main__":
    try:
        # Clean up any old files before starting
        cleanup_old_files()
        
        while True:
            text_input = input("Enter the text: ")
            if text_input.lower() in ['exit', 'quit', 'stop']:
                break
            TextToSpeech(text_input)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Final cleanup of all files
        cleanup_all_files()
        pygame.mixer.quit()
        pygame.quit()
        
        