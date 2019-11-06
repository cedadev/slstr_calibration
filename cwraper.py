#!/usr/bin/python -W ignore
#  Class to connect a process to output and error streams 
# sjp 28/1/04
#

import smtplib, subprocess, sys, os, time, string, pwd, grp, thread, signal, getopt

#----------------------------------
class collector:

# helper class to collect an output stream. This class tops and tails the stream so that non bulky out put can
# be sent in emails etc.
#
# 

    def __init__(self,ntop=100,nbot=5):
        self.head = ""
        self.total_size=0
        self.ntop = 1024*ntop
        self.nbot = 1024*nbot
        self.is_split=0

    def write(self,buf):
        if self.is_split:
            self.tail = self.tail +buf
            self.tail = self.tail[-self.nbot:]
        else:
           self.head = self.head + buf
           if self.total_size > self.ntop+ 2*self.nbot:
                self.head = self.head[:self.ntop]
                self.tail = self.head[-self.nbot:]
                self.is_split =1
 
        self.total_size=len(buf) +self.total_size
        
    def size(self): return self.total_size
	
    def content(self): 
        if self.is_split:
            return "%s...\n\n\n\n     ...%s" % (self.head, self.tail) 
        else:
            return "%s" % self.head	    
 

#-------------------------------
class connector:

# main class to connect a script to output and error files

    logfile = "/group_workspaces/cems2/slstr_cpa/cron_logs/cwraper.log"
#    logfile = "cwraper.log"

    def __init__(self,script, outputlog, errorlog):
        self.start_time=time.time()
	self.process = subprocess.Popen(script, shell=True, bufsize=4096,
	               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  #      self.process=popen2.Popen3(script,1)
        self.fromchild = self.process.stdout
        self.childerr = self.process.stderr
	self.script=script
	self.output=collector()
	self.errors=collector()
	self.status = -1
	self.killed = 0
	self.returncode = None
	self.stdout_log = outputlog
	self.stderr_log = errorlog
	self.cwd = os.getcwd()

    def read_output(self):
        nbuf=1024*4
	if self.stdout_log: output_log = open(self.stdout_log, "w")
	else:  output_log = open("/dev/null", "w")
        while 1:
	    # do stadard output stuff 
            outbuf=self.fromchild.read(nbuf)
            self.output.write(outbuf)		
            output_log.write(outbuf)		
            if outbuf=="": break

    def read_errors(self):
        nbuf=1024*4
	if self.stderr_log: err_log = open(self.stderr_log, "w")
	else:  err_log = open("/dev/null", "w")
        while 1:
	    # do stadard error stuff 
            errbuf=self.childerr.read(nbuf)
            self.errors.write(errbuf)
            err_log.write(errbuf)
            if errbuf=="": break

    def runtime(self): return time.time()-self.start_time

    def pid(self):
        if os.name == "nt": return "WINDOWS no pid"
        else: return self.process.pid

    def kill(self):
        os.kill(self.process.pid,signal.SIGKILL)     
	time.sleep(1)
	self.killed=1

    def do(self,timeout):
	
	# start threads to colloect output and errors
        thread.start_new_thread(self.read_output,())
        thread.start_new_thread(self.read_errors,())

        #  loop until process stops.  If time out is reached kill process 
        while 1: 
	    pollint=self.runtime()*0.01 +0.001
	    self.returncode = self.process.poll()
	    if self.returncode == None and self.runtime() < timeout: time.sleep(pollint)		
	    elif self.returncode == None: self.kill()
	    else: break
	
	if self.killed: self.status = 4
	elif self.returncode != 0: self.status = 3
	elif self.errors.size(): self.status = 2
	elif self.output.size(): self.status = 1
 	else: self.status = 0 
	
	self.end_time=time.time()
	
	return self.status
	
    def status_str(self):
	status_msgs = ("Ran - no output","Ran with output", "Ran with errors", "Failed","Failed - Killed on timeout","Running")
        return status_msgs[self.status] 
    
    def log(self):
        fh = open(connector.logfile, "a")     
        fh.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (time.asctime(time.localtime(self.start_time)),
	                 time.asctime(time.localtime(self.end_time)),
			 self.status_str(), 
			 pwd.getpwuid(os.getuid())[0],grp.getgrgid(os.getgid())[0],
			 os.uname()[1],
			 self.output.size(), self.errors.size(),
			 self.script)) 
	fh.close()

    def summary(self):
        msg = ""
	msg = msg + "script:      %s\n" % self.script
	msg = msg + "working directory:      %s\n" % self.cwd
	msg = msg + "status:      %s\n" % self.status_str()
	msg = msg + "returncode:  %s\n" % self.returncode
	msg = msg + "start time:  %s\n" % time.asctime(time.localtime(self.start_time))
	msg = msg + "end time:    %s\n" % time.asctime(time.localtime(self.end_time))
	run_time = self.end_time - self.start_time
	if run_time > 60*60*2: run_time = "%s Hours" % (run_time/(60*60.0)) 
	elif run_time > 60*2: run_time = "%s Minutes" % (run_time/60.0) 
	else: run_time = "%s Seconds" % run_time
	msg = msg + "run time:    %s\n" % run_time
	msg = msg + "uid:         %s(%s)\n" % (pwd.getpwuid(os.getuid())[0],os.getuid())
	msg = msg + "gid:         %s(%s)\n" % (grp.getgrgid(os.getgid())[0],os.getgid())
	msg = msg + "host:        %s\n" % os.uname()[1]
	msg = msg + "output log:  %s\n" % self.stdout_log
	msg = msg + "error log:   %s\n" % self.stderr_log
	msg = msg + "---------------------------\noutput size: %s\n" % self.output.size()
	msg = msg + "summary output:\n%s\n" % self.output.content()
	msg = msg + "---------------------------\nerrors size: %s\n" % self.errors.size()
	msg = msg + "summary errors:\n%s\n" % self.errors.content()
	return msg


#------------------------------------------
# MAIN PROGRAM
#
if __name__ == "__main__":

    def usage():
        print "Usage: cwraper [-t N] [-o output.txt] [-e error.txt] <email> <notify-level> <script>"
	print ""
	print "    -t N           set timeout to N hours. N can be a decimal to give small timeouts. Default=12"
	print "    -o output.txt  set log for standard out from the script "
	print "    -e error.txt   set log for standard error from the script "
	print "    <email> is the email address that will recieve the output,"
	print "            errors and other information generated by the script."
	print "    <notify-level> is an integer specifiying at which the message is sent out." 
	print "            Notify levels have the following meaning:" 
	print "            0 - Message is sent ever time."
	print "            1 - Send message only if some standard output is produced."
	print "            2 - Send message only if some standard error is produced."
	print "            3 - Send message only if the script fails (exit status non zero)."
	print "            4 - Send message only if the script fails by timeout" 
	print "            5 - Never send a message." 
	print "    <script> is command to be run." 
	raise "Usage Error"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:o:e:", 
	            ["help", "timeout=", "outputlog=", "errorlog="])
    except getopt.GetoptError, err:
        # print help information and exit:
        usage()
        sys.exit(2)
    outputlog = None
    errorlog = None
    timeout = 12.0 # timeout in hours


    for o, a in opts:
        if o in  ("-t", "-timeout"):
            timeout = float(a)
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--outputlog"):
            outputlog = a
        elif o in ("-e", "--errorlog"):
            errorlog = a
        else:
            assert False, "unhandled option"

    timeout = timeout *3600  #timeout in secs
	
    if len(args) < 3: usage()
    else:
	notify = args[0]
	level = args[1]
	script = string.join(args[2:]," ")

    #check for email address
    if notify.find("@") == -1: 
	print "*** Need email address\n"
	usage() 

    # check for int notify level
    try:
	level = int(level)
    except:
	print "*** Need int notify-level\n"
	usage() 

    # make connector and run script 
    c=connector(script, outputlog, errorlog)
    status = c.do(timeout)
    c.log()

    # email if status is >= notify-level	
    if status >= level: 

	msg = """Subject: %s: %s\n\n""" % (c.status_str(), script)

	msg = msg + "Notification from cron wrapper program\n\n"
	msg = msg + c.summary()


	server = smtplib.SMTP('localhost')
        server.sendmail('"Sam" <badc@rl.ac.uk>',notify,msg)

