import pika
import sys
from functools import partial
from asym_cript import *

SELF_NAME = 'supplier_2'

def initConnection(host='localhost'):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    return channel

def callback(ch, method, properties, body, private, channel2):
    body = body.decode()
    message, signature = body.split('|', 1)
    signature = bytes.fromhex(signature)
    public_key = load_public_key(r'keys\client\public_key.pem')
    is_valid = verify(signature, message.encode(), public_key)
    print(f" [x] Received {message} - Assinatura válida: {is_valid}")

    if is_valid == True :
        
        print("\n === ENVIO DE MERCADORIA === ")

        message2 = ' '.join(sys.argv[1:]) or "Smartphone Samsung"
        signature = sign(message2.encode(), private).hex()
        message1 = f"{SELF_NAME}|{message2}|{signature}"

        channel2.basic_publish(
                exchange='',
                routing_key='task_queue',
                body=message1
            )
        print(f" [x] Sent {message2}")

def main():
    # Configura a exchange 'order_type' do tipo 'topic'
    channel = initConnection()
    channel.exchange_declare(exchange='order_type', exchange_type='topic')

    # Channel2 para enviar mensagens para a fila 'task_queue'
    channel2 = initConnection()
    channel2.queue_declare(queue='task_queue', durable=True)

    private = load_private_key(r'keys\supplier_2\private_key.pem')

    # Nome único da fila para 'order.electronics'
    queue_name = 'order_queue_electronics'
    channel.queue_declare(queue=queue_name, exclusive=True)
    channel.queue_bind(exchange='order_type', queue=queue_name, routing_key='order.electronics')

    # Consumir mensagens específicas do tópico 'order.electronics'
    channel.basic_consume(queue=queue_name, on_message_callback= partial(callback, private = private, channel2 = channel2), auto_ack=True)

    print("Aguardando mensagens do tópico 'order.electronics'...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
