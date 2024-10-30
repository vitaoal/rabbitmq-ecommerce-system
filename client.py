import pika
import sys
from asym_cript import *

ORDERS = {
    'order.clothes': 'Jaqueta Nike',
    'order.electronics': 'Smartphone Samsung',
    'order.white': 'Geladeira Brastemp'
}

def initConnection(host = 'localhost'):
    """
    Função para inicializar a conexão com o RabbitMQ
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    return channel

def main():
    print("Iniciando carrinho...")

    channel = initConnection()

    # Cria a exchange 'order_type' para enviar mensagens
    # utilizando o roteamento 'topic', um tópico por categoria de pedido
    channel.exchange_declare(exchange='order_type', exchange_type='topic')

    # Carrega a sua chave privada
    private_key = load_private_key(r'keys\client\private_key.pem')

    while True:
        print("\n === E-COMMERCE ONLINE === ")

        for i, (key, value) in enumerate(ORDERS.items()):
            print(f"{i} - {value}")

        print("e - Sair")
        print(" ========================== ")
        option = input("Escolha uma opção: ")

        if option == 'e':
            break

        for i, (key, value) in enumerate(ORDERS.items()):
            if str(i) == str(option):
                print(f"\n Enviando pedido: {value}")

                order_id = value
                print("Enviando pedido para a fila 'order_queue'...")
                # Assina a mensagem com a sua chave privada
                # Necessário converter para hexadecimal para enviar pq não sei concatenar bytes
                signature = sign(order_id.encode(), private_key)
                signature = signature.hex()
                message = f"{order_id}|{signature}"
                # Envia a mensagem para a exchange 'order_type' com a chave do pedido
                print(f" [x] Sent {order_id}")
                channel.basic_publish(exchange='order_type', routing_key=key, body=message)
                break
    
    print("Fechando conexão...")
    channel.close()

if __name__ == "__main__":
    main()