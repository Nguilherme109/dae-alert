import requests
from flask import Flask, request, jsonify
import logging
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lista atualizada de contatos
CONTACTS = [
    "351933825194", "351937838650",  # Contatos originais
    "351933734373", "351966934017", "351924142009", 
    "351936277615", "351938458212", "351916418429",
    "351927246949", "351936835610"   # Novos contatos
]

def send_alerts():
    """Envia SMS e faz chamadas de voz"""
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
            logger.error(f"Falha na autenticação: {auth_response.text}")
            return False, "Falha na autenticação"
            
        token = auth_response.json().get("AccessToken")
        logger.info("Autenticação realizada com sucesso")
        
        time.sleep(1)
        
        # Envio de SMS com nova mensagem
        sms_data = {
            "SenderName": "DAE SOS",
            "Destinations": CONTACTS,
            "Text": "Teste e envio de sms - SOS DAE, SOS DAE. Alerta Cabine DAE Pavilhão Casa do Povo, operacionais em menos de 3 minutos. Forma Simples",
            "IsUnicode": True
        }
        
        logger.info(f"Enviando SMS com dados: {sms_data}")
        
        sms_response = requests.post(
            "https://api.smsbuzz.net/sms/sendmessage",
            json=sms_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        logger.info(f"Resposta SMS - Status: {sms_response.status_code}")
        logger.info(f"Resposta SMS - Corpo: {sms_response.text}")
        
        time.sleep(1)
        
        # Chamadas de voz com nova mensagem
        voice_data = {
            "Text": "Teste chamada de voz - SOS, DAÉ, SOS, DAÉ. DAÉ, Pavilhão Casa do Povo. Operacionais DAÉ, em menos de 3 minutos. Responda com, 1, a caminho, 2, indisponível. Forma Simples",
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
            logger.info(f"Chamada para {contact} - Status: {voice_response.status_code}")
            logger.info(f"Chamada para {contact} - Resposta: {voice_response.text}")
            time.sleep(1)
            
        return True, "Alertas enviados com sucesso"
        
    except Exception as e:
        logger.error(f"Erro no envio de alertas: {str(e)}")
        return False, str(e)

@app.route('/trigger', methods=['GET'])
def trigger():
    success, message = send_alerts()
    return jsonify({
        "success": success, 
        "message": message,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/', methods=['GET'])
def home():
    return "Sistema de Alerta DAE - Ativo"

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=3000)
