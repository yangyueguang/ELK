import sys
import pika
def send():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

    routing_key = sys.argv[1] if len(sys.argv) > 1 else 'anonymous.info'
    message = ' '.join(sys.argv[2:]) or 'Hello World!'
    channel.basic_publish(exchange='topic_logs',
                          routing_key=routing_key,
                          body=message)
    print(" [x] Sent %r:%r" % (routing_key, message))
    connection.close()

def recept():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    binding_keys = 'kern.*'
    if not binding_keys:
        print("Usage: %s [binding_key]..." % (sys.argv[0],))
        sys.exit(1)

    for binding_key in binding_keys:
        channel.queue_bind(exchange='topic_logs',
                           queue=queue_name,
                           routing_key=binding_key)

    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body,))

    channel.basic_consume(callback,
                          queue=queue_name,
                          no_ack=True)

    channel.start_consuming()



