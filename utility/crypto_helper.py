from collections import namedtuple

# https://ofek.dev/bit/
from bit import Key
from bit.format import public_key_to_address, public_key_to_segwit_address, bytes_to_wif
from bit.crypto import ripemd160_sha256
from bit.base32 import  encode

_BitBaseAddress = namedtuple('_BitBaseAddress', [
    'seed',
    'compressed_private_key_wif',
    'compressed_legacy_address',
    'segwit_p2sh_address',
    'segwit_address',
    'uncompressed_private_key_wif',
    'uncompressed_legacy_address',
    #'uncomprssed_segwit_address', думаю это не нужно
])

# так быстрее думаю будет поиск, всего 2 адреса
_BitBaseRipemd160 = namedtuple('_BitBaseRipemd160', [
    'seed',
    'compressed_ripemd160',
    'uncompressed_ripemd160',
])


class BitRecordRipemd160(_BitBaseRipemd160):
    '''
    Удобное представление полученных ключей и адресов из целочисленного зерна
    '''
    def __new__(cls, seed:int):
        super_obj = super(_BitBaseRipemd160, cls)
        # важно сохранять порядок элементов из _BitBaseRipemd160!
        values = [seed]

        compressed_private_key = Key.from_int(seed)  # Compressed by default

        compressed_byte_public_key = compressed_private_key._pk.public_key.format(compressed=True)
        compressed_ripemd160 = ripemd160_sha256(compressed_byte_public_key).hex()
        values.append(compressed_ripemd160)

        uncompressed_byte_public_key = compressed_private_key._pk.public_key.format(compressed=False)
        uncompressed_ripemd160 = ripemd160_sha256(uncompressed_byte_public_key).hex()
        values.append(uncompressed_ripemd160)

        return super_obj.__new__(cls, values)

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ', '.join("{}=%r".format(name) for name in self._fields) % self)

    def __str__(self):
        return "{}".format(
            ', '.join("{}=%r".format(name) for name in self._fields) % self)

class BitRecordAddress(_BitBaseAddress):
    '''
    Удобное представление полученных ключей и адресов из целочисленного зерна
    '''
    def __new__(cls, seed:int):
        super_obj = super(_BitBaseAddress, cls)
        # важно сохранять порядок элементов из _BitBase!
        values = [seed]

        compressed_private_key = Key.from_int(seed)  # Compressed by default

        compressed_private_key_wif = compressed_private_key.to_wif()  # compressed private key
        values.append(compressed_private_key_wif)

        compressed_legacy_address = compressed_private_key.address  # Legacy compressed address
        values.append(compressed_legacy_address)

        segwit_p2sh_address = compressed_private_key.segwit_address  # Segwit P2SH
        values.append(segwit_p2sh_address)

        public_key = compressed_private_key.public_key
        public_key = ripemd160_sha256(public_key)
        segwit_address = encode('bc', 0, public_key)
        values.append(segwit_address)

        # ucompressed
        uncompressed_private_key_wif = bytes_to_wif(compressed_private_key.to_bytes(), compressed=False)
        values.append(uncompressed_private_key_wif)

        uncompressed_private_key = Key(uncompressed_private_key_wif)
        uncompressed_legacy_address = uncompressed_private_key.address  # Legacy uncompressed address
        values.append(uncompressed_legacy_address)

        return super_obj.__new__(cls, values)

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ', '.join("{}=%r".format(name) for name in self._fields) % self)

    def __str__(self):
        return "{}".format(
            ', '.join("{}=%r".format(name) for name in self._fields) % self)

def _get_addresses(seed:int):
    '''
    Получить адреса и приватники для данного целочисленного зерна
    :param seed:
    :return:
    '''
    compressed_private_key = Key.from_int(seed) # Compressed by default

    compressed_private_key_wif = compressed_private_key.to_wif() #compressed private key
    print('compressed_private_key_wif' ,compressed_private_key_wif)

    compressed_legacy_address = compressed_private_key.address  #Legacy compressed address
    print('compressed_legacy_address' ,compressed_legacy_address)

    segwit_p2sh_address = compressed_private_key.segwit_address # Segwit P2SH
    print('segwit_p2sh_address', segwit_p2sh_address)

    public_key = compressed_private_key.public_key
    public_key = ripemd160_sha256(public_key)
    segwit_address = encode('bc', 0, public_key)
    print('segwit_address', segwit_address)

    # ucompressed
    uncompressed_private_key_wif = bytes_to_wif(compressed_private_key.to_bytes(), compressed=False)
    print('uncompressed_private_key_wif', uncompressed_private_key_wif)

    uncompressed_private_key = Key(uncompressed_private_key_wif)

    uncompressed_legacy_address = uncompressed_private_key.address  #Legacy uncompressed address
    print('uncompressed_legacy_address' , uncompressed_legacy_address)

    #segwit on uncomprssed key - могут быть проблемы? Но вроде разрешили https://github.com/bitcoin/bitcoin/issues/20178
    # the public key used in P2SH-P2WPKH MUST be compressed https://bitcoincore.org/en/segwit_wallet_dev/
    #NONE uncomprssed_segwit_p2sh_address = uncompressed_private_key.segwit_address # Segwit P2SH
    #print('uncomprssed_segwit_p2sh_address', uncomprssed_segwit_p2sh_address)

    uncomprssed_public_key = uncompressed_private_key.public_key
    uncomprssed_public_key = ripemd160_sha256(uncomprssed_public_key)
    uncomprssed_segwit_address = encode('bc', 0, uncomprssed_public_key)
    print('uncomprssed_segwit_address', uncomprssed_segwit_address)
    pass

def _get_ripemd160(seed:int):
    '''
    Получить ripemd160 адреса и приватники для данного целочисленного зерна
    :param seed:
    :return:
    '''
    compressed_private_key = Key.from_int(seed) # Compressed by default

    compressed_private_key_wif = compressed_private_key.to_wif() #compressed private key
    print('compressed_private_key_wif' ,compressed_private_key_wif)

    compressed_byte_public_key = compressed_private_key._pk.public_key.format(compressed=True)
    compressed_ripemd160 = ripemd160_sha256(compressed_byte_public_key).hex()
    print('compressed_ripemd160', compressed_ripemd160)

    uncompressed_byte_public_key = compressed_private_key._pk.public_key.format(compressed=False)
    uncompressed_ripemd160 = ripemd160_sha256(uncompressed_byte_public_key).hex()
    print('uncompressed_ripemd160', uncompressed_ripemd160)

    pass

def process_seed(seed:int):
    '''
    Обработать адреса полученные из seed
    :param seed:
    :return:
    '''
    # print('seed', seed)
    if seed <= 0: #  ValueError: Secret scalar must be greater than 0 and less than 115792089237316195423570985008687907852837564279074904382605163141518161494337.
        return

    rec = BitRecordRipemd160(seed)
    print(rec, ' type', type(rec))
    print(rec.compressed_ripemd160)
    print(rec.uncompressed_ripemd160)

    # rec = BitRecordAddress(seed)
    # print(rec.segwit_address)
    # print(rec.segwit_p2sh_address)
    # print(rec.compressed_legacy_address)
    # print(rec.uncompressed_legacy_address)
    pass

def test_keys():
    seed = 5122
    _get_addresses(seed)
    pass

def test2(seed):
    rec = BitRecordAddress(seed)
    print(rec, ' type', type(rec))
    print(rec.compressed_private_key_wif)
    print(rec.compressed_legacy_address)
    pass

def test_ripemd160(seed):
    #_get_ripemd160(seed)
    rec = BitRecordRipemd160(seed)
    print(rec, ' type', type(rec))
    print(rec.compressed_ripemd160)
    print(rec.uncompressed_ripemd160)
    pass

if __name__ == '__main__':
    #test_keys()
    #test2(145)
    test_ripemd160(1)