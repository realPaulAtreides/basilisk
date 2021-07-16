from basilisk.wallet.rpc import WalletOwnerV3Proxy

def main():
    wallet = WalletOwnerV3Proxy('http://127.0.0.1:3420/v3/owner', '/home/user/.grin/user/.owner_api_secret')
    print(wallet.shared_key.hex())
    print(wallet.open_wallet(None, "./password.secret"))
    print(wallet.retrieve_summary_info({'minimum_confirmations': 1}, refresh_from_node=True))
    print(wallet.retrieve_summary_info(refresh_from_node=True, minimum_confirmations=1))
    print(wallet.accounts())

main()
