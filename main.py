from web3 import Web3
import rsa
import re




def numbers(x):
    return (re.findall(r'-[0-9.]+|[0-9.]+', x))


def RSAsettings():
    global address
    global privatekey
    print("n - new keys (send transaction)")
    print("l - load keys (from blockchain)")
    while True:
        num = input('Your choice: ')
        if num == "n":
            a = gen_keys()
            print("RSA settings: ")
            address = input("address: ")
            privatekey = input("private key (blockchain): ")
            setRSApub(address, a[0], privatekey)
            print(a[0])
            print(a[1])
            print("Remember the private key to access your inbox")
            privkey = a[1]
            break
        elif num == "l":
            buf = numbers(input("RSA private key(not blockchain private key): "))
            address = input("Your blockchain address: ")
            privatekey = input("Private key(blockchain): ")
            privkey = rsa.PrivateKey(int(buf[0]), int(buf[1]), int(buf[2]), int(buf[3]), int(buf[4]))
            #print(privkey)
            break
        else:
            print('What is it?')
    return privkey




def gen_keys():
    (pubkey, privkey) = rsa.newkeys(1024)
    #print(pubkey)
    #print(privkey)
    return [pubkey,privkey]


def encrypt(data, pubkey):
    crypto = data.encode('utf8')
    crypto = rsa.encrypt(crypto, pubkey)  # Зашифровка
    #crypto = crypto.decode('utf8')
    return crypto

def decrypt(data, pk):
    #decrypto = ''
    try:
        decrypto = rsa.decrypt(data, pk).decode("utf8")  # Расшифровка
    except :
        decrypto = "ERROR"
    return decrypto






testnet = "https://matic-mumbai.chainstacklabs.com"
web3 = Web3(Web3.HTTPProvider(testnet))
print("// SPDX-License-Identifier: MIT")
print("by Daniil Smirnov")
print("I don't collect any of your data")

print(f"Gateway: {testnet}")
print(f"Is connected: {web3.is_connected()}")  # Is connected: True





# интерфейс
ERC20_ABI = ('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"RSApub","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"clearIncomings","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"mails","outputs":[{"internalType":"string","name":"data","type":"string"},{"internalType":"address","name":"from","type":"address"},{"internalType":"uint256","name":"unix","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"string","name":"data","type":"string"}],"name":"sendMessage","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"key","type":"string"}],"name":"setRSApub","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"pure","type":"function"}]')


mail_address = '0x7A0D26Ac86D9D036b2BBE410d913ECDb9bcd4908'


mail = web3.eth.contract(mail_address, abi=ERC20_ABI)









def getInbox(address):
    return mail.functions.balanceOf(address).call()

def getPub(address):
    a = numbers(mail.functions.RSApub(address).call())
    #print(pubkey)
    pubkey = rsa.PublicKey(int(a[0]), int(a[1]))
    return pubkey


def setRSApub(address, key, private_key):
    dict_transaction = {
        'chainId': web3.eth.chain_id,
        'from': address,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(address),
    }

    # создаём транзакцию
    transaction = mail.functions.setRSApub(str(key)).build_transaction(dict_transaction)

    # подписываем
    signed_txn = web3.eth.account.sign_transaction(transaction, str(private_key))

    # Отправляем, смотрим тут https://testnet.polygonscan.com/
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Адрес вашей транзакции:",txn_hash.hex())


def b2s(s):
    """Convert a string to raw bytes without encoding"""
    return str(s)[2:-1]

def s2b(s):
    return s.encode('latin1').decode('unicode_escape').encode('latin1')



def sendMessage(address, someone_address,data, private_key):
    dict_transaction = {
      'chainId': web3.eth.chain_id,
      'from': address,
      'gasPrice': web3.eth.gas_price,
      'nonce': web3.eth.get_transaction_count(address),
    }

    encrypteddata = b2s(encrypt(data, getPub(str(someone_address))))

    # создаём транзакцию
    transaction = mail.functions.sendMessage(str(someone_address),str(encrypteddata)).build_transaction(dict_transaction)


    # подписываем
    signed_txn = web3.eth.account.sign_transaction(transaction, str(private_key))

    # Отправляем, смотрим тут https://testnet.polygonscan.com/
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("txnHash",txn_hash.hex())

def clearInbox(address, private_key):
    dict_transaction = {
        'chainId': web3.eth.chain_id,
        'from': address,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(address),
    }

    # создаём транзакцию
    transaction = mail.functions.clearIncomings().build_transaction(dict_transaction)

    # подписываем
    signed_txn = web3.eth.account.sign_transaction(transaction, str(private_key))

    # Отправляем, смотрим тут https://testnet.polygonscan.com/
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("txnHash",txn_hash.hex())


def _getMail(address, number):
    data = mail.functions.mails(str(address), int(number)).call()
    return (data)


def getMail(address, number):
    c = ["", "", ""]
    try:
        c[0] = _getMail(str(address), int(number))[0]
        c[0] = s2b(c[0])
        c[0] = b2s(rsa.decrypt(c[0], RSAprivatekey))

    except:
        c[0] = "ERROR"
    try:
        c[1] = _getMail(str(address), int(number))[1]
    except:
        c[1] = "ERROR"
    try:
        c[2] = _getMail(str(address), int(number))[2]
    except:
        c[2] = "ERROR"
    return c


def get_all_mails(address):
    for i in range(getInbox(str(address))):
        print(f'message №{i}')                                                #  № сообщения - его id
        m = getMail(str(address), i)
        #am = m[0]
        maili = m[0]
        addri = m[1]
        unix = m[2]
        print('data:',maili)
        print('from:', addri)
        print('timestamp:', unix)
        print()




def main():
    while True:
        print("GM - get message by recipient's address and number")
        print("GI - get number of incoming messages by recipient address")
        print("GAM - get all messages at destination address")
        print("SM - send message (from, to, data, private key)")
        print("CI - clear incoming (address, private key)")
        print("GMR - receive message by recipient's address and number (without decoding)")
        print("EX - exit")
        metod = input()
        if metod == 'GM':
            #address = str(input("address: "))
            number = int(input("number: "))
            print(getMail(address, number))
        elif metod == 'GI':
            #address = str(input("address: "))
            print(getInbox(address))
        elif metod == 'GMR':
            #address = str(input("address: "))
            number = int(input("number: "))
            abbb = _getMail(address, number)
            print(s2b(abbb[0]), abbb[1])
        elif metod == 'GAM':
            #address = str(input("address: "))
            print(get_all_mails(address))
        elif metod == 'SM':
            #userAddress = str(input("from: "))
            toAddress = str(input("to: "))
            data = str(input("data: "))
            #privateKey = str(input("private key: "))
            sendMessage(address, toAddress, data, privatekey)
        elif metod == 'CI':
            #address = str(input("address: "))
            #privateKey = str(input("private key: "))
            clearInbox(address, privatekey)
        elif metod == 'EX':
            break
        else:
            print("What is it?")

if __name__ == '__main__':
    RSAprivatekey = RSAsettings()


    #print(privatekey)
    main()