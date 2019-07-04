from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.handler import TransactionHandler
from asset_payload import *
from asset_state   import *


class AssetTransactionHandler(TransactionHandler):

	def __init__(self, namespace_prefix):
		self._namespace_prefix = namespace_prefix
	
	@property
	def family_name(self):
		return 'asset'

	@property
	def family_versions(self):
		return ['1.0']

	@property
	def namespaces(self):
		return [self._namespace_prefix]

	def apply(self,transaction,context):
		header = transaction.header
		signer = header.signer_public_key

		asset_payload = AssetPayload.from_bytes(transaction.payload)

		asset_state   = AssetState(context)

	#### Implement the logic of Exchanging assets from hand to hand ####

		if asset_payload.action == "create":
			if asset_state.get_asset(asset_payload.serie) is not None:
				raise InvalidTransaction(
					'Transaction invalide : Asset deja existant: {}'.format(
						asset_payload.serie))

			asset = Asset (name  = asset_payload.name,
						   serie = asset_payload.serie,
						   owner = signer)

			asset_state.set_asset(asset_payload.serie, asset)

			print("L'entreprise {} a cree un bien.".format(signer[:6]))


			
			
		elif asset_payload.action == "transfer" :

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
		
		elif asset_payload.action == "destroy":
			asset = asset_state.get_asset(asset_payload.serie)
			if asset is None:
				raise InvalidTransaction("Action Invalide : Le bien en question n'existe pas")
			asset_state.delete_asset(asset_payload.serie)

		else:
			raise InvalidTransaction('Action non geree: {} veuillez selection une action parmis ces choix : <create>, <transfer>, <destroy>'.format(asset_payload.action))

		
