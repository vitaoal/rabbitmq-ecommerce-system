from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import os

DEBUG = False

# Gerar par de chaves
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key

def encrypt(message, public_key):
    encrypted = public_key.encrypt(message, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
        )
    )
    return encrypted

def decrypt(encrypted, private_key):
    decrypted = private_key.decrypt(encrypted, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
        )
    )
    return decrypted

def sign(message, private_key):
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify(signature, message, public_key):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False

def load_public_key(path):
    with open(path, "rb") as file:
        public_key = serialization.load_pem_public_key(file.read())
    return public_key

def load_private_key(path):
    with open(path, "rb") as file:
        private_key = serialization.load_pem_private_key(file.read(), password=None)
    return private_key

def main():
     
    print("Gerando par de chaves...")
    private_key, public_key = generate_keys()
    with open(r"keys\client\private_key.pem", "wb") as file:
        file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open(r"keys\client\public_key.pem", "wb") as file:
        file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
          

    for x in range(1,4):

        directory = f"keys/supplier_{x}"

        private_key, public_key = generate_keys()
        with open(os.path.join(directory, "private_key.pem"), "wb") as file:
            file.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
        ))
        with open(os.path.join(directory, "public_key.pem"), "wb") as file:

            file.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
        x = x + 1

    if DEBUG:
        print("Carregando chaves do arquivo...")
        loaded_private_key = load_private_key(r"keys\client\private_key.pem")
        loaded_public_key = load_public_key(r"keys\client\public_key.pem")

        message = b"Mensagem de teste"
        print("Criptografando mensagem...")
        encrypted_message = encrypt(message, loaded_public_key)
        print("Mensagem criptografada:", encrypted_message)

        print("Descriptografando mensagem...")
        decrypted_message = decrypt(encrypted_message, loaded_private_key)
        print("Mensagem descriptografada:", decrypted_message)

        print("Assinando mensagem...")
        signature = sign(message, loaded_private_key)
        print("Assinatura:", signature)

        print("Verificando assinatura...")
        is_valid = verify(signature, message, loaded_public_key)
        print("Assinatura válida:", is_valid)

if __name__ == "__main__":
    main()