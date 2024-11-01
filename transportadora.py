import pika
import sys
from asym_cript import *
from functools import partial
import pika

# Conecte-se ao RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Purge da fila especificada
channel.queue_purge(queue='task_queue')

connection.close()

def initConnection(host = 'localhost'):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    channel.queue_declare(queue='')
    return channel

def callback(ch, method, properties, body):
    body = body.decode()
    #print(f" [x] Received {body}")
    author, message, signature = body.split('|', 2)
    print(f" [x] Received {message}")

    signature = bytes.fromhex(signature)

    key_path = f'keys\\{author}\\public_key.pem'

    # Verifica a assinatura com cada chave pública
    public_key = load_public_key(key_path)
    is_valid = verify(signature, message.encode(), public_key)
       
    if is_valid:
        print(f"Assinatura verificada com sucesso usando {public_key}")

def main():
    
    channel = initConnection()
    channel.queue_declare(queue='task_queue', durable=True)

    channel.basic_consume(queue='task_queue', on_message_callback=callback)
    print("Transportadora aguardando pedidos")

    channel.start_consuming()

if __name__ == "__main__":
    main()