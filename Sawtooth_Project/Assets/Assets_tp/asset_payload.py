from sawtooth_sdk.processor.exceptions import InvalidTransaction


class AssetPayload:

	def __init__(self, payload):

		try: 
		#Make the format of the payload , csv utf-8 encoded
			#name, serie, action, new_owner = payload.decode().split(',')
			print(payload.decode())
		except ValueError:
			raise InvalidTransaction("[-] Encodage de payload incorrect !")
		 
		if not serie:
		  	raise InvalidTransaction("[-] Nom de bien requis ")

		if not action:
		  	raise InvalidTransaction("[-] Action requise")

		if action not in ('create', 'transfer','destroy'):
		  	raise InvalidTransaction("[-] L'action choisie est invalide")

		if action == "transfer":
		        if new_owner is None:
                            raise InvalidTransaction("[-] Renseignez un destinataire pour recevoir le bien")


		self._name         = name
		self._serie        = serie
		self._action       = action
		self._new_owner    = new_owner


	@staticmethod
	def from_bytes(payload):
		return AssetPayload(payload = payload)

	@property
	def name(self):
		return self._name
    
	@property
	def serie(self):
		return self._serie
	
	@property
	def action(self):
		return self._action

	@property
	def new_owner(self):
		return self._new_owner    

	
