# -*- coding: utf-8 -*-
# base Pythin modules
import SocketServer, threading, signal
# my Python modules
import task_manager, cache_manager, my_handler

ADDRESS = 'localhost'
PORT = 8080
DB_NAME = 'twitter_data.db'

class MyServer(SocketServer.ThreadingTCPServer):
    def __init__(self, *args, **kwargs):
        SocketServer.ThreadingTCPServer.__init__(self, *args, **kwargs)
        
        print '<server> Initializing cache'
        self.__cacheManager = cache_manager.CacheManager()
        
        print '<server> Initializing manager'
        self.__taskEvent = threading.Event()
        self.__taskManager = task_manager.TaskManager(self, DB_NAME, self.__taskEvent, self.__cacheManager)
        self.__taskManager.start()
        self.__taskEvent.set()
        
        self.__taskTimer = threading.Timer(30, self.__eventSignaller)
        self.__taskTimer.start()
    
        signal.signal(signal.SIGINT, self.requestShutDown)
    #end __init__
        
    def __eventSignaller(self):
        timer = 30
        if not self.__taskManager.isWorking():
            print '<server> Waking manager...'
            self.__taskEvent.set()
        else:
            timer = 10
            
        self.__taskTimer = threading.Timer(timer, self.__eventSignaller)
        self.__taskTimer.start()

    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        self.RequestHandlerClass(self.__cacheManager, request, client_address, self)
        
    def requestShutDown(self, *args):
        print '<server> Shutdown sequence initiated...'
        self.__taskTimer.cancel()
        self.__taskManager.requestShutDown()
        self.__taskEvent.set()
#end MyServer
        
def main():
    server = MyServer((ADDRESS, PORT), my_handler.MyHandler)
    server.serve_forever()
    server.server_close()

if __name__ == "__main__":
    main()