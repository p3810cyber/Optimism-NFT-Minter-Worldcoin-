#
from web3 import Web3
import json
from loguru import logger

ABI = json.load(open('abi.json'))

def mint_nfts(private_keys_path: str) -> None:
    web3 = Web3(Web3.HTTPProvider(f'https://rpc.ankr.com/optimism'))
    contract_address = Web3.to_checksum_address('0x6a886c76693ed6f4319a289e3fe2e670b803a2da')
    contract = web3.eth.contract(address=contract_address, abi=ABI)

    with open(private_keys_path, 'r', encoding='utf-8-sig') as file:
        private_keys = [row.strip() for row in file]

    for private_key in private_keys:
        address = Web3.to_checksum_address(web3.eth.account.from_key(private_key).address)
        tx = contract.functions.mint(address, 1).build_transaction(
            {
                'from': address,
                'gas': 130000,
                'gasPrice': web3.to_wei('0.001', 'gwei'),
                'nonce': web3.eth.get_transaction_count(address),
                'chainId': web3.eth.chain_id,
                'value': 0,
            })
        logger.info('Send Transaction')
        signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)

        web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = web3.to_hex(web3.keccak(signed_tx.rawTransaction))
        logger.info(f'Transaction hash: {tx_hash}')

        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt['status'] == 1:
            logger.info(f"OK. Block number: {tx_receipt['blockNumber']}")
        else:
            logger.info('Transaction failed.')

if __name__ == '__main__':
    mint_nfts(private_keys_path='private_keys.txt')
