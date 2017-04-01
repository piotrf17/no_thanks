import no_thanks_client

SERVER_ADDRESS='localhost:50123'
NAME='random'
PASSWORD='test123'

def main():
  client = no_thanks_client.NoThanksClient(SERVER_ADDRESS)
  client_id = client.Register(NAME, PASSWORD)
  print client_id

if __name__ == "__main__":
  main()
