import os
from telegram import Voice
import aiohttp
import aiofiles
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(base_url="https://api.groq.com/openai/v1",
    api_key=OPENAI_API_KEY)

async def handle_audio_message(voice: Voice) -> str:
    """
    Download and save the audio file from a Telegram voice message.
    
    :param voice: Voice object from the Telegram message
    :return: Path to the saved audio file
    """
    file_id = voice.file_id
    file = await voice.get_file()
    file_path = file.file_path
    
    # Create a temporary directory for audio files if it doesn't exist
    os.makedirs("temp_audio", exist_ok=True)
    
    local_filename = os.path.join("temp_audio", f"{file_id}.ogg")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(file_path) as resp:
            if resp.status == 200:
                async with aiofiles.open(local_filename, mode='wb') as f:
                    await f.write(await resp.read())
    
    return local_filename


def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe the audio file using OpenAI's Whisper API.
    
    :param audio_file_path: Path to the audio file
    :return: Transcribed text
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3", 
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")
    finally:
        # Clean up the temporary audio file
        os.remove(audio_file_path)