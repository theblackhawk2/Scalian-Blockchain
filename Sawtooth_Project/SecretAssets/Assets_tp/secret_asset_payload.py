import json
from sawtooth_sdk.processor.exceptions import InvalidTransaction


class SecretAssetPayload:

	def __init__(self, payload):

		try: 
		#Make the format of the payload , csv utf-8 encoded
			action , params = payload.decode().split(';')[5],payload.decode().split(';')[6]
			print("This is the action params"+ params)

		except ValueError:
			raise InvalidTransaction("[-] Encodage de payload incorrect !")

		if action == "write":
			Requiredkeys = ["Hc","encMessage","encryptedShares","policy","polyCommitments"]
			for key in Requiredkeys: 
				if key not in json.loads(params):
					raise InvalidTransaction("[-] Champ manquant : " + key)
			self._action = action
			self._params = json.loads(params) 
			
		elif action == "read":
			self._params = params
		elif action == "share":
			pass
		else : 
			raise InvalidTransaction("[-] Type de transaction non reconnu")

			
		self._action = action
		


	@staticmethod
	def from_bytes(payload):
		return SecretAssetPayload(payload = payload)

	@property
	def action(self):
		return self._action
	
	@property
	def params(self):
		return self._params

	
      

	
