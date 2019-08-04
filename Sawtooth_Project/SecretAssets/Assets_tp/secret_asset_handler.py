import hashlib
import json
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.handler import TransactionHandler
from secret_asset_payload import *
from secret_asset_state   import *



class SecretAssetTransactionHandler(TransactionHandler):

	def __init__(self, namespace_prefix):
		self._namespace_prefix = namespace_prefix
	
	@property
	def family_name(self):
		return 'secret_asset'

	@property
	def family_versions(self):
		return ['1.0']

	@property
	def namespaces(self):
		return [self._namespace_prefix]

	def apply(self,transaction,context):
		header = transaction.header
		signer = header.signer_public_key
		#Tester si li signataire est celui qui a envoyé la transaction
		
		asset_payload = SecretAssetPayload.from_bytes(transaction.payload)
		asset_state   = SecretAssetState(context)

		if asset_payload.action == "write":
			print(json.loads(asset_payload.params['policy'])['members'])
			for member in json.loads(asset_payload.params['policy'])['members']:
				# Inputs : action, pubkey, Hash of Transaction
				if asset_state.get_asset("write",member[0],hashlib.sha512(json.dumps(asset_payload.params,sort_keys=True).encode()).hexdigest()) is not None:
					raise InvalidTransaction("Transaction Invalide : Secret deja existant")
				secretAsset = SecretAsset(jfile = asset_payload.params)
				asset_state.set_asset(asset_payload.action,member[0],hashlib.sha512(json.dumps(asset_payload.params,sort_keys=True).encode()).hexdigest(),secretAsset)
				
			
		elif asset_payload.action == "read":
			pass
			"""
			asset = asset_state.get_asset(asset_payload.serie)
		    
			if asset is None:
				raise InvalidTransaction("Transfer impossible : Le bien en question n'existe pas")
			else:
					
				if asset.owner != signer:
					raise InvalidTransaction("Transfer impossible : vous ne pouvez transferer que vos propre biens")
				else: 
					asset.owner = asset_payload.new_owner
					assets[asset.serie] = asset
					self._store_asset(asset.serie, assets=assets)
					print("Bien {} transfere , {} => {}".format(asset.serie, signer,asset_payload.new_owner))            
		    """

		elif asset_payload.action == "destroy":
			pass
			"""
			asset = asset_state.get_asset(asset_payload.serie)
			if asset is None:
				raise InvalidTransaction("Action Invalide : Le bien en question n'existe pas")
			asset_state.delete_asset(asset_payload.serie)
			"""
		else:
			raise InvalidTransaction('Action non geree: {} veuillez selection une action parmis ces choix : <create>, <transfer>, <destroy>'.format(asset_payload.action))


