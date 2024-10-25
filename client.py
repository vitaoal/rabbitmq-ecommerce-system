import pika
import sys

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
    channel.queue_declare(queue='notification_queue')       # Será usada posteriormente
    return channel

def main():
    print("Iniciando carrinho...")

    channel = initConnection()

    # Cria a exchange 'order_type' para enviar mensagens
    # utilizando o roteamento'topic', um tópico por categoria de pedido
    channel.exchange_declare(exchange='order_type', exchange_type='topic')

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
            if str(i) == option:
                order_id = key
                print("Enviando pedido para a fila 'order_queue'...")
                channel.basic_publish(exchange='order_type', routing_key=order_id, body=order_id)
                break
    
    print("Fechando conexão...")
    channel.close()

if __name__ == "__main__":
    main()