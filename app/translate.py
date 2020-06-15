from app import app
import requests
import json
from flask_babel import _

def translate(text, source_language, dest_language):
	if not app.config['MS_TRANSLATOR_KEY']:
		return _('Error: Translation serice is not configured')
	auth = {'Ocp-Apim-Subscription-Key':app.config['MS_TRANSLATOR_KEY']}
	r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
                     '/Translate?text={}&from={}&to={}'.\
					 format(text, source_language, dest_language),\
					 headers=auth)
	if r.status_code != 200:
		return _('Error occured in translation service')
	return json.loads(r.content.decode('utf-8-sig'))	