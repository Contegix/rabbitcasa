import sys
import simpledaemon
import logging as logger
import puka

class RabbitCasaDaemon(simpledaemon.Daemon):

    default_conf = '/etc/rabbitcasa.conf'
    section = 'RabbitMQ'

    def conf(self, configname):
        """ read in configurations from file and establish as part of the inner workings of this daemon object """

        # first, make sure we have a configs list initialized
        if not hasattr(self, 'configs'):
            self.configs = dict()

        # next, see if the configuration we want is not available
        if configname not in self.configs:
            self.configs[configname] = self.config.get(self.section, configname)
            log.debug('configuration \'%s\' given value: %s' % (configname, self.configs[configname]))

        return self.configs[configname]

    def run(self):
        # init our varying connection wrappers
        self.config = self.config_parser
        #user = self.conf('myuser'),
	#TODO: Queue should be in config 
	#client args should be in config
	
	client = puka.Client("amqp://localhost/")
	promise = client.connect()
	client.wait(promise)

	promise = client.queue_declare(queue='report-collector', durable=True)
	client.wait(promise)

	consume_promise = client.basic_consume(queue='report-collector', prefetch_count=1)
        while True:
  		try:
			result = client.wait(consume_promise)
    			logger.debug("Received message %r" % (result,))
    			client.basic_ack(result)
			#TODO: Put in Cassandra
		except KeyboardInterrupt as e:
			promise = client.close()
			client.wait(promise)
			raise

if __name__ == '__main__':
    RabbitCasaDaemon().main()
