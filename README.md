# Grin-Wallet owner_api RPC proxy in python

## Install

`git clone https://github.com/realPaulAtreides/basilisk.git`
`cd basilisk`
`python setup.py install`


## Usage

```
from basilisk.wallet.rpc import WalletOwnerV3Proxy

# Instatiate a wallet connection with the api endpoint and path to the api secret file
wallet = WalletOwnerV3Proxy('http://127.0.0.1:3420/v3/owner', '/home/user/.grin/user/owner_api_secret')

# Open wallet with a password stored in a text file, must have extention .secret
wallet.open_wallet(None, "./password.secret")

# Or open wallet with a password passed as a string
wallet.open_wallet(None, "password1")

wallet.accounts()

## Method args can be a dict
print(wallet.retrieve_summary_info({'minimum_confirmations': 1, 'refresh_from_node': True}))

## Args can also be a positional arguments
print(wallet.retrieve_summary_info(minimum_confirmations=1, refresh_from_node=True))

## Args can be a mix of both, but positional args must come last
print(wallet.retrieve_summary_info({'minimum_confirmations': 1}, refresh_from_node=True))

```

## Future Dev
Efforts will be made to include further grin utilities in this library
