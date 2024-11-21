import boto3
import pyaudio
import wave
import io
import os
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from pydub import AudioSegment




load_dotenv(override=True)

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
#parametetros audio file
AUDIO_SIZE = 1024 
FORMAT = pyaudio.paInt16 
CHANNELS = 1  
RATE = 44100  
#condição de parada de captura
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 3

#s3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

#--------------------------------------------
def start_stream():
    audio= pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,input=True,frames_per_buffer=AUDIO_SIZE)
    return audio, stream
#----------------------------------------------
def silence_cut(audio):
    audio_data=np.frombuffer(audio,dtype=np.int16)
    volume = np.abs(audio_data).mean()
    return volume< SILENCE_THRESHOLD
#----------------------------------------------

def convert_wav_mp3(wav_audio):
    wav_buffer = io.BytesIO(wav_audio)
    mp3_buffer = io.BytesIO()
    audio_seg = AudioSegment.from_wav(wav_buffer)
    
    try:
        audio_seg.export(mp3_buffer, format='mp3', bitrate='128k')
    except Exception as e:
        print(f"Error occurred during export: {e}")
    
    mp3_buffer.seek(0)
    return mp3_buffer.getvalue()  


#------------------------------------------------
def upload_to_s3(mp3, id):
    filename = f"audio_{id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    try:
        s3_client.upload_fileobj(
            io.BytesIO(mp3),
            S3_BUCKET_NAME,
            filename,
            ExtraArgs={'ContentType': 'audio/mp3'}
        )
        print(f"Upload com sucesso: {filename}")
    except Exception as e:
        print(f"erro ao fazer upload do arquivo {filename}: {e}")
#---------------------------------------------------
def save_and_upload(frames, id):
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    mp3_data = convert_wav_mp3(wav_buffer.getvalue())
    upload_to_s3(mp3_data, id)
#------------------------------------------------
def record():
    audio,stream=start_stream()
    print(f"Gravando novo audio")

    id=0
    frames=[]
    silent_count=0
    target_cut=int(SILENCE_DURATION * RATE/ AUDIO_SIZE)

    try:
        while True:
            audio_data = stream.read(AUDIO_SIZE)
            frames.append(audio_data)
                        
            if silence_cut(audio_data):
                silent_count+=1 
            else:
                silent_count=0
            if silent_count>=target_cut:
                print(f"Silencio detectado, finalizando audio")
                save_and_upload(frames,id)
                frames = []
                id += 1
                silent_count = 0

    except KeyboardInterrupt:
        print(f"Gravação interrompida")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
 #--------------------------------------------

if __name__ == "__main__":
    record()
