
#ESTE É UM CODIGO EXPERIMENTAL, UTILIZANDO STREAMING DE AUDIO COM OBJETIVO DE REDUZIR A LATENCIA NA TRANSCRIÇÃO, É NECESSÁRIO UMA REVISÃO NESSE CONCEITO
import boto3
import whisper
import os
from dotenv import load_dotenv
from torch.cuda.amp import autocast
from time import sleep
from pydub import AudioSegment
import numpy as np
import io


load_dotenv()

s3=boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)
bucket='s3-audio-voice-assist'

model = whisper.load_model("./whisper/models/base.pt", device='cuda')

def list_audio(bucket):
    reply= s3.list_objects_v2(Bucket=bucket)
    return [item['Key'] for item in reply.get('Contents', []) if item['Key'].endswith(('.mp3', '.wav'))] 

def download_audio(s3_key):
    transcription={}
    for key in s3_key:
        filename= key.split('/')[-1]
        s3.download_file(bucket, key, filename)
        with autocast():   
            result = model.transcribe(filename)
        transcription[key]= result['text']
        print(transcription[key])
        os.remove(filename)
    return transcription    
     
def stream_audio_from_s3(bucket_name, file_key):
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    audio_stream = obj['Body']
    chunk_size = 1024 * 8
    while True:
        data = audio_stream.read(chunk_size)
        data = data.set_channels(1).set_frame_rate(16000)
        data = np.array(data.get_array_of_samples(), dtype=np.float32)
        with autocast():   
            result = model.transcribe(data)
        print(result)
        if not data:
            break
        print(f"Read {len(data)} bytes")


def keep_stream(bucket):
    s3_client = boto3.client('s3')
    audio_files = set()
    while True:
        response = s3_client.list_objects_v2(Bucket=bucket)
        for obj in response.get('Contents', []):
            file_key = obj['Key']
            if file_key not in audio_files:
                stream_audio_from_s3(bucket, file_key)
                audio_files.add(file_key)
        sleep(10)

keep_stream(bucket)
