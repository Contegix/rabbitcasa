import sys
import simpledaemon
import logging as logger
import puka
import json
import base64

from cassandra.cluster import Cluster

class RabbitCasaDaemon(simpledaemon.Daemon):

    default_conf = '/etc/rabbitcasa.conf'
    section = 'rabbitcasa'

    def conf(self, configname):
        """ read in configurations from file and establish as part of the inner workings of this daemon object """

        # first, make sure we have a configs list initialized
        if not hasattr(self, 'configs'):
            self.configs = dict()

        # next, see if the configuration we want is not available
        if configname not in self.configs:
            self.configs[configname] = self.config.get(self.section, configname)
            logger.debug('configuration \'%s\' given value: %s' % (configname, self.configs[configname]))

        return self.configs[configname]

    def run(self):
        # init our varying connection wrappers
        self.config = self.config_parser

        cassandra_cluster = self.conf('cassandra_cluster').split(",")
        cassandra_keyspace = self.conf('cassandra_keyspace')
        cassandra_keyspace_statement = self.conf('cassandra_keyspace_statement')
        cassandra_table_statement = self.conf('cassandra_table_statement')
        cassandra_query_fields = self.conf('cassandra_query_fields').split(",")
        cassandra_body_field = self.conf('cassandra_body_field')
        cassandra_insert_statement = self.conf('cassandra_insert_statement')

        logger.debug(cassandra_cluster)
        cluster = Cluster(cassandra_cluster)
        session = cluster.connect()
        session.execute(cassandra_keyspace_statement)
        session = cluster.connect(cassandra_keyspace)
  
        session.execute(cassandra_table_statement)

        rabbit_queue = self.conf('rabbitqueue')
        rabbit_requeue = self.conf('rabbitrequeue')
        rabbitmq_url = self.conf('rabbitmq_url')
       
	client = puka.Client(rabbitmq_url)
	promise = client.connect()
	client.wait(promise)

	promise = client.queue_declare(queue=rabbit_queue, durable=True)
	client.wait(promise)
	if rabbit_requeue:
		promise = client.queue_declare(queue=rabbit_requeue, durable=True)
		client.wait(promise)

	consume_promise = client.basic_consume(queue=rabbit_queue, prefetch_count=1)
        while True:
  		try:
			result = client.wait(consume_promise)
                        payload = json.loads(result['body']) 
                        fields = []
                        values = []
                        for field in cassandra_query_fields:
                            fields.append(field)
                            if isinstance(payload[field], basestring):
                                values.append(payload[field].strip())
                            else:
                                values.append(payload[field])
                        fields.append(cassandra_body_field)
                        body = ''
                        try:
                            if 'body' in payload['body']:
                                body = payload['body']['body']
                            else:
                                body = payload['body']
                        except Exception as e:
                            logger.exception('Failed to append payload')

                        if body:
                            values.append(body.strip())
                        else:
                            values.append(' ')

    			client.basic_ack(result)

                        insert_statement = session.prepare(cassandra_insert_statement)
                        session.execute(insert_statement.bind( values ))

			if rabbit_requeue:
				promise = client.basic_publish(exchange='', routing_key=rabbit_requeue, body=result['body'])
				client.wait(promise)
		except KeyboardInterrupt as e:
			promise = client.close()
			client.wait(promise)
			raise

if __name__ == '__main__':
    RabbitCasaDaemon().main()
