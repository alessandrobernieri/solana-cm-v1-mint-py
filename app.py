import asyncio
import json
from solana.publickey import PublicKey
from solana.keypair import Keypair
from anchorpy import  Program, Provider
from datetime import datetime
import solana.system_program as sp
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solana.keypair import Keypair
from anchorpy.program import context
from anchorpy.program.namespace import account as nsaccount
from anchorpy.program.namespace.instruction import InstructionFn
from metaplex import metadata
from solana.rpc.types import TxOpts 
import base58
from spl.token._layouts import MINT_LAYOUT
from spl.token.instructions import MintToParams, get_associated_token_address, initialize_mint, InitializeMintParams, mint_to
from metaplex.metadata import TOKEN_PROGRAM_ID, create_associated_token_account_instruction 
import traceback
import time
import configparser
import concurrent.futures
import requests
from solana.rpc.async_api import AsyncClient
import os

def current_milli_time():
    return round(time.time() * 1000)

def mint_from_candy(config, candyMachineId, payer, treasury, payer_addr, tokenmetaprog, tokenprog, sysprog, rent, clock, api_end, program, date_utc):
    mint = Keypair()
    mint_add = mint.public_key
    metadata_acc = metadata.get_metadata_account(mint_add)
    masteredition = metadata.get_edition(mint_add)
    mint_nft = program.instruction['mintNft']

    accounts = {'config': config, 'candyMachine': candyMachineId,
    'payer': payer.public_key, 'wallet': treasury, 'metadata': metadata_acc, 'mint': mint_add,
    'mintAuthority': payer.public_key, 'updateAuthority': payer_addr, 
    'masterEdition': masteredition, 'tokenMetadataProgram': tokenmetaprog,
    'tokenProgram': tokenprog, 'systemProgram': sysprog, 'rent': rent,
    'clock': clock}
    # Create the instructions
    client = Client(api_end, blockhash_cache=True)

    min_rent_reseponse = client.get_minimum_balance_for_rent_exemption(MINT_LAYOUT.sizeof())
    lamports = min_rent_reseponse["result"]

    # Create account instruction
    create_acc = sp.create_account(
        sp.CreateAccountParams(
            from_pubkey=payer.public_key,
            new_account_pubkey=mint.public_key,
            lamports=lamports,
            space=MINT_LAYOUT.sizeof(),
            program_id=TOKEN_PROGRAM_ID))

    # Initialize mint instruction
    init_mint = initialize_mint(
        InitializeMintParams(
            decimals=0,
            program_id=TOKEN_PROGRAM_ID,
            mint=mint.public_key,
            mint_authority=payer.public_key,
            freeze_authority=payer.public_key))
    # Create associated token account instruction
    associated_token_account = get_associated_token_address(payer.public_key, mint.public_key)
    ass_token_acc = create_associated_token_account_instruction(
        associated_token_account=associated_token_account,
        payer=payer.public_key,
        wallet_address=payer.public_key,
        token_mint_address=mint_add)
    # Create mint instruction
    mint_tx = mint_to(
        MintToParams(
            program_id=TOKEN_PROGRAM_ID,
            mint=mint_add,
            dest = associated_token_account,
            mint_authority=payer.public_key,
            amount=1,
            signers=[payer.public_key]))

    contx = context.Context(accounts, [], [payer.public_key], [
        create_acc, init_mint, ass_token_acc, mint_tx], TxOpts(skip_preflight=True))

    tx = mint_nft(ctx=contx)
    final_tx = Transaction()
    final_tx.add(create_acc)
    final_tx.add(init_mint)
    final_tx.add(ass_token_acc)
    final_tx.add(mint_tx)
    final_tx.add(tx)
    signers = []
    signers.append(payer)
    signers.append(mint)

    current_utc = datetime.utcnow()
    if(date_utc>current_utc):
        date_diff2 = date_utc - current_utc
        date_diff=date_diff2.seconds+((date_diff2.microseconds)/1000000)

        print('Waiting '+str(date_diff-0.5)+' seconds..')
        time.sleep(date_diff-0.5)

    try:
        pre_time = current_milli_time()
        recent_bh = client.get_recent_blockhash()
        r = recent_bh.get('result')
        e = r.get('value')
        bh = e.get('blockhash')
        final_tx.recent_blockhash=bh
        final_tx.sign(payer, mint)
    except Exception:
        print(traceback.format_exc())

    mint_tx=client.send_transaction(final_tx, payer, mint, opts = TxOpts(skip_preflight=True))
    post_time = current_milli_time()

    return ('Tx sent in: '+str(post_time-pre_time)+'ms, '+mint_tx["result"])

async def main():
    APIEndpoint = config['Settings']['APIEndpoint']
    MintAmount = int(config['Settings']['MintAmount'])
    CandyMachineAddress = config['Addresses']['CandyMachineAddress']
    MainWallet = config['Wallets']['MainWallet']

    secret_key = MainWallet
    payer = Keypair.from_secret_key(base58.b58decode(secret_key))
    payer_addr = payer.public_key
    
    provider = Provider(AsyncClient(APIEndpoint), payer)
    program_id = PublicKey("cndyAnrLdpjq1Ssp1z8xxDsB8dxe7u4HL5Nxi2K5WXZ")
    prog2 = PublicKey("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
    
    candyMachineId = PublicKey(CandyMachineAddress)
    
    idl = await Program.fetch_idl(program_id, provider)

    program = Program(idl, program_id, provider)
    
    print('Wallet connected: '+str(payer.public_key))
    print('Pay attention to mint price before you press y!')
    
    tokenmetaprog = 'metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s'
    tokenprog = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
    sysprog = '11111111111111111111111111111111'
    rent = 'SysvarRent111111111111111111111111111111111'
    clock = 'SysvarC1ock11111111111111111111111111111111'

    command = 'r'
    while(command == 'r'):
        data = await program.account['CandyMachine'].fetch(candyMachineId)
        config = data.get('config')
        treasury = data.get('wallet')
        # Get candy infos
        data_info = data.get('data')
        price = data_info.get('price')
        datez = data_info.get('goLiveDate')
        if datez is None:
            date_utc='No date yet'
        else:
            date_utc = datetime.utcfromtimestamp(datez)
        items = data_info.get('itemsAvailable')
        items_redeemed = data.get('itemsRedeemed')
        items_minted = items - items_redeemed
        print('Candy Fetched!')
        if price is None:
            print('Price: none, Date UTC: '+str(date_utc))
        else:
            print('Price: '+str(price*0.000000001)+', Date UTC: '+str(date_utc))
        print(str(items_minted)+'/'+str(items)+' available.')

        command = input('Write "y" to mint '+str(MintAmount)+' NFT, "r" to reload: ')
    else:
        if(command == 'y'):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for _ in range(MintAmount):
                    futures.append(executor.submit(mint_from_candy, config, candyMachineId, payer, treasury, payer_addr, tokenmetaprog, tokenprog, sysprog, rent, clock, APIEndpoint, program, date_utc))
                for future in concurrent.futures.as_completed(futures):
                    print(future.result())

    commandz = input('Done.')

    await program.close()

asyncio.run(main())


