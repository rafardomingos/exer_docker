import psycopg2
import redis
import json
from bottle import Bottle, request

print('Aguardando menssagens...sssss')
class Sender(Bottle):
	def __init__(self):
		super().__init__()
		self.route('/', method='POST', callback=self.send)
		self.fila = redis.StrictRedis(host='service_queue', port=6379, db=0)
		DSN = 'dbname=email_sender user=postgres host=service_db'
		self.conn = psycopg2.connect(DSN)

	def register_message(self, subject, message):
		SQL = 'INSERT INTO emails (subject, message) VALUES (%s, %s)'
		cur = self.conn.cursor()
		cur.execute(SQL, (subject, message))
		self.conn.commit()
		cur.close()

		msg = {'subject': subject, 'message': message}
		self.fila.rpush('sender', json.dumps(msg))

		print('Mensagem registrada!')

	def send(self):
		assunto = request.forms.get('assunto')
		mensagem = request.forms.get('mensagem')

		self.register_message(assunto, mensagem)
		
		return 'Mensagem enfileirada! Assunto: {} Mensagem: {}'.format(
			assunto, mensagem
		)

if __name__ == '__main__':
	sender = Sender()
	sender.run(host='0.0.0.0', port=8000, debug=True)