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
		

		print("The payload action is " + asset_payload.action)
		if asset_payload.action == "write":
			
			for member in json.loads(asset_payload.params['policy'])['members']:
				# Inputs : action, pubkey, Hash of Transaction
				if asset_state.get_asset("write",member[0],hashlib.sha512(json.dumps(asset_payload.params,sort_keys=True).encode()).hexdigest()) is not None:
					raise InvalidTransaction("Transaction Invalide : Secret deja existant")
				secretAsset = SecretAsset(jfile = asset_payload.params)
				txw = hashlib.sha512(json.dumps(asset_payload.params,sort_keys=True).encode()).hexdigest()
				print(" In Write : Member  :" + str(member))
				print(" In Write : Txw     :" + str(txw))
				asset_state.set_asset(asset_payload.action,member[0],txw,secretAsset)
				
			
		elif asset_payload.action == "read":
			# Params for this action should be replaced with a query service for existing transactions and replace them with txw
			txw = asset_payload.params
			# we will test with the first mock member, this one should be changed later with the sender
			member = ['101327191784287492373383809902168603188987799081777419466034047135455849629090','23776359816484729224351517659128510016876926467066255348726241832497012031432']
			print("Member : " + str(member))
			print(" Txw   : " + txw)
			print(json.dumps(asset_payload.params,sort_keys=True))
			if asset_state.get_asset("write",member[0], txw) is not None:
				
				#Testing id read was already granted (Creating method to insert transactions)
				#If not create method to insert read transactions 
			else:
				raise InvalidTransaction("Demande d'accès a un secret non existant")

		elif asset_payload.action = "share":

				"""
				Asset = asset_state.get_asset("write",member[0], txw)
				if member in Asset.policy:
					print("Secret deja existant et lecteur autorisée, enregistrement de la demande read")
				else: 
					print("Secret existant mais utilisateur non autorisé")
				"""
			else:
				raise InvalidTransaction("Transaction Invalide : secret Inexistant")

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


