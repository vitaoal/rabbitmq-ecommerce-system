import pika
import sys
from asym_cript import *

def initConnection(host = 'localhost'):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    channel.queue_declare(queue='order_queue')
    return channel

def callback(ch, method, properties, body):
    body = body.decode()
    print(f" [x] Received {body}")
    message, signature = body.split('|', 1)

    signature = bytes.fromhex(signature)
    public_key = load_public_key(r'keys\client\public_key.pem')

    # Verifica a assinatura da mensagem com a chave pública do fornecedor
    is_valid = verify(signature, message.encode(), public_key)
    print(f" [x] Received {message} - Assinatura válida: {is_valid}")

def main():
    print("Iniciando fornecedor...")
    channel = initConnection()

    channel.exchange_declare(exchange='order_type', exchange_type='topic')
    queue_name = 'order_queue'

    # Liga a fila 'order_queue' à exchange 'order_type' com a chave '*' recebendo todas as msgs
    channel.queue_bind(exchange='order_type', queue=queue_name, routing_key='order.*')

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

if __name__ == "__main__":
    main()