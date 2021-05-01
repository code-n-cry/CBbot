from blockcypher import *
import json
import requests
import cryptocompare
from cryptos import *
from pywallet import wallet
from constants.exceptions import InvalidAddress, BadTransaction


class CryptoOperating:
    """
    Класс для операций с криповалютой. Позволяет проверять баланс, отправлять транзакции и
    генерировать криптовалютные кошельки. Здесь используется HTTP-API разных сервисов.
    """

    def __init__(self):
        with open('static/json/general_bot_info.json', encoding='utf-8') as json_data:
            all_data = json.load(json_data)
            self.addresses = all_data['Wallets']
            self.private_keys = all_data['Secrets']
            self.token = all_data['Tokens']['BlockCypher']
        with open('static/json/crypto_fees.json', encoding='utf-8') as fees:
            self.fees = json.load(fees)
        self.doge_class = Doge()
        self.btc_class = Bitcoin()
        self.ltc_class = Litecoin()
        self.abbrev_to_their_full = {
            'BTC': self.btc_class,
            'LTC': self.ltc_class,
            'DOGE': self.doge_class
        }
        self.abbreviations_to_link = {
            'DOGE': 'https://chain.so/api/v2/get_address_balance/',
            'BTC': 'https://chain.so/api/v2/get_address_balance/',
            'LTC': 'https://chain.so/api/v2/get_address_balance/',
            'ETH': 'https://api.blockcypher.com/v1/eth/main/addrs/'
        }

    def generate_wallet(self, coin_symbol: str):
        seed = wallet.generate_mnemonic()
        crypto_wallet = wallet.create_wallet(coin_symbol, seed, 0)
        return crypto_wallet['address'], crypto_wallet['private_key']

    def check_crypto_wallet(self, crypto_abbreviation: str, crypto_wallet: str):
        if crypto_abbreviation in ['DOGE', 'BTC', 'LTC']:
            url_part2 = f'{crypto_abbreviation}/{crypto_wallet}'
            full_url = self.abbreviations_to_link[crypto_abbreviation] + url_part2
            response = requests.get(full_url).json()
            if response['status'] == 'success':
                return response['data']['confirmed_balance']
            raise InvalidAddress
        try:
            url = self.abbreviations_to_link[crypto_abbreviation] + crypto_wallet
            response = requests.get(url).json()
            return response['final_balance'] / 1000000000000000000
        except KeyError:
            raise InvalidAddress

    def send_coin(self, coin_symbol: str, private_key: str, to_public_address: str, amount: float):
        amount_to_satoshi = int(amount * 100000000)
        fee = self.fees[coin_symbol] * 100000000
        coin_class = self.abbrev_to_their_full[coin_symbol]
        signed_transaction = coin_class.preparesignedtx(private_key, to_public_address,
                                                        amount_to_satoshi, fee=fee)
        confirmed_tx = coin_class.pushtx(signed_transaction)
        return confirmed_tx

    def check_chain_transaction(self, crypto_abbreviation: str, tx_hash: str):
        url = f'https://chain.so/api/v2/get_confidence/{crypto_abbreviation}/{tx_hash}'
        response = requests.get(url).json()
        status = response['status']
        if status == 'fail':
            raise BadTransaction
        confirmations = response['data']['confirmations']
        if confirmations <= 1:
            return 1
        if confirmations == 2:
            return 2
        if confirmations >= 3:
            return 3
        return status

    def get_balance(self, crypto_abbreviation: str):
        """
        Конкретно эта функция проверяет баланс НАШИХ кошельков, реквизитов бота.
         За другие балансы отвечает функция check_crypto_wallet.
        """
        all_data = get_address_full(self.addresses[crypto_abbreviation],
                                    coin_symbol=crypto_abbreviation.lower())
        balance = all_data['balance']
        return balance / 100000000

    def send_transaction(self, crypto_abbreviation: str, address_send_to: str, amount: float,
                         private_key=False):
        if not private_key:
            return self.send_coin(crypto_abbreviation.lower(),
                                  self.private_keys[crypto_abbreviation], address_send_to, amount)
        return self.send_coin(crypto_abbreviation, private_key, address_send_to, amount)

    def get_price(self, crypto, fiat):
        price = cryptocompare.get_price(crypto, fiat)
        digit_price = price[crypto][fiat]
        return digit_price
