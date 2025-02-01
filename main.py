import os
import requests
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate_smsbuzz():
   """Autenticação na API SMSBuzz"""
   auth_url = "https://api.smsbuzz.net/api/accesstoken"
   headers = {
       "Content-Type": "application/json"
   }
   auth_data = {
       "Username": "nuno.guilherme@formasimples.pt",
       "Password": "Ng46533850.*"
   }
   
   try:
       response = requests.post(auth_url, json=auth_data, headers=headers)
       logger.info(f"Auth Response Code: {response.status_code}")
       logger.info(f"Auth Response Body: {response.text}")
       
       if response.status_code == 200:
           return response.json().get("AccessToken")
       return None
   except Exception as e:
       logger.error(f"Auth Error: {str(e)}")
       return None

def send_sms(token):
   """Função para envio de SMS"""
   try:
       sms_url = "https://api.smsbuzz.net/sms/sendmessage"
       headers = {
           "Authorization": f"Bearer {token}",
           "Content-Type": "application/json"
       }
       
       sms_data = {
           "SenderName": "DAE SOS",
           "Destinations": ["+351933825194", "+351937838650"],
           "Text": "SOS DAE, SOS DAE. Alerta Cabine DAE Pavilhão Casa do Povo, operacionais em menos de 3 minutos.",
           "IsUnicode": "True"
       }
       
       logger.info(f"Enviando SMS com dados: {sms_data}")
       response = requests.post(sms_url, json=sms_data, headers=headers)
       logger.info(f"SMS Response Code: {response.status_code}")
       logger.info(f"SMS Response Text: {response.text}")
       
       return response.status_code == 200, response.text
   except Exception as e:
       logger.error(f"Erro no envio do SMS: {str(e)}")
       return False, str(e)

def make_voice_call(token):
   """Função para realizar chamada de voz"""
   try:
       voice_url = "https://api.smsbuzz.net/call/send"
       headers = {
           "Authorization": f"Bearer {token}",
           "Content-Type": "application/x-www-form-urlencoded"
       }
       
       # Formatando dados para form-data
       voice_data = {
           "Destinations[]": "+351933825194",  # Um destino por vez
           "Text": "SOS, DAÉ, SOS, DAÉ. DAÉ, Pavilhão Casa do Povo. Operacionais DAÉ, em menos de 3 minutos. Responda com, 1, a caminho, 2, indisponível.",
           "Language": "pt-PT",
           "TTSVoice": "pt-PT-RaquelNeural",
           "AudioFile": ""
       }
       
       # Lista de números para chamar
       destinations = ["+351933825194", "+351937838650"]
       responses = []
       
       # Fazer uma chamada para cada destino
       for dest in destinations:
           voice_data["Destinations[]"] = dest
           logger.info(f"Iniciando chamada de voz para {dest}")
           response = requests.post(voice_url, data=voice_data, headers=headers)
           logger.info(f"Voice Call Response Code for {dest}: {response.status_code}")
           logger.info(f"Voice Call Response Text for {dest}: {response.text}")
           responses.append({"destination": dest, "success": response.status_code == 200})
       
       # Verifica se todas as chamadas foram bem sucedidas
       all_success = all(r["success"] for r in responses)
       return all_success, str(responses)
   except Exception as e:
       logger.error(f"Erro na chamada de voz: {str(e)}")
       return False, str(e)

@app.route('/trigger', methods=['GET', 'POST'])
def trigger_alert():
   try:
       logger.info("Recebido sinal da Shelly - Iniciando processo")
       
       # Autenticação única
       token = authenticate_smsbuzz()
       if not token:
           logger.error("Falha na autenticação")
           return jsonify({"success": False, "message": "Falha na autenticação"}), 401

       # Envio de SMS
       sms_success, sms_response = send_sms(token)
       
       # Chamada de voz
       voice_success, voice_response = make_voice_call(token)
       
       # Verifica resultados
       return jsonify({
           "success": sms_success or voice_success,
           "message": "Processo concluído",
           "sms_status": {"success": sms_success, "response": sms_response},
           "voice_status": {"success": voice_success, "response": voice_response}
       })

   except Exception as e:
       logger.error(f"Erro no processo: {str(e)}")
       return jsonify({
           "success": False,
           "message": f"Erro no processo: {str(e)}"
       }), 500

@app.route('/', methods=['GET'])
def home():
   return "Sistema de Alerta DAE - Ativo"

if __name__ == '__main__':
   app.run(debug=False, host="0.0.0.0", port=3000)
