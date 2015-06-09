import queue
import random
from converter import ConverterQueue

GlobalSessionsTable = {}

def do_convertion(task_item):
    x = random.randint(10,10000)
    print("Converting! ", task_item, x)
    task_item.run()
    print("Watcher Socket:", GlobalSessionsTable[task_item.watchers])
    SocketToWatcher = GlobalSessionsTable[task_item.watchers]
    SocketToWatcher.send("done")
    print("Done ", x)

def renew_queue(task):
    global mainQueue, converterQueue
    mainQueue = queue.Queue(0)
    converterQueue = ConverterQueue(mainQueue, do_convertion)
    mainQueue.put(task)
    converterQueue.start()

mainQueue = queue.Queue(0)
converterQueue = ConverterQueue(mainQueue, do_convertion)
