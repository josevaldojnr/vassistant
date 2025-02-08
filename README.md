Assistente de Voz (UNIMED)

<h1>INSTALAÇÃO</h1>
<li>
  Crie uma conta na AWS
</li>
<li>
  Defina um usuario IAM com permisssões para bucket S3
</li>
<li>
  Crie um bucket S3 para armazenar os arquivos de audio.
</li>
<li>
  Clone o repositório <code>git clone https://github.com/josevaldojnr/vassistant.git</code>
</li>
<li>
  Instale as dependências do definidas no arquivo <code>requirements.txt</code> - <code>pip install -r requirements.txt</code>
</li>
<li>
  Altere o caminho definido nos scripts para encontrar o modelo desejado.<br>
  <code>model = whisper.load_model("/your_path/base.pt", device='cuda')</code>
</li>
<li>
  Crie um arquivo .env na pasta raiz do repositório, esta irá conter as variaveis de configuração para acesso ao bucket S3<br>
  Nesse arquivo insira as credencias de de acesso:<br>
   <code>AWS_ACCESS_KEY_ID='***********'
 AWS_SECRET_ACCESS_KEY='************'
 AWS_REGION_NAME='***********'
 S3_BUCKET_NAME='**********'</code>
  
</l1>
<li>
  Adicione o arquivo .env ao <code>.gitignore</code>
</li>
