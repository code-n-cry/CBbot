from blockcypher import *
import json
import os
import requests
from cryptos import *
from pywallet import wallet
from exceptions import InvalidAddress


class CryptoOperating:
    def __init__(self):
        with open('static/json/general_bot_info.json',
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

    def generate_bitcoin_wallet(self):
        seed = wallet.generate_mnemonic()
        btc_wallet = wallet.create_wallet('BTC', seed, 0)
        return btc_wallet['address'], btc_wallet['private_key']

    def generate_litecoin_wallet(self):
        seed = wallet.generate_mnemonic()
        ltc_wallet = wallet.create_wallet('LTC', seed, 0)
        return ltc_wallet['address'], ltc_wallet['private_key']

    def generate_dogecoin_wallet(self):
        seed = wallet.generate_mnemonic()
        doge_wallet = wallet.create_wallet('DOGE', seed, 0)
        return doge_wallet['address'], doge_wallet['private_key']

    def generate_eth_wallet(self):
        pass

    def check_crypto_wallet(self, crypto_abbreviation: str, crypto_wallet: str):
        abbreviations_to_full = {
            'DOGE': f'https://dogechain.info/api/v1/address/balance/{crypto_wallet}',
            'BTC': f'https://blockchain.info/rawaddr/{crypto_wallet}',
            'LTC': f'https://api.blockcypher.com/v1/ltc/main/addrs/{crypto_wallet}/balance',
            'ETH': f'https://api.blockcypher.com/v1/eth/main/addrs/{crypto_wallet}/balance'
        }
        response = requests.get(abbreviations_to_full[crypto_abbreviation]).json()
        if 'error' in list(response.keys()):
            raise InvalidAddress
        return True

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
