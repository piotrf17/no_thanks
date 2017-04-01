from __future__ import print_function

import grpc

import no_thanks_pb2
import no_thanks_pb2_grpc

class NoThanksClient(object):
  def __init__(self, server_address):
    self.channel = grpc.insecure_channel(server_address)
    self.stub = no_thanks_pb2_grpc.NoThanksStub(self.channel)

  def Register(self, name, password):
    request = no_thanks_pb2.RegisterRequest(name=name, password=password)
    response = self.stub.Register(request)
    return response.client_id
