import hashlib
ASSET_NAMESPACE = hashlib.sha512('asset'.encode()).hexdigest()[0:6]

class Asset:
    def __init__(self, name, serie, owner):
        self.name    = name
        self.serie   = serie
        self.owner   = owner


class AssetState:
    
    TIMEOUT = 3

    def __init__(self, context):

        self._context = context
        self._address_cache = {}
    
    def get_asset(self,serie_asset):

        return self._load_assets(serie_asset=serie_asset).get(serie_asset)

    def set_asset(self,serie_asset,asset):

        assets = self._load_assets(serie_asset=serie_asset)

        assets[serie_asset] = asset

        self._store_asset(serie_asset, assets=assets)

    def delete_asset(self,serie_asset):
        assets = self._load_assets(serie_asset=serie_asset)

        del assets[serie_asset]
        if assets:
            self._store_asset(serie_asset, assets=assets)
        else:
            self._delete_asset(serie_asset)

    def _serialize(self, assets):
        asset_strs = []
        for asset_serie, a in assets.items():
            asset_str = ",".join(
                [asset_serie, a.name, a.owner])
            asset_strs.append(asset_str)

        return "|".join(sorted(asset_strs)).encode()

    def _deserialize(self,data):

        assets = {}
        try:
            for asset in data.decode().split("|"):
                asset_serie, name, owner = asset.split(",")

                assets[asset_serie] = Asset(name, asset_serie, owner)
        except ValueError:
            raise InternalError("Echec de decodage,veuillez choisir le bon format")

        return assets

    def _store_asset(self, serie_asset, assets):

        address = self._make_asset_address(serie_asset)

        state_data = self._serialize(assets)

        self._address_cache[address] = state_data

        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _delete_asset(self, serie_asset):
        address = self._make_asset_address(serie_asset)

        self._context.delete_state(
            [address],
            timeout=self.TIMEOUT)

        self._address_cache[address] = None

    def _load_assets(self, serie_asset):
        address = self._make_asset_address(serie_asset)

        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_assets = self._address_cache[address]
                assets = self._deserialize(serialized_assets)
            else:
                assets = {}
        else:
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT)
            if state_entries:

                self._address_cache[address] = state_entries[0].data

                assets = self._deserialize(data=state_entries[0].data)

            else:
                self._address_cache[address] = None
                assets = {}

        return assets

    def _make_asset_address(self,serie_asset):
        print("Le namespace choisi est ..."+ ASSET_NAMESPACE) 
        return ASSET_NAMESPACE + hashlib.sha512(serie_asset.encode()).hexdigest()[:64]
