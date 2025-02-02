import requests
from flask import Flask, request, jsonify
import logging
from datetime import datetime
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONTACTS = [
    "351933825194", "351937838650", "351933734373", 
    "351966934017", "351924142009", "351936277615", 
    "351938458212", "351916418429", "351927246949", 
    "351936835610"
]

last_execution_time = None
MIN_INTERVAL = 60

def can_send_alert():
    global last_execution_time
    now = datetime.now()
    
    if last_execution_time is None:
        last_execution_time = now
        return True
        
    if (now - last_execution_time).seconds < MIN_INTERVAL:
        logger.warning("Bloqueado: Tentativa de envio muito próxima")
        return False
        
    last_execution_time = now
    return True

def send_alert():
    try:
        if not can_send_alert():
            return False, "Aguarde 60 segundos entre alertas"

        logger.info("Iniciando novo processo de alertas")

        auth_response = requests.post(
            "https://api.smsbuzz.net/api/accesstoken",
            json={
                "Username": "nuno.guilherme@formasimples.pt",
                "Password": "Ng46533850.*"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if auth_response.status_code != 200:
            return False, "Falha na autenticação"
            
        token = auth_response.json().get("AccessToken")
        logger.info("Autenticação realizada com sucesso")

        sms_response = requests.post(
            "https://api.smsbuzz.net/sms/sendmessage",
            json={
                "SenderName": "DAE SOS",
                "Destinations": CONTACTS,
                "Text": "Teste e envio de sms - SOS DAE, SOS DAE. Alerta Cabine DAE Pavilhão Casa do Povo, operacionais em menos de 3 minutos. Forma Simples",
                "IsUnicode": True
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if sms_response.status_code != 200:
            logger.error(f"Erro no envio de SMS: {sms_response.text}")
            return False, "Falha no envio de SMS"
            
        logger.info("SMS enviados com sucesso")

        voice_data = {
            "Text": "Teste chamada de voz - SOS, DAÉ, SOS, DAÉ. DAÉ, Pavilhão Casa do Povo. Operacionais DAÉ, em menos de 3 minutos. Responda com, 1, a caminho, 2, indisponível. Forma Simples",
            "Language": "pt-PT",
            "TTSVoice": "pt-PT-RaquelNeural",
            "AudioFile": "",
            "CallerId": "351300505120"
        }

        for i in range(0, len(CONTACTS), 5):
            group = CONTACTS[i:i+5]
            logger.info(f"Processando grupo de chamadas {i//5 + 1}")
            
            for contact in group:
                voice_data["Destinations[]"] = contact
                voice_response = requests.post(
                    "https://api.smsbuzz.net/call/send",
                    data=voice_data,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
                logger.info(f"Chamada para {contact}: {voice_response.status_code}")
            
            if i + 5 < len(CONTACTS):
                time.sleep(2)

        logger.info("Processo de alertas concluído com sucesso")
        return True, "Alertas enviados com sucesso"
        
    except Exception as e:
        logger.error(f"Erro no processo: {str(e)}")
        return False, str(e)

@app.route('/trigger', methods=['GET'])
def trigger():
    success, message = send_alert()
    return jsonify({
        "success": success,
        "message": message,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/', methods=['GET'])
def home():
    return "Sistema de Alerta DAE - Ativo"

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=3000)
