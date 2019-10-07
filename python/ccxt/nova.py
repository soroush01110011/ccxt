# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
import hashlib
from ccxt.base.errors import ExchangeError


class nova (Exchange):

    def describe(self):
        return self.deep_extend(super(nova, self).describe(), {
            'id': 'nova',
            'name': 'Novaexchange',
            'countries': ['TZ'],  # Tanzania
            'rateLimit': 2000,
            'version': 'v2',
            'has': {
                'CORS': False,
                'createMarketOrder': False,
                'createDepositAddress': True,
                'fetchDepositAddress': True,
                'fetchDeposits': True,
                'fetchWithdrawals': True,
            },
            'urls': {
                'referral': 'https://novaexchange.com/signup/?re=is8vz2hsl3qxewv1uawd',
                'logo': 'https://user-images.githubusercontent.com/1294454/30518571-78ca0bca-9b8a-11e7-8840-64b83a4a94b2.jpg',
                'api': 'https://novaexchange.com/remote',
                'www': 'https://novaexchange.com',
                'doc': 'https://novaexchange.com/remote/faq',
            },
            'api': {
                'public': {
                    'get': [
                        'markets/',
                        'markets/{basecurrency}/',
                        'market/info/{pair}/',
                        'market/orderhistory/{pair}/',
                        'market/openorders/{pair}/buy/',
                        'market/openorders/{pair}/sell/',
                        'market/openorders/{pair}/both/',
                        'market/openorders/{pair}/{ordertype}/',
                    ],
                },
                'private': {
                    'post': [
                        'getbalances/',
                        'getbalance/{currency}/',
                        'getdeposits/',
                        'getwithdrawals/',
                        'getnewdepositaddress/{currency}/',
                        'getdepositaddress/{currency}/',
                        'myopenorders/',
                        'myopenorders_market/{pair}/',
                        'cancelorder/{orderid}/',
                        'withdraw/{currency}/',
                        'trade/{pair}/',
                        'tradehistory/',
                        'getdeposithistory/',
                        'getwithdrawalhistory/',
                        'walletstatus/',
                        'walletstatus/{currency}/',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'tierBased': False,
                    'percentage': True,
                    'maker': 0.2 / 100,
                    'taker': 0.2 / 100,
                },
            },
            'commonCurrencies': {
                'FAIR': 'FairCoin',
            },
        })

    def fetch_markets(self, params={}):
        response = self.publicGetMarkets(params)
        markets = response['markets']
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            id = self.safe_string(market, 'marketname')
            quoteId, baseId = id.split('_')
            base = self.safe_currency_code(baseId)
            quote = self.safe_currency_code(quoteId)
            symbol = base + '/' + quote
            disabled = self.safe_value(market, 'disabled', False)
            active = not disabled
            result.append(self.extend(self.fees['trading'], {
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': active,
                'info': market,
            }))
        return result

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        request = {
            'pair': self.market_id(symbol),
        }
        response = self.publicGetMarketOpenordersPairBoth(self.extend(request, params))
        return self.parse_order_book(response, None, 'buyorders', 'sellorders', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        request = {
            'pair': self.market_id(symbol),
        }
        response = self.publicGetMarketInfoPair(self.extend(request, params))
        ticker = response['markets'][0]
        timestamp = self.milliseconds()
        last = self.safe_float(ticker, 'last_price')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high24h'),
            'low': self.safe_float(ticker, 'low24h'),
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': self.safe_float(ticker, 'change24h'),
            'average': None,
            'baseVolume': None,
            'quoteVolume': self.safe_float(ticker, 'volume24h'),
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        #
        # fetchMyTrades
        #
        #    {
        #        basecurrency: 'BTC',
        #        fee: '0.00000026',
        #        fromamount: '1079.13354707',
        #        fromcurrency: 'LINX',
        #        orig_orderid: 42906337,
        #        price: '0.00000012',
        #        toamount: '0.0.00012924',
        #        tocurrency: 'BTC',
        #        trade_time: '2019-07-28 13:36',
        #        tradeid: 21715234,
        #        tradetype: 'SELL',
        #        unix_t_trade_time: 1564313790,
        #    }
        #
        timestamp = self.safe_timestamp_2(trade, 'unix_t_datestamp', 'unix_t_trade_time')
        symbol = None
        if market is not None:
            symbol = market['symbol']
        type = None
        side = self.safe_string_lower(trade, 'tradetype')
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'amount')
        feeCost = self.safe_float(trade, 'fee')
        fee = None
        if feeCost is not None:
            feeCurrency = None if (market is None) else market['quote']
            fee = {
                'cost': feeCost,
                'currency': feeCurrency,
            }
        order = self.safe_integer(trade, 'orig_orderid')
        id = self.safe_integer(trade, 'tradeid')
        cost = None
        if price is not None and amount is not None:
            cost = amount * price
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': order,
            'type': type,
            'side': side,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': fee,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
        }
        response = self.publicGetMarketOrderhistoryPair(self.extend(request, params))
        return self.parse_trades(response['items'], market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        #
        # privatePostTradehistory response
        #
        #    {
        #        items: {
        #            {
        #                basecurrency: 'BTC',
        #                fee: '0.00000026',
        #                fromamount: '1079.13354707',
        #                fromcurrency: 'LINX',
        #                orig_orderid: 42906337,
        #                price: '0.00000012',
        #                toamount: '0.0.00012924',
        #                tocurrency: 'BTC',
        #                trade_time: '2019-07-28 13:36',
        #                tradeid: 21715234,
        #                tradetype: 'SELL',
        #                unix_t_trade_time: 1564313790,
        #            },
        #        },
        #        message: 'Your trade history with recent first',
        #        page: 1,
        #        pages: 1,
        #        perpage: 100,
        #        status: 'success',
        #        total_items: 1
        #    }
        self.load_markets()
        market = None
        if symbol is not None:
            market = self.market(symbol)
        response = self.privatePostTradehistory(params)
        return self.parse_trades(response['items'], market, since, limit)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetbalances(params)
        balances = self.safe_value(response, 'balances')
        result = {'info': response}
        for i in range(0, len(balances)):
            balance = balances[i]
            currencyId = self.safe_string(balance, 'currency')
            code = self.safe_currency_code(currencyId)
            lockbox = self.safe_float(balance, 'amount_lockbox')
            trades = self.safe_float(balance, 'amount_trades')
            account = {
                'free': self.safe_float(balance, 'amount'),
                'used': self.sum(lockbox, trades),
                'total': self.safe_float(balance, 'amount_total'),
            }
            result[code] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        self.load_markets()
        amount = str(amount)
        price = str(price)
        market = self.market(symbol)
        request = {
            'tradetype': side.upper(),
            'tradeamount': amount,
            'tradeprice': price,
            'tradebase': 1,
            'pair': market['id'],
        }
        response = self.privatePostTradePair(self.extend(request, params))
        tradeItems = self.safe_value(response, 'tradeitems', [])
        tradeItemsByType = self.index_by(tradeItems, 'type')
        created = self.safe_value(tradeItemsByType, 'created', {})
        orderId = self.safe_string(created, 'orderid')
        return {
            'info': response,
            'id': orderId,
        }

    def cancel_order(self, id, symbol=None, params={}):
        request = {
            'orderid': id,
        }
        return self.privatePostCancelorder(self.extend(request, params))

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        #
        # privatePostMyopenorders response
        #
        #    {
        #        items: {
        #            {
        #                fromamount: 1079.13354707,
        #                fromcurrency: 'LINX',
        #                market: 'BTC_LINX',
        #                orderdate: '2019-07-28 10:50',
        #                orderid: 43102690,
        #                ordertype: 'SELL',
        #                price: '0.00000015',
        #                toamount: '0.00016187',
        #                tocurrency: 'BTC',
        #                unix_t_orderdate: 1564303847
        #            },
        #        },
        #        message: 'Your open orders with recent first',
        #        page: 1,
        #        pages: 1,
        #        perpage: 100,
        #        status: 'success',
        #        total_items: 1
        #    }
        self.load_markets()
        market = None
        response = self.privatePostMyopenorders(params)
        orders = self.safe_value(response, 'items', [])
        return self.parse_orders(orders, market, since, limit, {
            'status': 'open',
        })

    def parse_order(self, order, market=None):
        #
        # fetchOpenOrders
        #
        #    {
        #        fromamount: 1079.13354707,
        #        fromcurrency: 'LINX',
        #        market: 'BTC_LINX',
        #        orderdate: '2019-07-28 10:50',
        #        orderid: 43102690,
        #        ordertype: 'SELL',
        #        price: '0.00000015',
        #        toamount: '0.00016187',
        #        tocurrency: 'BTC',
        #        unix_t_orderdate: 1564303847
        #    }
        #
        orderId = self.safe_string(order, 'orderid')
        symbol = None
        marketId = self.safe_string(order, 'market')
        if marketId is not None:
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
                symbol = market['symbol']
            else:
                baseId = self.safe_string(order, 'fromcurrency')
                quoteId = self.safe_string(order, 'tocurrency')
                base = self.safe_currency_code(baseId)
                quote = self.safe_currency_code(quoteId)
                symbol = base + '/' + quote
        status = self.safe_string(order, 'status')
        timestamp = self.safe_timestamp(order, 'unix_t_orderdate')
        amount = self.safe_float(order, 'fromamount')
        side = self.safe_string_lower(order, 'ordertype')
        return {
            'id': orderId,
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'type': None,
            'side': side,
            'price': None,
            'cost': None,
            'amount': amount,
            'remaining': None,
            'filled': None,
            'status': status,
            'fee': None,
            'trades': None,
            'info': order,
        }

    def create_deposit_address(self, code, params={}):
        self.load_markets()
        currency = self.currency(code)
        request = {
            'currency': currency['id'],
        }
        response = self.privatePostGetnewdepositaddressCurrency(self.extend(request, params))
        address = self.safe_string(response, 'address')
        self.check_address(address)
        tag = self.safe_string(response, 'tag')
        return {
            'currency': code,
            'address': address,
            'tag': tag,
            'info': response,
        }

    def fetch_deposit_address(self, code, params={}):
        self.load_markets()
        currency = self.currency(code)
        request = {
            'currency': currency['id'],
        }
        response = self.privatePostGetdepositaddressCurrency(self.extend(request, params))
        address = self.safe_string(response, 'address')
        self.check_address(address)
        tag = self.safe_string(response, 'tag')
        return {
            'currency': code,
            'address': address,
            'tag': tag,
            'info': response,
        }

    def parse_transaction(self, transaction, currency=None):
        timestamp = self.safe_timestamp_2(transaction, 'unix_t_time_seen', 'unix_t_daterequested')
        updated = self.safe_timestamp(transaction, 'unix_t_datesent')
        currencyId = self.safe_string(transaction, 'currency')
        code = self.safe_currency_code(currencyId)
        status = self.parse_transaction_status(self.safe_string(transaction, 'status'))
        amount = self.safe_float(transaction, 'tx_amount')
        addressTo = self.safe_string(transaction, 'tx_address')
        fee = None
        txid = self.safe_string(transaction, 'tx_txid')
        type = self.safe_string(transaction, 'type')
        return {
            'info': transaction,
            'id': None,
            'currency': code,
            'amount': amount,
            'addressFrom': None,
            'address': addressTo,
            'addressTo': addressTo,
            'tagFrom': None,
            'tag': None,
            'tagTo': None,
            'status': status,
            'type': type,
            'updated': updated,
            'txid': txid,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'fee': fee,
        }

    def parse_transaction_status(self, status):
        statuses = {
            'Accounted': 'ok',
            'Confirmed': 'ok',
            'Incoming': 'pending',
            'Approved': 'pending',
            'Sent': 'pending',
        }
        return self.safe_string(statuses, status, status)

    def fetch_deposits(self, code=None, since=None, limit=None, params={}):
        response = self.privatePostGetdeposithistory(params)
        for i in range(0, len(response['items'])):
            response['items'][i]['type'] = 'deposit'
        currency = None
        if code is not None:
            currency = self.currency(code)
        deposits = self.safe_value(response, 'items', [])
        return self.parse_transactions(deposits, currency, since, limit)

    def fetch_withdrawals(self, code=None, since=None, limit=None, params={}):
        response = self.privatePostGetwithdrawalhistory(params)
        for i in range(0, len(response['items'])):
            response['items'][i]['type'] = 'withdrawal'
        currency = None
        if code is not None:
            currency = self.currency(code)
        withdrawals = self.safe_value(response, 'items', [])
        return self.parse_transactions(withdrawals, currency, since, limit)

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/'
        if api == 'private':
            url += api + '/'
        url += self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = str(self.nonce())
            url += '?' + self.urlencode({'nonce': nonce})
            signature = self.hmac(self.encode(url), self.encode(self.secret), hashlib.sha512, 'base64')
            body = self.urlencode(self.extend({
                'apikey': self.apiKey,
                'signature': signature,
            }, query))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] != 'success':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response
