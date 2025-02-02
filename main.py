import requests
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista de contatos para receber alertas
CONTACTS = ["+351933825194", "+351937838650"]

def send_alerts():
    """Envia SMS e faz chamadas de voz em simultâneo"""
    try:
        # Autenticação
        auth_response = requests.post(
            "https://api.smsbuzz.net/api/accesstoken",
            json={
                "Username": "nuno.guilherme@formasimples.pt",
                "Password": "Ng46533850.*"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if auth_response.status_code != 200:
            logger.error("Falha na autenticação")
            return False, "Falha na autenticação"
            
        token = auth_response.json().get("AccessToken")
        logger.info("Autenticação realizada com sucesso")
        
        # Envio único de SMS para todos os contatos
        sms_response = requests.post(
            "https://api.smsbuzz.net/sms/sendmessage",
            json={
                "SenderName": "DAE SOS",
                "Destinations": CONTACTS,  # Lista completa de contatos
                "Text": "SOS DAE, SOS DAE. Alerta Cabine DAE Pavilhão Casa do Povo, operacionais em menos de 3 minutos.",
                "IsUnicode": "True"
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        logger.info(f"SMS enviado: {sms_response.status_code}")
        
        # Chamadas de voz para todos os contatos
        voice_data = {
            "Text": "SOS, DAÉ, SOS, DAÉ. DAÉ, Pavilhão Casa do Povo. Operacionais DAÉ, em menos de 3 minutos. Responda com, 1, a caminho, 2, indisponível.",
            "Language": "pt-PT",
            "TTSVoice": "pt-PT-RaquelNeural",
            "AudioFile": "",
            "CallerId": "351300505120"
        }
        
        for contact in CONTACTS:
            voice_data["Destinations[]"] = contact
            voice_response = requests.post(
                "https://api.smsbuzz.net/call/send",
                data=voice_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            logger.info(f"Chamada iniciada para {contact}: {voice_response.status_code}")
            
        return True, "Alertas enviados com sucesso"
        
    except Exception as e:
        logger.error(f"Erro no envio de alertas: {str(e)}")
        return False, str(e)

@app.route('/trigger', methods=['GET', 'POST'])
def trigger():
    success, message = send_alerts()
    return jsonify({"success": success, "message": message})

@app.route('/', methods=['GET'])
def home():
    return "Sistema de Alerta DAE - Ativo"

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=3000)
