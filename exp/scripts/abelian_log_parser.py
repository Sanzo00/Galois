##########################################
# To parse log files generated by abelian.
# Author: Gurbinder Gill
# Email: gurbinder533@gmail.com
#########################################

import re
import os
import sys, getopt
import csv
import numpy

######## NOTES:
# All time values are in sec by default.


def match_timers(fileName, benchmark, forHost, numRuns, numThreads, time_unit):

  mean_time = 0.0;
  recvNum_total = 0
  recvBytes_total = 0
  sendNum_total = 0
  sendBytes_total = 0
  sync_pull_avg_time_total = 0.0;
  extract_avg_time_total = 0.0;
  set_avg_time_total = 0.0;
  sync_push_avg_time_total = 0.0;
  graph_init_time = 0
  hg_init_time = 0
  total_time = 0

  if (time_unit == 'seconds'):
    divisor = 1000
  else:
    divisor = 1
  #e2901bc2-f648-4ff4-9976-ac3b4c794a6a,(NULL),0 , TIMER_2,7,0,79907
  timer_regex = re.compile(r'.*,\(NULL\),0\s,\sTIMER_(\d*),' + re.escape(forHost) + r',(\d*),(\d*)')
  #timer_regex = re.compile(r'.*,\(NULL\),0\s,\sTIMER_(\d*),7,\d*,(\d*)')

  log_data = open(fileName).read()

  timers = re.findall(timer_regex, log_data)
  print timers

  for timer in timers:
    mean_time = mean_time + float(timer[2])

  if(len(timers) > 0):
    mean_time /= len(timers)
    mean_time /= divisor
    mean_time = round(mean_time, 3)

  print "Mean time: ", mean_time

  if(benchmark == "cc"):
    benchmark = "ConnectedComp"

  ## SYNC_PULL and SYNC_PUSH total average over runs.
  num_iterations = 0
  for i in range(0, int(numRuns)):
    # find extract
    extract_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),SYNC_EXTRACT_(?i)' + re.escape(benchmark) + r'\w*_' + re.escape(str(i)) + r'_(\d*),\d*,(\d*),(\d*).*')
    extract_lines = re.findall(extract_regex, log_data)
    for j in range (0, len(extract_lines)):
      extract_avg_time_total += float(extract_lines[j][2])

    # find set
    set_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),SYNC_SET_(?i)' + re.escape(benchmark) + r'\w*_' + re.escape(str(i)) + r'_(\d*),\d*,(\d*),(\d*).*')
    set_lines = re.findall(set_regex, log_data)
    for j in range (0, len(set_lines)):
      set_avg_time_total += float(set_lines[j][2])

    # find sync_pull
    sync_pull_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),SYNC_PULL_(?i)' + re.escape(benchmark) + r'\w*_' + re.escape(str(i)) + r'_(\d*),\d*,(\d*),(\d*).*')
    sync_pull_lines = re.findall(sync_pull_regex, log_data)
    num_iterations = len(sync_pull_lines);
    for j in range (0, len(sync_pull_lines)):
      sync_pull_avg_time_total += float(sync_pull_lines[j][2])

    # find sync_push
    sync_push_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),SYNC_PUSH_(?i)' + re.escape(benchmark) + r'\w*_'+ re.escape(str(i)) + r'_(\d*),\d*,(\d*),(\d*).*')
    sync_push_lines = re.findall(sync_push_regex, log_data)

    if(num_iterations == 0):
      num_iterations = len(sync_push_lines)

    for j in range (0, len(sync_push_lines)):
      sync_push_avg_time_total += float(sync_push_lines[j][2])

  extract_avg_time_total /= int(numRuns)
  extract_avg_time_total /= divisor
  extract_avg_time_total = round(extract_avg_time_total, 0)

  set_avg_time_total /= int(numRuns)
  set_avg_time_total /= divisor
  set_avg_time_total = round(set_avg_time_total, 0)

  sync_pull_avg_time_total /= int(numRuns)
  sync_pull_avg_time_total /= divisor
  sync_pull_avg_time_total = round(sync_pull_avg_time_total, 0)

  sync_push_avg_time_total /= int(numRuns)
  sync_push_avg_time_total /= divisor
  sync_push_avg_time_total = round(sync_push_avg_time_total, 0)

  ## sendBytes and recvBytes.
  #recvBytes_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),RecvBytes,\d*,(\d*),(\d*),.*')
  #recvBytes_search = recvBytes_regex.search(log_data)
  #if recvBytes_search is not None:
     #recvBytes_total = float(recvBytes_search.group(1))/int(numRuns)

  #sendBytes_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),SendBytes,\d*,(\d*),(\d*),.*')
  #sendBytes_search = sendBytes_regex.search(log_data)
  #if sendBytes_search is not None:
    #sendBytes_total = float(sendBytes_search.group(1))/int(numRuns)

  ## sendNum and recvNum.
  #recvNum_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),RecvNum,\d*,(\d*),(\d*),.*')
  #recvNum_search = recvNum_regex.search(log_data)
  #if recvNum_search is not None:
    #recvNum_total = float(recvNum_search.group(1))/int(numRuns)

  #sendNum_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),SendNum,\d*,(\d*),(\d*),.*')
  #sendNum_search = sendNum_regex.search(log_data)
  #if sendNum_search is not None:
    #sendNum_total = float(sendNum_search.group(1))/int(numRuns)

  ## Get Graph_init, HG_init, total
  timer_graph_init_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),TIMER_GRAPH_INIT,' + re.escape(numThreads) + r',(\d*),(\d*).*')
  timer_hg_init_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),TIMER_HG_INIT,' + re.escape(numThreads) + r',(\d*),(\d*).*')
  timer_total_regex = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,\(NULL\),TIMER_TOTAL,' + re.escape(numThreads) + r',(\d*),(\d*).*')


  timer_graph_init = timer_graph_init_regex.search(log_data)
  timer_hg_init = timer_hg_init_regex.search(log_data)
  timer_total = timer_total_regex.search(log_data)

  if timer_graph_init is not None:
    graph_init_time = float(timer_graph_init.group(1))
    graph_init_time /= divisor
    graph_init_time = round(graph_init_time, 0)

  if timer_hg_init is not None:
    hg_init_time = float(timer_hg_init.group(1))
    hg_init_time /= divisor
    hg_init_time = round(hg_init_time, 0)

  if timer_total is not None:
    total_time = float(timer_total.group(1))
    total_time /= divisor
    total_time = round(total_time, 0)

  ## Get Commits, Conflicts, Iterations, Pushes for worklist versions:
  commits_search = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,(?i)' + re.escape(benchmark) + '\w*,Commits,' + re.escape(numThreads) + r',(\d*),(\d*).*').search(log_data)
  conflicts_search = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,(?i)' + re.escape(benchmark) + r'\w*,Conflicts,' + re.escape(numThreads) + r',(\d*),(\d*).*').search(log_data)
  iterations_search = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,(?i)' + re.escape(benchmark) + r'\w*,Iterations,' + re.escape(numThreads) + r',(\d*),(\d*).*').search(log_data)
  pushes_search = re.compile(r'\[' + re.escape(forHost) + r'\]STAT,(?i)' + re.escape(benchmark) + r'\w*,Pushes,' + re.escape(numThreads) + r',(\d*),(\d*).*').search(log_data)

  commits    = 0
  conflicts  = 0
  iterations = 0
  pushes     = 0
  if commits_search is not None:
    commits = int(commits_search.group(1))
    commits /= int(numRuns)
  if conflicts_search is not None:
    conflicts = int(conflicts_search.group(1))
    conflicts /= int(numRuns)
  if iterations_search is not None:
    iterations = int(iterations_search.group(1))
    iterations /= int(numRuns)
  if pushes_search is not None:
    pushes = int(pushes_search.group(1))
    pushes /= int(numRuns)


  print mean_time
  #return mean_time,graph_init_time,hg_init_time,total_time,sync_pull_avg_time_total,sync_push_avg_time_total,recvNum_total,recvBytes_total,sendNum_total,sendBytes_total,commits,conflicts,iterations, pushes
  #return mean_time,graph_init_time,hg_init_time,total_time,extract_avg_time_total,set_avg_time_total,sync_pull_avg_time_total,sync_push_avg_time_total,num_iterations,commits,conflicts,iterations, pushes
  return mean_time


def sendRecv_bytes_all(fileName, benchmark, total_hosts, numRuns, numThreads):
  sendBytes_list = [0]*256 #Max host number is 256
  recvBytes_list = [0]*256 #Max host number is 256

  log_data = open(fileName).read()

  ## sendBytes and recvBytes.
  total_SendBytes = 0;
  for host in range(0,int(total_hosts)):
    sendBytes_regex = re.compile(r'\[' + re.escape(str(host)) + r'\]STAT,\(NULL\),SendBytes,\d*,(\d*),(\d*),.*')
    sendBytes_search = sendBytes_regex.search(log_data)
    if sendBytes_search is not None:
      sendBytes_list[host] = float(sendBytes_search.group(1))/int(numRuns)

  total_SendBytes = sum(sendBytes_list)

  total_RecvBytes = 0;
  for host in range(0,int(total_hosts)):
    recvBytes_regex = re.compile(r'\[' + re.escape(str(host)) + r'\]STAT,\(NULL\),RecvBytes,\d*,(\d*),(\d*),.*')
    recvBytes_search = recvBytes_regex.search(log_data)
    if recvBytes_search is not None:
       recvBytes_list[host] = float(recvBytes_search.group(1))/int(numRuns)

  total_RecvBytes = sum(recvBytes_list)
  return total_SendBytes, sendBytes_list



def sendBytes_syncOnly(fileName, benchmark, total_hosts, numRuns, numThreads):
  sendBytes_total_list = [0]*256 #Max host number is 256
  sendBytes_pull_sync_list = [0]*256 #Max host number is 256
  sendBytes_push_sync_list = [0]*256 #Max host number is 256
  sendBytes_pull_sync_reply_list = [0]*256 #Max host number is 256

  log_data = open(fileName).read()

  ## sendBytes from sync_pull.
  total_SendBytes_pull_sync = 0;
  for host in range(0,int(total_hosts)):
    sendBytes_sync_pull_regex = re.compile(r'\[' + re.escape(str(host)) + r'\]STAT,\(NULL\),SEND_BYTES_SYNC_PULL_(?i)'+ re.escape(benchmark) + r'_0_\d*,\d*,(\d*),(\d*),.*')
    sendBytes_sync_pull_lines = re.findall(sendBytes_sync_pull_regex, log_data)
    print sendBytes_sync_pull_lines

    if len(sendBytes_sync_pull_lines) > 0:
      sendBytes_pull_sync_list[host] = float(sendBytes_sync_pull_lines[0][0]) * len(sendBytes_sync_pull_lines)
      sendBytes_total_list[host] += sendBytes_pull_sync_list[host]
      print "-------> : ", host , " val : " , sendBytes_pull_sync_list[host]

  total_SendBytes_pull_sync = sum(sendBytes_pull_sync_list)

  ## sendBytes from sync_pull_reply.
  total_SendBytes_pull_reply = 0;
  for host in range(0,int(total_hosts)):
    sendBytes_sync_pull_reply_regex = re.compile(r'\[' + re.escape(str(host)) + r'\]STAT,\(NULL\),SEND_BYTES_SYNC_PULL_REPLY_(?i)'+ re.escape(benchmark) + r'_0_\d*,\d*,(\d*),(\d*),.*')
    sendBytes_sync_pull_reply_lines = re.findall(sendBytes_sync_pull_reply_regex, log_data)
    print sendBytes_sync_pull_reply_lines

    if len(sendBytes_sync_pull_reply_lines) > 0:
      sendBytes_pull_sync_reply_list[host] = float(sendBytes_sync_pull_reply_lines[0][0]) * len(sendBytes_sync_pull_reply_lines)
      sendBytes_total_list[host] += sendBytes_pull_sync_reply_list[host]
      #print "-------> : ", host , " val : " , sendBytes_pull_sync_reply_list[host]

  total_SendBytes_pull_reply = sum(sendBytes_pull_sync_reply_list)

  #[2]STAT,(NULL),SEND_BYTES_SYNC_PUSH_BFS_0_0,15,33738828,33738828,0,0,0,0,0,0,0,0,0,0,0,0,0,0
   ## sendBytes from sync_push.
  total_SendBytes_push_sync = 0;
  for host in range(0,int(total_hosts)):
    sendBytes_sync_push_regex = re.compile(r'\[' + re.escape(str(host)) + r'\]STAT,\(NULL\),SEND_BYTES_SYNC_PUSH_(?i)'+ re.escape(benchmark) + r'_0_\d*,\d*,(\d*),(\d*),.*')
    sendBytes_sync_push_lines = re.findall(sendBytes_sync_push_regex, log_data)
    print sendBytes_sync_push_lines

    if len(sendBytes_sync_push_lines) > 0:
      sendBytes_push_sync_list[host] = float(sendBytes_sync_push_lines[0][0]) * len(sendBytes_sync_push_lines)
      sendBytes_total_list[host] += sendBytes_push_sync_list[host]
      #print "-------> : ", host , " val : " , sendBytes_push_sync_list[host]

  total_SendBytes_push_sync = sum(sendBytes_push_sync_list)

  total_SendBytes = total_SendBytes_pull_sync + total_SendBytes_pull_reply + total_SendBytes_push_sync

  return total_SendBytes, total_SendBytes_pull_sync, total_SendBytes_pull_reply, total_SendBytes_push_sync, sendBytes_total_list


def build_master_ghost_matrix(fileName, benchmark, partition, total_hosts, numRuns, numThreads):
  #[1]STAT,(NULL),GhostNodes_from_1,15,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
  log_data = open(fileName).read()
  if partition == "edge-cut":
    GhostNodes_array = numpy.zeros((int(total_hosts), int(total_hosts)))
    for host in range(0, int(total_hosts)):
      #(NULL),0 , GhostNodes_from_1,3,0,45865
      #ghost_from_re = re.compile(r'\[' + re.escape(str(host)) + r'\]STAT,\(NULL\),GhostNodes_from_(\d*),\d*,(\d*),.*')
      ghost_from_re = re.compile(r'\(NULL\),\d* , GhostNodes_from_(\d*),' + re.escape(str(host)) + r',\d*,(\d*)')
      ghost_from_lines = re.findall(ghost_from_re, log_data)
      if(len(ghost_from_lines) > 0):
        for line in ghost_from_lines:
          GhostNodes_array[host][int(line[0])] = int(line[1])
    return GhostNodes_array
  #[1]STAT,(NULL),SLAVE_NODES_FROM_0,15,21693895,21693895,0,0,0,0,0,0,0,0,0,0,0,0,0,0
  elif partition == "vertex-cut" or partition == "vertex-cut-balanced":
    SlaveNodes_array = numpy.zeros((int(total_hosts), int(total_hosts)))
    for host in range(0, int(total_hosts)):
      slave_from_re = re.compile(r'\[' + re.escape(str(host)) + r'\]STAT,\(NULL\),SLAVE_NODES_FROM_(\d*),\d*,(\d*),.*')
      slave_from_lines = re.findall(slave_from_re, log_data)
      if(len(slave_from_lines) > 0):
        for line in slave_from_lines:
          SlaveNodes_array[host][int(line[0])] = int(line[1])
    return SlaveNodes_array


#[0]STAT,(NULL),SYNC_PULL_BARRIER_BFS_0_1,15,992,992,0,0,0,0,0,0,0,0,0,0,0,0,0,0
#[0]STAT,(NULL),SYNC_PULL_BARRIER_BFS_0_2,15,538,538,0,0,0,0,0,0,0,0,0,0,0,0,0,0
#[0]STAT,(NULL),SYNC_PULL_BARRIER_BFS_0_3,15,1408,1408,0,0,0,0,0,0,0,0,0,0,0,0,0,0
#[0]STAT,(NULL),SYNC_PULL_BARRIER_BFS_1_1,15,1458,1458,0,0,0,0,0,0,0,0,0,0,0,0,0,0
#[0]STAT,(NULL),SYNC_PULL_BARRIER_BFS_1_2,15,1568,1568,0,0,0,0,0,0,0,0,0,0,0,0,0,0
#[0]STAT,(NULL),SYNC_PULL_BARRIER_BFS_1_3,15,2766,2766,0,0,0,0,0,0,0,0,0,0,0,0,0,0
def time_at_barrier(fileName, benchmark, total_hosts, numRuns, numThreads):
  log_data = open(fileName).read()
  thousand = 1000.0
  sync_pull_barrier_avg_time_total = [0.0]*256
  sync_pull_avg_time_total = [0.0]*256

  for host in range(0, int(total_hosts)):
      for i in range(0, int(numRuns)):
        # find sync_pull
        sync_pull_barrier_regex = re.compile(r'\[' + re.escape(str(host)) + r'\]STAT,\(NULL\),SYNC_PULL_BARRIER_(?i)' + re.escape(benchmark) + r'\w*_' + re.escape(str(i)) + r'_(\d*),\d*,(\d*),(\d*).*')
        sync_pull_barrier_lines = re.findall(sync_pull_barrier_regex, log_data)
        num_iterations = len(sync_pull_barrier_lines);
        for j in range (0, len(sync_pull_barrier_lines)):
          sync_pull_barrier_avg_time_total[host] += float(sync_pull_barrier_lines[j][2])

      sync_pull_barrier_avg_time_total[host] /= int(numRuns)
      sync_pull_barrier_avg_time_total[host] /= thousand

  for host in range(0, int(total_hosts)):
      for i in range(0, int(numRuns)):
        # find sync_pull
        sync_pull_regex = re.compile(r'\[' + re.escape(str(host)) + r'\]STAT,\(NULL\),SYNC_PULL_(?i)' + re.escape(benchmark) + r'\w*_' + re.escape(str(i)) + r'_(\d*),\d*,(\d*),(\d*).*')
        sync_pull_lines = re.findall(sync_pull_regex, log_data)
        num_iterations = len(sync_pull_lines);
        for j in range (0, len(sync_pull_lines)):
          sync_pull_avg_time_total[host] += float(sync_pull_lines[j][2])

      sync_pull_avg_time_total[host] /= int(numRuns)
      sync_pull_avg_time_total[host] /= thousand

  print sync_pull_barrier_avg_time_total
  print sync_pull_avg_time_total


#63719d90-126e-4bdb-87d2-b7d878a23abc,(NULL),0 , CommandLine,0,0,/work/02982/ggill0/Distributed_latest/build_dist_hetero/release_new_gcc/exp/apps/compiler_outputs/bfs_push-topological_edge-cut /scratch/01131/rashid/inputs/rmat16-2e28-a=0.57-b=0.19-c=0.19-d=0.05.rgr -srcNodeId=155526494 -maxIterations=10000 -verify=0 -t=15
#63719d90-126e-4bdb-87d2-b7d878a23abc,(NULL),0 , Threads,0,0,15
#63719d90-126e-4bdb-87d2-b7d878a23abc,(NULL),0 , Hosts,0,0,4
#63719d90-126e-4bdb-87d2-b7d878a23abc,(NULL),0 , Runs,0,0,3

def get_basicInfo(fileName, get_devices):

  hostNum_regex = re.compile(r'.*,\(NULL\),0\s,\sHosts,0,0,(\d*)')
  cmdLine_regex = re.compile(r'.*,\(NULL\),0\s,\sCommandLine,0,0,(.*)')
  threads_regex = re.compile(r'.*,\(NULL\),0\s,\sThreads,0,0,(\d*)')
  runs_regex = re.compile(r'.*,\(NULL\),0\s,\sRuns,0,0,(\d*)')

  log_data = open(fileName).read()

  hostNum    = ''
  cmdLine    = ''
  threads    = ''
  runs       = ''
  benchmark  = ''
  algo_type  = ''
  cut_type   = ''
  input_graph = ''

  hostNum_search = hostNum_regex.search(log_data)
  if hostNum_search is not None:
    hostNum = hostNum_search.group(1)

  cmdLine_search = cmdLine_regex.search(log_data)
  if cmdLine_search is not None:
    cmdLine = cmdLine_search.group(1)

  threads_search = threads_regex.search(log_data)
  if threads_search is not None:
    threads = threads_search.group(1)

  runs_search    = runs_regex.search(log_data)
  if runs_search is not None:
    runs = runs_search.group(1)

  split_cmdLine_algo = cmdLine.split()[0].split("/")[-1].split("_")
  benchmark, algo_type, cut_type =  split_cmdLine_algo

  split_cmdLine_input = cmdLine.split()[1].split("/")
  input_graph = split_cmdLine_input[-1]

  devices = ''
  if get_devices:
    split_cmdLine_devices = cmdLine.split()[3].split("=")
    if split_cmdLine_devices[0] == '-pset':
      devices = split_cmdLine_devices[-1]
      cpus = devices.count('c')
      gpus = devices.count('g')
      if gpus == 0:
        devices = str(cpus) + " CPU"
      elif cpus == 0:
        devices = str(gpus) + " GPU"
      else:
        devices = str(cpus) + " CPU + " + str(gpus) + " GPU"

  return hostNum, cmdLine, threads, runs, benchmark, algo_type, cut_type, input_graph, devices

def format_str(col):
  max_len = 0
  for c in col:
    if max_len < len(str(c)):
      max_len = len(str(c))
  return max_len

def main(argv):
  inputFile = ''
  forHost = '0'
  outputFile = 'LOG_output.csv'
  time_unit = 'seconds'
  get_devices = False
  try:
    opts, args = getopt.getopt(argv,"hi:n:o:md",["ifile=","node=","ofile=","milliseconds","devices"])
  except getopt.GetoptError:
    print 'abelian_log_parser.py -i <inputFile> [-o <outputFile> -n <hostNumber 0 to hosts-1> --milliseconds --devices]'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'abelian_log_parser.py -i <inputFile> [-o <outputFile> -n <hostNumber 0 to hosts-1> --milliseconds --devices]'
      sys.exit()
    elif opt in ("-i", "--ifile"):
      inputFile = arg
    elif opt in ("-n", "--node"):
      forHost = arg
    elif opt in ("-o", "--ofile"):
      outputFile = arg
    elif opt in ("-m", "--milliseconds"):
      time_unit = 'milliseconds'
    elif opt in ("-d", "--devices"):
      get_devices = True

  if inputFile == '':
    print 'abelian_log_parser.py -i <inputFile> [-o <outputFile> -n <hostNumber 0 to hosts-1> --milliseconds --devices]'
    sys.exit(2)

  print 'Input file is : ', inputFile
  print 'Output file is : ', outputFile
  print 'Data for host : ', forHost

  hostNum, cmdLine, threads, runs, benchmark, algo_type, cut_type, input_graph, devices = get_basicInfo(inputFile, get_devices)

  #shorten the graph names:
  if input_graph == "twitter-ICWSM10-component_withRandomWeights.transpose.gr" or input_graph == "twitter-ICWSM10-component-transpose.gr" or input_graph == "twitter-ICWSM10-component_withRandomWeights.gr" or input_graph == "twitter-ICWSM10-component.gr":
    input_graph = "twitterIC"
  elif input_graph == "USA-road-d.USA.transpose.gr" or input_graph == "USA-road-d.USA-trans.gr" or input_graph == "USA-road-d.USA.gr":
    input_graph = "road-USA"
  elif input_graph == "rmat16-2e25-a=0.57-b=0.19-c=0.19-d=.05.transpose.gr" or input_graph == "rmat16-2e25-a=0.57-b=0.19-c=0.19-d=.05.gr":
    input_graph = "rmat25"
  elif input_graph == "rmat16-2e24-a=0.57-b=0.19-c=0.19-d=.05.transpose.gr" or input_graph == "rmat16-2e24-a=0.57-b=0.19-c=0.19-d=.05.gr":
    input_graph = "rmat24"
  elif input_graph == "rmat16-2e28-a=0.57-b=0.19-c=0.19-d=0.05.trgr" or input_graph == "rmat16-2e28-a=0.57-b=0.19-c=0.19-d=0.05.rgr":
    input_graph = "rmat28"

  print 'Hosts : ', hostNum , ' CmdLine : ', cmdLine, ' Threads : ', threads , ' Runs : ', runs, ' benchmark :' , benchmark , ' algo_type :', algo_type, ' cut_type : ', cut_type, ' input_graph : ', input_graph
  if get_devices:
    print 'Devices : ', devices
  data = match_timers(inputFile, benchmark, forHost, runs, threads, time_unit)
  #total_SendBytes, sendBytes_list = sendRecv_bytes_all(inputFile, benchmark, hostNum, runs, threads)
  #total_SendBytes, total_SendBytes_pull_sync, total_SendBytes_pull_reply, total_SendBytes_push_sync, sendBytes_list = sendBytes_syncOnly(inputFile, benchmark, hostNum, runs, threads)
  print data

  output_str = benchmark + ',' + 'abelian'  + ','
  if get_devices:
    output_str += devices  + ','
  else:
    output_str += hostNum  + ',' + threads  + ','
  output_str += input_graph  + ',' + algo_type  + ',' + cut_type
  #time_at_barrier(inputFile, benchmark, forHost, runs, threads)

  #output_str = benchmark + ',' + 'abelian'  + ',' + hostNum  + ',' + threads  + ',' + input_graph  + ',' + algo_type  + ',' + cut_type

  #for d in data:
    #output_str += ','
    #output_str += str(d)
  print output_str


  header_csv_str = "benchmark,platform,"
  if get_devices:
    header_csv_str += "devices,"
  else:
    header_csv_str += "host,threads,"
  header_csv_str += "input,variant,partition,mean_time" #,graph_init_time,hg_init_time,total_time,extract_avg_time,set_avg_time,sync_pull_avg_time,sync_push_avg_time,converge_iterations,commits,conflicts,iterations,pushes,total_sendBytes, total_sendBytes_pull_sync, total_sendBytes_pull_reply, total_sendBytes_push_sync"

  #for i in range(0,256):
    #header_csv_str += ","
    #header_csv_str += ("SB_" + str(i))

  header_csv_list = header_csv_str.split(',')
  #if outputFile is empty add the header to the file
  try:
    if os.path.isfile(outputFile) is False:
      fd_outputFile = open(outputFile, 'wb')
      wr = csv.writer(fd_outputFile, quoting=csv.QUOTE_NONE, lineterminator='\n')
      wr.writerow(header_csv_list)
      fd_outputFile.close()
      print "Adding header to the empty file."
    else:
      print "outputFile : ", outputFile, " exists, results will be appended to it."
  except OSError:
    print "Error in outfile opening\n"

  data_list = [data] #list(data)
  #data_list.extend((total_SendBytes, total_SendBytes_pull_sync, total_SendBytes_pull_reply, total_SendBytes_push_sync))
  complete_data = output_str.split(",") + data_list #+ list(sendBytes_list)
  fd_outputFile = open(outputFile, 'a')
  wr = csv.writer(fd_outputFile, quoting=csv.QUOTE_NONE, lineterminator='\n')
  wr.writerow(complete_data)
  fd_outputFile.close()

'''
  ## Write ghost and slave nodes to a file.
  ghost_array = build_master_ghost_matrix(inputFile, benchmark, cut_type, hostNum, runs, threads)
  ghostNodes_file = outputFile + "_" + cut_type
  fd_ghostNodes_file = open(ghostNodes_file, 'ab')
  fd_ghostNodes_file.write("\n--------------------------------------------------------------\n")
  fd_ghostNodes_file.write("\nHosts : " + hostNum + "\nInputFile : "+ inputFile + "\nBenchmark: " + benchmark + "\nPartition: " + cut_type + "\n\n")
  numpy.savetxt(fd_ghostNodes_file, ghost_array, delimiter=',', fmt='%d')
  fd_ghostNodes_file.write("\n--------------------------------------------------------------\n")
  fd_ghostNodes_file.close()
'''

if __name__ == "__main__":
  main(sys.argv[1:])

