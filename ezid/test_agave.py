from django.conf import settings
from agavepy.agave import Agave, AgaveException
import json, logging
import ezid
import urllib2

logger = logging.getLogger(__name__)

def _client(client_key, client_secret, token, refresh_token):
	try:		
		agave = Agave(
	        token=token, refresh_token=refresh_token, api_key=client_key,
	        api_secret=client_secret, api_server='https://agave.iplantc.org',
	        client_name='Default', verify=False
	    )
		
	except AgaveException as e:
		print '{{"error": "{0}" }}'.format(json.dumps(e.message))

	return agave

if __name__ == "__main__":
	client_key = 'ZszUvACfATGTWzmNeXiKMHFJec0a'
	client_secret = 'gPmHDpUySQndO8AfC7rg7XiFvVYa'	
	token = 'c5795ecdbfe0ed374b83ec7cc78df59e'
	refresh_token = 'ea13f5718b82ab45b6e82659704273b'

	agave = _client(client_key, client_secret, token, refresh_token)
	query = {'name': 'idsvc.project'}
	l = agave.meta.listMetadata(q = json.dumps(query))
	print json.dumps(l, indent = 2)

