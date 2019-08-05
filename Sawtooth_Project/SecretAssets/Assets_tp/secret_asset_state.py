import hashlib
import ast
ASSET_NAMESPACE = hashlib.sha512('secret_asset'.encode()).hexdigest()[0:6]



class SecretAsset:
    def __init__(self,jfile):
        self.Hc = jfile["Hc"]
        self.encMessage = jfile["encMessage"]
        self.encryptedShares = jfile["encryptedShares"]
        self.policy = jfile["policy"]
        self.polyCommitments = jfile["polyCommitments"]

class SecretAssetState:
    
    TIMEOUT = 3

    def __init__(self, context):

        self._context = context
        self._address_cache = {}
    
    def get_asset(self,action,pubkey,tx):

        return self._load_assets(action,pubkey).get(tx)

    def set_asset(self,action,pubkey,tx,asset):

        assets = self._load_assets(action,pubkey)

        assets[tx] = asset
        print("Half assignment Asset")
        self._store_assets(action,pubkey, assets=assets)

    def delete_asset(self,serie_asset):
        assets = self._load_assets(serie_asset=serie_asset)

        del assets[serie_asset]
        if assets:
            self._store_asset(serie_asset, assets=assets)
        else:
            self._delete_asset(serie_asset)

    def _serialize(self, transactions):
        print("In serialize")
        transaction_strs = []
        for tx, s in transactions.items():
            transaction_str = ";".join(
            [tx, s.Hc ,s.encMessage,("$").join(s.encryptedShares),s.policy , str(s.polyCommitments)])
            transaction_strs.append(transaction_str)
        print("After return")
        return "|".join(sorted(transaction_strs)).encode()

    def _deserialize(self,data):
        transactions = {}
        try:
            for transaction in data.decode().split("|"):
                txn, Hc, encMessage, encryptedShares, policy, polyCommitments = transaction.split(";")
                encryptedShares = encryptedShares.split('$')
                polyCommitments = ast.literal_eval(polyCommitments)
                jfile = {
                    "Hc":Hc,
                    "encMessage":encMessage,
                    "encryptedShares":encryptedShares,
                    "policy":policy,
                    "polyCommitments":polyCommitments
                }
                transactions[txn] = SecretAsset(jfile = jfile)
        except ValueError:
            raise InternalError("Echec de decodage,veuillez choisir le bon format")
        print("keys of assets "+ str(transactions.keys()))
        return transactions

    def _store_assets(self, action,pubkey, assets):

        address = self._make_asset_address(action,pubkey)

        state_data = self._serialize(assets)

        self._address_cache[address] = state_data

        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _delete_asset(self, action, pubkey):
        address = self._make_asset_address(action, pubkey)

        self._context.delete_state(
            [address],
            timeout=self.TIMEOUT)

        self._address_cache[address] = None

    def _load_assets(self, action, pubkey):
        address = self._make_asset_address(action,pubkey)
        print(str(self._address_cache))
        if address in self._address_cache:
            print("Address in address cache")
            if self._address_cache[address]:
                serialized_assets = self._address_cache[address]
                assets = self._deserialize(serialized_assets)
            else:
                assets = {}
        else:
            print("address not in address cache")
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT)
            if state_entries:

                self._address_cache[address] = state_entries[0].data

                assets = self._deserialize(data=state_entries[0].data)

            else:
                self._address_cache[address] = None
                assets = {}
        print("Returning Asset")
        return assets

    def _make_asset_address(self,action,pubkey):
        return ASSET_NAMESPACE + hashlib.sha512(action.encode()).hexdigest()[:4] + hashlib.sha512(pubkey.encode()).hexdigest()[:60]
