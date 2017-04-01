from concurrent import futures

import grpc
import hashlib
import logging
import sqlite3
import time
import uuid

import no_thanks_pb2
import no_thanks_pb2_grpc


DATABASE = './test.db'


class NoThanks(no_thanks_pb2_grpc.NoThanksServicer):
  def __init__(self, db_path):
    self.db_path = db_path
  
  def Register(self, request, context):
    if not request.name or not request.password:
      raise ValueError('no name or password provided')
    
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name=?', (request.name,))
    entry = cursor.fetchone()

    if not entry:
      logging.info('Creating user "%s"', request.name);
      user = no_thanks_pb2.User()
      user.name = request.name
      user.password_hash = hashlib.sha256(request.password).hexdigest()
      user.client_id = hash(uuid.uuid4()) % (1 << 63)
      cursor.execute('INSERT INTO users VALUES (?,?)', (
        request.name, sqlite3.Binary(user.SerializeToString())))
      conn.commit()
    else:
      user = no_thanks_pb2.User()
      user.ParseFromString(entry[1])

    # Verify password. I know this doesn't have salt or anything, but I'm just
    # trying to avoid name collissions, not be super secure.
    password_hash = hashlib.sha256(request.password).hexdigest()
    if password_hash != user.password_hash:
      raise ValueError('Invalid password')

    return no_thanks_pb2.RegisterResponse(client_id=user.client_id)


def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  no_thanks = NoThanks(DATABASE)
  no_thanks_pb2_grpc.add_NoThanksServicer_to_server(no_thanks, server)
  server.add_insecure_port('[::]:50123')
  server.start()
  try:
    while True:
      time.sleep(60.0)
  except KeyboardInterrupt:
    server.stop(0)

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  serve()
