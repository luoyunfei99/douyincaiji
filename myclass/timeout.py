import threading

class TimeoutThread(threading.Thread):
    def __init__(self, target, args=(), kwargs={}):
        threading.Thread.__init__(self)
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.error = None

    def run(self):
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception as e:
            self.error = e