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
        
        if response.status_code == 200:
            return response.json().get("AccessToken")
        return None
    except Exception as e:
        logger.error(f"Auth Error: {str(e)}")
        return None

@app.route('/trigger', methods=['GET', 'POST'])
def trigger_alert():
    try:
        logger.info("Recebido sinal da Shelly - Iniciando processo")
        
        # Autenticação
        token = authenticate_smsbuzz()
        if not token:
            logger.error("Falha na autenticação")
            return jsonify({"success": False, "message": "Falha na autenticação"}), 401

        # Envio do SMS
        sms_url = "https://api.smsbuzz.net/sms/send"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        sms_data = {
            "SenderName": "SMSBUZZ",
            "Destinations": "933825194",
            "Text": "SOS DAE, SOS DAE. Alerta Cabine DAE Pavilhão Casa do Povo, operacionais em menos de 3 minutos."
        }

        logger.info(f"Enviando SMS com dados: {sms_data}")
        sms_response = requests.post(sms_url, json=sms_data, headers=headers)
        logger.info(f"SMS Response Code: {sms_response.status_code}")
        logger.info(f"SMS Response Text: {sms_response.text}")
        
        if sms_response.status_code == 200:
            campaign_id = sms_response.json().get("CampaignId")
            logger.info(f"SMS enviado com sucesso - Campaign ID: {campaign_id}")
            return jsonify({
                "success": True, 
                "message": "Alerta enviado com sucesso",
                "campaign_id": campaign_id
            })
        
        logger.error(f"Erro ao enviar SMS: {sms_response.text}")
        return jsonify({
            "success": False,
            "message": f"Erro ao enviar SMS: {sms_response.text}"
        }), 500

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
