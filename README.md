## Instalação

Para instalar o aplicativo em Python, siga as etapas abaixo:

1. Clone o repositório:
   
   `git clone https://github.com/seu-usuario/nome-do-repositorio.git`
   
2. Navegue até o diretório do projeto:
   
   `cd nome-do-repositorio`
   
3. Crie um ambiente virtual (opcional, mas recomendado):
   
   `python -m venv myenv`
   
4. Ative o ambiente virtual:
   - Windows:

     &#x20;`myenv\Scripts\activate`
     
   - Linux/macOS:&#x20;

     `source myenv/bin/activate`
     
5. Instale as dependências do projeto:
   
   `pip install -r requirements.txt`
   
6. Execute o aplicativo usando o Uvicorn:&#x20;

   `uvicorn main:app --host=0.0.0.0 --port=8080`

Agora, o aplicativo estará disponível em http://localhost:8080.

## Instalação via Docker

Você também pode executar o aplicativo usando o Docker. Certifique-se de ter o Docker instalado e siga as etapas abaixo:

1. Clone o repositório:
   
   `git clone https://github.com/seu-usuario/nome-do-repositorio.git`
   
2. Navegue até o diretório do projeto:
   
   `cd nome-do-repositorio`
   
3. Construa a imagem do Docker:
   
   `docker build -t nome-do-aplicativo .`
   
4. Execute o contêiner do Docker:
   
   `docker run -p 8080:8090 nome-do-aplicativo`

Agora, o aplicativo estará disponível em <http://localhost:8080>.

## Utilizando a GPU

Se você deseja usar o método da GPU, siga as etapas abaixo:

1. Alugue uma GPU em <https://cloud.vast.ai/create/.>
2. Escolha a imagem stable-diffusion:web-automatic-8.0.1.
3. No arquivo .env.example, substitua IP\_DA\_GPU pelo IP da GPU alugada e renomeie o arquivo para .env.

## Implantação no Heroku

Este repositório já está configurado para ser implantado no Heroku usando a autorização de acesso ao GitHub. Basta seguir as etapas apropriadas no Heroku para conectar seu repositório e fazer a implantação.


 
