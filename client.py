from twisted.internet import reactor, protocol

import sys

class EchoClient(protocol.Protocol):
    def connectionMade(self):
        self.transport.write(self.factory.data)

    def dataReceived(self, data):
        print(data.decode('utf-8'))
        self.transport.loseConnection()

    def connectionLost(self, reason):
        pass

class EchoClientFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, data=None):
        self.data = data

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed! Server Unvailable! Please check config!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        reactor.stop()


def main():
    data = None
    if 1 < len(sys.argv) < 3:
        data = sys.argv[1].encode('utf-8')
    elif 2 < len(sys.argv) < 4:
        data = (sys.argv[1] + " " + sys.argv[2]).encode('utf-8')
    elif len(sys.argv) == 1:
        data = "help".encode('utf-8')
    f = EchoClientFactory(data)
    reactor.connectTCP("localhost", 8000, f)
    reactor.run()

if __name__ == '__main__':
    main()
