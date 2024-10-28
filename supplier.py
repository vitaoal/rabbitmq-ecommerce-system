import pika
import sys
from functools import partial
from asym_cript import *

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

        message2 = ' '.join(sys.argv[1:]) or "Jaqueta Nike"
        signature = sign(message2.encode(), private).hex()
        message1 = f"{message2}|{signature}"

        channel2.basic_publish(
                exchange='',
                routing_key='task_queue',
                body=message1
            )
        print(f" [x] Sent {message2}")

def main():
    channel = initConnection()

    # Configura a exchange 'order_type' do tipo 'topic'
    channel.exchange_declare(exchange='order_type', exchange_type='topic')
    channel2 = initConnection()
    channel2.queue_declare(queue='task_queue', durable=True)
    private = load_private_key(r'keys\supplier_1\private_key.pem')

    
    # Nome único da fila para 'order.clothes'
    queue_name = 'order_queue_clothes'
    channel.queue_declare(queue=queue_name, exclusive=True)
    channel.queue_bind(exchange='order_type', queue=queue_name, routing_key='order.clothes')

    # Consumir mensagens específicas do tópico 'order.clothes'
    channel.basic_consume(queue=queue_name, on_message_callback= partial(callback, private = private, channel2 = channel2), auto_ack=True)

    print("Aguardando mensagens do tópico 'order.clothes'...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
