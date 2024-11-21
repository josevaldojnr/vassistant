import boto3
import whisper
from pydub import AudioSegment
import os
from dotenv import load_dotenv
from torch.cuda.amp import autocast
import subprocess
import warnings
import re

warnings.simplefilter(action='ignore', category=FutureWarning)


keywords = ["fome","estou com fome", "dor", "estou com dor", "que dor", "passando mal","sentindo mal","sede","estou com sede"]
load_dotenv()

s3=boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)
bucket='s3-audio-voice-assist'

model = whisper.load_model("./whisper/models/base.pt", device='cuda')

####################
####################
####################
####################

def process_text (text):
    processed_text = re.sub(r'[^\w\s]', '', text)
    return processed_text.lower().split()

def trigger_assistent(model_result, keywords):
  words=(model_result.get("text","")).lower().split()
  words= " ".join(words)
  words=process_text(words)
  for keyword in keywords:
    if keyword.lower() in words:
     subprocess.run(["python","activate_assist.py"])
     return True

def list_audio(bucket):
    reply= s3.list_objects_v2(Bucket=bucket)
    return [item['Key'] for item in reply.get('Contents', []) if item['Key'].endswith(('.mp3', '.wav'))] 

def download_audio(s3_key):
    print(keywords)
    transcription={}
    for key in s3_key:
        filename= key.split('/')[-1]
        s3.download_file(bucket, key, filename)
        result = model.transcribe(filename)
        transcription[key]= result['text']
        print(transcription[key])
        print(f'----------------------------------------------------')
        if trigger_assistent(result,keywords):
           return 
        os.remove(filename)
    return   
     

#def combine_audio():

if __name__ == "__main__":  
    audio_keys=list_audio(bucket)
    if audio_keys:
        download_audio(audio_keys)
    else:
        print("No audio chunks found in S3 bucket.")
