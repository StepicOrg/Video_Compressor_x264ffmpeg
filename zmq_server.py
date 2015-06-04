
#
# mainQueue = queue.Queue(0)
# WORKERS = 4
#
# for i in range(WORKERS):
#     ConverterQueue(mainQueue).start()
#
# for i in range(10):
#     mainQueue.put("AAA")
#
# for i in range(WORKERS):
#     mainQueue.put(None)
#

#
# import time
# import zmq
# import queue
# from converter import ConverterQueue
#
# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.bind("tcp://*:5555")
#
# mainQueue = queue.Queue(0)
# converterQueue = ConverterQueue(mainQueue)
# WORKERS = 4
#
#
# while True:
#     #  Wait for next request from client
#     message = socket.recv()
#     print("Received request: %s" % message)
#     if len(message):
#         if converterQueue.is_empty():
#             mainQueue = queue.Queue(0)
#             converterQueue = ConverterQueue(mainQueue)
#             mainQueue.put(message)
#             converterQueue.start()
#         else:
#             mainQueue.put(message)
#
#     #  Do some 'work'
#     time.sleep(1)
#
#     #  Send reply back to client
#     socket.send(b"Im Spawning ")