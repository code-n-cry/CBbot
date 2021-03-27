from blockcypher import *
import json
import os
from cryptos import *


class CryptoOperating:
    def __init__(self):
        with open(os.getcwd() + '\\static\\json\\general_wallets.json',
                  encoding='utf-8') as json_data:
            all_data = json.load(json_data)
            self.addresses = all_data['Wallets']
            self.private_keys = all_data['Secrets']
            self.token = all_data['Tokens']['BlockCypher']
        self.doge_class = Doge()
        self.btc_class = Bitcoin()
        self.ltc_class = Litecoin()
        self.abbrev_to_their_full = {
            'BTC': self.btc_class,
            'LTC': self.ltc_class,
            'DOGE': self.doge_class
        }

    def send_doges(self, to_public_address: str, amount: int):
        amount *= 1
        private_key = self.private_keys['DOGE']
        tx = simple_spend(private_key, to_public_address, amount, coin_symbol='doge',
                          api_key=self.token,
                          privkey_is_compressed=False)  # tx-сокращение от transaction
        return tx

    def get_balance(self, crypto_abbreviation: str):
        all_data = get_address_full(self.addresses[crypto_abbreviation],
                                    coin_symbol=crypto_abbreviation.lower())
        balance = all_data['balance']
        return balance / 100000000

    def send_transaction(self, crypto_abbreviation: str, address_send_to: str, amount: int):
        self.send_doges(address_send_to, amount * 100000000)
