import subprocess
import sys
import gobject

__all__ = ("SelectProcess", "ThreadedProcess", "GProcess")

def gsignature(*args, **kwargs):
    run_when = kwargs.pop("run_when", gobject.SIGNAL_RUN_FIRST)
    return_type = kwargs.pop("return_type", gobject.TYPE_NONE)
    return (run_when, return_type, args)

def read_all_iter(buff, block_size=1024):
    """Auxiliar function that reads all data it cans"""
    chunk = buff.read(block_size)
    yield chunk
    
    while len(chunk) == block_size:
        chunk = buff.read(block_size)
        yield chunk

def read_all(sock, block_size=1024):
    return "".join(read_all_iter(sock, block_size))


class AbstractGProcess(gobject.GObject):
    __gsignals__ = {
        "started": gsignature(gobject.TYPE_INT),
        "finished": gsignature(gobject.TYPE_INT),
        "stdout-data": gsignature(gobject.TYPE_STRING),
        "stderr-data": gsignature(gobject.TYPE_STRING),
    }
    
    def __init__(self, args):
        self.args = args
        gobject.GObject.__init__(self)

    def stop(self):
        if self.proc is None:
            return
        
        if self.proc.poll() is not None:
            return
            
        try:
            os.kill(self.proc.pid, 15)
        except OSError:
            try:
                os.kill(self.proc.pid, 9)
            except OSError:
                pass
        

    def do_finished(self, pid):
        self.proc = None

class PolledProcess(AbstractGProcess):
    polling_time = 50
    
    def start(self):
        self.proc = subprocess.Popen(
            self.args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            
        )
        self.emit("started", self.proc.pid)
        gobject.timeout_add(self.polling_time, self.on_tick)
    
    def on_tick(self):
        val = self.proc.poll()
        if val is not None:
            # TODO: make this smoother, data should be read in
            # chunks in order to avoid flooding the UI with info
            self.emit("stdout-data", self.proc.stdout.read())
            self.emit("stderr-data", self.proc.stderr.read())
            self.emit("finished", val)

        return val is None

class SelectProcess(AbstractGProcess):

    def start(self):
        self.proc = subprocess.Popen(
            self.args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        gobject.io_add_watch(self.proc.stdout, gobject.IO_IN, self.on_buff_read, "stdout-data")
        gobject.io_add_watch(self.proc.stderr, gobject.IO_IN, self.on_buff_read, "stderr-data")
        gobject.child_watch_add(self.proc.pid, self.on_finished)
        self.emit("started", self.proc.pid)

    def on_buff_read(self, fd, cond, signame):
        self.emit(signame, read_all(fd))
    
    def on_finished(self, pid, condition):
        self.emit("finished", condition / 256)

if sys.platform == "win32":
    GProcess = ThreadedProcess
else:
    GProcess = SelectProcess
    
if __name__ == '__main__':
    import gtk

    def on_read(proc, data):
        print data,

    def on_finished(obj, err):
        print err,
        gtk.main_quit()

    #gproc = GProcess
    gproc = PolledProcess


    proc = gproc(sys.argv[1:])
    proc.start()
    proc.connect("finished", on_finished)
    proc.connect("stdout-data", on_read)
    proc.connect("stderr-data", on_read)
    gtk.main()


