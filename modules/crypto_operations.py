from blockcypher import *
import json
import requests
from cryptos import *
from pywallet import wallet
from exceptions import InvalidAddress


class CryptoOperating:
    def __init__(self):
        with open('static/json/general_bot_info.json', encoding='utf-8') as json_data:
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
        self.abbreviations_to_link = {
            'DOGE': 'https://dogechain.info/api/v1/address/balance/',
            'BTC': 'https://blockchain.info/rawaddr/',
            'LTC': 'https://api.blockcypher.com/v1/ltc/main/addrs/',
            'ETH': 'https://api.blockcypher.com/v1/eth/main/addrs/'
        }
        self.abbreviation_to_tx_function = {
            'DOGE': self.send_doges,
            'BTC': self.send_bitcoins,
            'LTC': self.send_ltc
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
        seed = wallet.generate_mnemonic()
        eth_wallet = wallet.create_wallet('ETH', seed, 0)
        return eth_wallet['address'], eth_wallet['private_key']

    def check_crypto_wallet(self, crypto_abbreviation: str, crypto_wallet: str):
        url = self.abbreviations_to_link[crypto_abbreviation] + f'{crypto_wallet}/balance'
        if crypto_abbreviation in ['DOGE', 'BTC']:
            url = self.abbreviations_to_link[crypto_abbreviation] + f'{crypto_wallet}'
        response = requests.get(url).json()
        if 'error' in list(response.keys()):
            raise InvalidAddress
        if crypto_abbreviation in ['BTC', 'LTC']:
            return response['final_balance'] / 100000000
        if crypto_abbreviation == 'DOGE':
            return response['balance']
        else:
            return response['balance'] / 1000000000000000000

    def send_bitcoins(self, private_key: str, to_public_address: str, amount: float,
                      is_key_compressed=False):
        amount_to_satoshi = int(amount * 100000000)
        tx = simple_spend(private_key, to_public_address, amount_to_satoshi, coin_symbol='btc',
                          api_key=self.token, privkey_is_compressed=False)
        return tx

    def send_ltc(self, private_key: str, to_public_address: str, amount: float,
                 is_key_compressed=False):
        amount_to_satoshi = int(amount * 100000000)
        tx = simple_spend(private_key, to_public_address, amount_to_satoshi, coin_symbol='ltc',
                          api_key=self.token, privkey_is_compressed=False)
        return tx

    def send_doges(self, private_key: str, to_public_address: str, amount: float,
                   is_key_compressed=False):
        amount_to_satoshi = int(amount * 100000000)
        tx = simple_spend(private_key, to_public_address, amount_to_satoshi, coin_symbol='doge',
                          api_key=self.token,
                          privkey_is_compressed=False)  # tx-сокращение от transaction
        return tx

    def get_balance(self, crypto_abbreviation: str):
        all_data = get_address_full(self.addresses[crypto_abbreviation],
                                    coin_symbol=crypto_abbreviation.lower())
        balance = all_data['balance']
        return balance / 100000000

    def send_transaction(self, crypto_abbreviation: str, address_send_to: str, amount: float,
                         private_key=False):
        if not private_key:
            self.abbreviation_to_tx_function[crypto_abbreviation](
                self.private_keys[crypto_abbreviation], address_send_to, amount)
        else:
            self.abbreviation_to_tx_function[crypto_abbreviation](private_key, address_send_to,
                                                                  amount, is_key_compressed=True)
