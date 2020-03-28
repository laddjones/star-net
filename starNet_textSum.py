import socket
import sys
import threading
try: 
    import queue
except ImportError:
    import Queue as queue
import time
import select
from decimal import Decimal
import copy
import inspect
import base64
import datetime

#new_univser
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
import bs4 as BeautifulSoup
import urllib.request  

# command line:
# python ./star-node.py LaddsNode 3000 0 0 1

# command line: star-node <name> <local-port> <PoC-address> <PoC port> <N>
#	<name>: an ASCII string (Min: 1 character, Max: 16 characters) that names that star-node
#	<local-port>: the UDP port number that this star-node should use (for peer discovery)
#	<PoC-address>: the host-name of the PoC for this star-node. Set to 0 if this star-node does not have a PoC
#	<Poc-port>: the UDP port number of the PoC for this star-node. Set to 0 if this start-node does not have a PoC
#	<N>: the maximum number of star-nodes

# star_net laddjones$ python ./star-node.py LaddsNode 3000 128.61.30.128 30001 2

#new_universe
date_cur = datetime.datetime.today()
date_cur = str(date_cur) + ".txt"
f = open(date_cur, "w+")
f.write("")
f.close()

# global variables 
peerCheck = 0
starName = "NodeWithoutName"
starAddr = socket.gethostname()
starPort = 0
starPoCAddr = "0"
starPoCPort = 0
N_nodes = 0

hub_flag = 0
message_rec_flag = 0

_lock_ = threading.Lock()

time_out = 0.0

disconnect = 0

sentTime = ""
# N - 1
rtt_calc_list = []
waitingRes = 0
waitingResSum = 0
rtt_indv_time = 0.0
my_rtt_sum = 0.0
rec_rtt_sum = 0.0
# N
rtt_sum_list = []

loc_list_flag = [[]]
loc_list_flagONL = []

hub_tuple = ("","")
hub_flag = 0

itself_hub_ac = 0

need_to_print = 0

keep_alive_flag = 0

network_already_live = 0

hold_for_print = 0

rtt_list_for_user = []


time_first_discover = ""
time_first_node_die = ""
time_rtt_requests = ""
time_rtt_respnses = ""
time_rtt_sum_values = ""
time_rtt_sum_other_nodes = ""
time_hub_sections = ""
time_messages_sent = ""
time_forwarded_messages = ""
time_messages_received = ""
time_retransmitted_messages = ""
time_nodes_disconnect = ""
time_youself_disconnect = ""

peer_disc_fin_flag = 0
go_time = 0
beut_address = []
disc_list_fun = []

the_flag = 0

file_spread_flag = 0

# here we can add to these methods to check numbers or names etc (currently not using either)
def is_valid_number(input):
	try:
		float(input)
		return True
	except ValueError:
		return False
def is_valid_name(input):
	return True

# breaking up command line into individual variables (if confused, look at the command line explanation above)
try:
	starName = sys.argv[1]
	starPort = int(sys.argv[2])
	starPoCAddr = socket.gethostname()
	starPoCPort = int(sys.argv[4])
	print ("howd it ever work")
	N_nodes = int(sys.argv[5])
	print ("")
	print ("starName: " + str(starName)) 
	print ("starPort: " + str(starPort)) 
	print ("starPoCAddr: " + str(starPoCAddr))
	print ("starPoCPort: " + str(starPoCPort))
	print ("Nnodes: " + str(N_nodes)) 
except:
	print ("invalid input, bye")


# the address and port # of this star-node
loc_serv_addr = (socket.gethostname(), starPort)
# the address and port # of this star-node's PoC

poc_serv_addr = (starPoCAddr, starPoCPort)

#new_universe
def _create_dictionary_table(text_string):
   
    #removing stop words
    stop_words = set(stopwords.words("english"))
    
    words = word_tokenize(text_string)
    
    #reducing words to their root form
    stem = PorterStemmer()
    
    #creating dictionary for the word frequency table
    frequency_table = dict()
    for wd in words:
        wd = stem.stem(wd)
        if wd in stop_words:
            continue
        if wd in frequency_table:
            frequency_table[wd] += 1
        else:
            frequency_table[wd] = 1

    return frequency_table


def _calculate_sentence_scores(sentences, frequency_table):   

    #algorithm for scoring a sentence by its words
    sentence_weight = dict()

    for sentence in sentences:
        sentence_wordcount = (len(word_tokenize(sentence)))
        sentence_wordcount_without_stop_words = 0
        for word_weight in frequency_table:
            if word_weight in sentence.lower():
                sentence_wordcount_without_stop_words += 1
                if sentence[:7] in sentence_weight:
                    sentence_weight[sentence[:7]] += frequency_table[word_weight]
                else:
                    sentence_weight[sentence[:7]] = frequency_table[word_weight]

        sentence_weight[sentence[:7]] = sentence_weight[sentence[:7]] / sentence_wordcount_without_stop_words

       

    return sentence_weight

def _calculate_average_score(sentence_weight):
   
    #calculating the average score for the sentences
    sum_values = 0
    for entry in sentence_weight:
        sum_values += sentence_weight[entry]

    #getting sentence average value from source text
    average_score = (sum_values / len(sentence_weight))

    return average_score

def _get_article_summary(sentences, sentence_weight, threshold):
    sentence_counter = 0
    article_summary = ''

    for sentence in sentences:
        if sentence[:7] in sentence_weight and sentence_weight[sentence[:7]] >= (threshold):
            article_summary += " " + sentence
            sentence_counter += 1

    return article_summary

def _run_article_summary(article):
    
    #creating a dictionary for the word frequency table
    #print (article)
    frequency_table = _create_dictionary_table(article)

    #tokenizing the sentences
    sentences = sent_tokenize(article)

    #algorithm for scoring a sentence by its words
    sentence_scores = _calculate_sentence_scores(sentences, frequency_table)

    #getting the threshold
    threshold = _calculate_average_score(sentence_scores)

    #producing the summary
    article_summary = _get_article_summary(sentences, sentence_scores, 1.5 * threshold)

    return  article_summary
# end new_universe

# takes a whole package and returns pakg list form (everything after the @)
# sendPort: remember the which port the data receive from.
def at_break(data):
	newDiscList = ""
	sendPort = 0
	flag = 0
	for i in range (len(data)):
		if flag == 1:
			newDiscList = data[i:]
			break
		if data[i:i+1] == "@":
			j = i
			while (data[j-1:j] != "*"):
				j = j -1;
			sendPort = data[j:i]
			flag = 1
	return sendPort, newDiscList

#takes in pakg_list and returns a list containing lists of address and port
#pakg_list is: address, port, address, port, ...
def disc_list_break(pakg_list):
	return_list = []
	info = ""
	count = 0
	sub_list = []
	i = 0
	while i < len(pakg_list):
		while pakg_list[i:i+1] != ",":
			info = info + str(pakg_list[i:i+1])
			i = i + 1
		count = count + 1
		i = i + 1
		if count == 2:
			sub_list.append(info) #now sublist has both address and port
			return_list.append(sub_list)
			sub_list = []
			count = 0
			info = ""
		else:
			sub_list.append(info)
			info = ""
	return return_list

# important
disc_list_pakg = starAddr + "," + str(starPort) + ","
disc_list = disc_list_break(disc_list_pakg) # [["loc address", "port"]]
nodes_alive = []


def compare_lists(comp_list):
	global disc_list
	global disc_list_pakg

	newList = copy.deepcopy(disc_list)
	flag = 0
	i = 0
	l = 0
	while i < len(comp_list):
		while l < len(disc_list):
			if comp_list[i][0] == disc_list[l][0] and comp_list[i][1] == disc_list[l][1]:
				flag = 1
			l = l + 1
		if flag == 0:
			newList.append(comp_list[i])
			disc_list_pakg = disc_list_pakg + comp_list[i][0] + "," + comp_list[i][1] + ","
		flag = 0
		l = 0
		i = i + 1
	return newList

def get_rtt_calc():
	# N - 1
	global rtt_calc_list
	global my_rtt_sum
	# N
	global rtt_sum_list
	global rtt_indv_time
	global waitingRes
	global sentTime

	global nodes_alive
	global rtt_list_for_user

	global time_rtt_sum_values

	# send rtt packets and get rtt times,
	# add up your rtt times and get my_rtt_calc number

	udpSocketRTTcalc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rtt_calc_list = []
	for i in nodes_alive:
		#print "@@@@@@@@@@@@@@ 4"
		if i[0] != starAddr or int(i[1]) != starPort:
			address = (i[0], int(i[1]))
			try:
				ackCheckRTT = 0
				#print "@@@@@@@@@@@@@@ 5"
				while ackCheckRTT == 0:
					startTime = time.time()
					rttCalcPacket = "0100" + "*" + str(starAddr) + "*" + str(starPort) + "@" + str(startTime)
					sent = udpSocketRTTcalc.sendto(rttCalcPacket.encode(), address)
					waitTime0 = time.time()
					#print "@@@@@@@@@@@@@@ 6"
					while waitingRes == 0 and (time.time() - waitTime0 < 1.0):
						#print "@@@@@@@@@@@@ 6.1"
						wait = True
					if waitingRes != 0:
						#print "@@@@@@@@@@@@@@ 7"
						if str(sentTime) == str(startTime):
							#print "@@@@@@@@@@@@@@ 8"
							rtt_calc_list.append(rtt_indv_time)
							ackCheckRTT = 1
						waitingRes = 0
						waitTime = time.time()
						while time.time() - waitTime < 1.0:
								wait = True
			except:
				print ("error")
	#print "@@@@@@@@@@@@@@ 9"
	rtt_list_for_user = rtt_calc_list
	my_rtt_sum = 0.0
	#print "@@@@@@@@@@@@@@ 10"
	for i in rtt_calc_list:
		my_rtt_sum = my_rtt_sum + i
	#print "@@@@@@@@@@@@@@ 11"
	time_rtt_sum_values = time_rtt_sum_values + "New RTT sum value computed at: " + str(time.time()) + ", "

def get_rtt_sum():
		# N - 1
	global rtt_calc_list
	global my_rtt_calc
	global my_rtt_sum
	# N
	global rtt_sum_list
	global rtt_indv_time
	global waitingResSum
	global sentTime
	global rec_rtt_sum

	global nodes_alive

	global hub_tuple

	global hub_flag

	global time_hub_sections

	# send rtt packets and get rtt times,
	# add up your rtt times and get my_rtt_calc number

	udpSocketRTTsum = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	rtt_sum_list = []
	#print "@@@@@@@@@@@@@@ 12"
	for i in nodes_alive:
		if i[0] != starAddr or int(i[1]) != starPort:
			address = (i[0], int(i[1]))
			try:
				#print "@@@@@@@@@@@@@@ 13"
				waitingResSum = 0
				while waitingResSum == 0:
					#print "@@@@@@@@@@@@@@ 14"
					rttSUMPacket = "0110" + "*" + str(starAddr) + "*" + str(starPort) + "@"
					sent = udpSocketRTTsum.sendto(rttSUMPacket.encode(), address)
					waitTime = time.time()
					while time.time() - waitTime < 1.0:
							wait = True
				rtt_sum_list.append([i[0], i[1], rec_rtt_sum])
			except:
				print ("error")
	rtt_sum_list.append([starAddr, str(starPort), my_rtt_sum])
	min_value = 1234567890.0
	#print "@@@@@@@@@@@@@@ 15"
	for i in rtt_sum_list:
		if i[2] < min_value:
			min_value = i[2]
			hub_tuple = (i[0], str(i[1]))
	#print "@@@@@@@@@@@@@@ 16"
	time_hub_sections = time_hub_sections + "Updated hub at time: " + str(time.time()) + ", "
	hub_flag = 1


def send_packet(id, my_addr, my_port, send_to_addr, send_to_port, newList_pakg):
	serv_addr = (send_to_addr, int(send_to_port))
	# create udp socket
	updSocketSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		#       id  * this sn address  * this sn port @ disc_list	 				
		packToSend = id + "*" + my_addr + "*" + str(my_port) + "@" + newList_pakg
		sent = updSocketSend.sendto(packToSend.encode(), serv_addr)
	except:
		print ("sending stuff broke")
	updSocketSend.close()

disp_flag = 0
address_pass_hub = []
data_message_pass_hub = ""
# helper function to get the right port number from the received package data
# 0000*ipsec-143-215-28-37.vpn.gatech.edu*3300@ipsec-143-215-28-37.vpn.gatech.edu,3300,
def hub_sep_send():
	global disc_list
	global disc_list_pakg
	global starAddr
	global starPort
	global loc_serv_addr
	global peerCheck
	global sentTime
	global rtt_indv_time
	global waitingRes
	global waitingResSum
	global my_rtt_sum
	global rec_rtt_sum
	global message_rec_flag
	global nodes_alive
	global loc_list_flag	
	global disp_flag
	global address_pass_hub
	global data_message_pass_hub
	global loc_list_flagONL

	global peer_disc_fin_flag
	global go_time
	global beut_address
	global disc_list_fun

	global time_forwarded_messages

	global the_flag

	global file_spread_flag

	updSocketGOTIME = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#imp_switch = 0

	#while imp_switch == 0:
		# !! could move this whole block into disp_flag section bellow

	#imp_switch = 1
	run_num = 0
	
	while True:
		while go_time == 0 and len(disc_list) < N_nodes:
			#print "what"
			wait = True
		#while (disc_list < N_nodes or run_one == 0):
		#if True == True:
		run_num = run_num + 1
		if go_time == 1:
			for i in disc_list_fun:
				# if ((not equal to sender) and (not equal to itself))
				peer_disc_fin_flag = 0
				#print disc_list_fun
				#print i
				while (peer_disc_fin_flag == 0):

					#print "_peer_disc_fin_flag_"
					#print peer_disc_fin_flag
					#print "##################"
					#print i[0]
					#print starAddr
					#print i[1]
					#print str(starPort)
					#print i[0]
					#print socket.gethostbyaddr(beut_address[0])[0]
					#print i[1]
					#print str(beut_address[1])
					## something has got to be up with this if statement 
					#might have to undo the line below
					if (i[1] != str(starPort)) and (str(i[1]) != str(beut_address[1])):
						#print ""
						#print "_in_"
						try:
							#       id  * this sn address  * this sn port @ disc_list	 				
							packToSend = "0000" + "*" + starAddr + "*" + str(starPort) + "@" + disc_list_pakg
							#print ""
							#print "packet to send"
							#print packToSend
							#print 
							sent = updSocketGOTIME.sendto(packToSend.encode(), (i[0], int(i[1])))
						except:
							print ("sending stuff broke")
					else:
						peer_disc_fin_flag = 1
					#print "_out_"
					discWait = time.time()
					while time.time() - discWait < .1:
						wait = True
			go_time = 0
		if len(disc_list) == N_nodes:
			the_flag = 1
			break

	updSocketGOTIME.close()


	# go time ---------------- go time -------------------- go time -------------

	#print "DONE< OUT< FINISHED"

	updSocketHUB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	while disconnect == 0:
		disp_flag = 0
		while disp_flag == 0:
			wait = True

		data_message = data_message_pass_hub
		address = address_pass_hub
		#print "address !!!!!!!!!!!!"
		#print address
		for i in nodes_alive:
			time_forwarded_messages = time_forwarded_messages + "Hub (you) forwarded message at: " + str(time.time()) + ", "
			loc_list_flag = [[]]
			if (i[1] != str(starPort)) and (i[1] != str(address[1])):
				while i != loc_list_flag:
					if file_spread_flag == 0:
						data_message_spread = "1010" + "*" + str(starAddr) + "*" + str(starPort) + "@" + data_message
						sent = updSocketHUB.sendto(data_message_spread.encode(), (i[0], int(i[1])))
					else:
						data_message_spread = "1100" + "*" + str(starAddr) + "*" + str(starPort) + "@" + data_message
						sent = updSocketHUB.sendto(data_message_spread.encode(), (i[0], int(i[1])))
					bs = time.time()
					while time.time() - bs < 1.0:
						wait = True
				loc_list_flag = [[]]
				loc_list_flagONL = []
		file_spread_flag = 0
		disp_flag = 0


def server():
	global disc_list
	global disc_list_pakg
	global starAddr
	global starPort
	global loc_serv_addr
	global peerCheck
	global sentTime
	global rtt_indv_time
	global waitingRes
	global waitingResSum
	global my_rtt_sum
	global rec_rtt_sum
	global message_rec_flag
	global nodes_alive
	global loc_list_flag
	global disp_flag
	global itself_hub_ac
	global address_pass_hub
	global data_message_pass_hub
	global _lock_
	global need_to_print
	global keep_alive_flag
	global network_already_live
	global hold_for_print
	global loc_list_flagONL

	global time_first_discover
	global time_first_node_die
	global time_rtt_requests
	global time_rtt_respnses
	global time_rtt_sum_values
	global time_rtt_sum_other_nodes
	global time_hub_sections
	global time_messages_sent
	global time_forwarded_messages
	global time_messages_received
	global time_retransmitted_messages
	global time_nodes_disconnect
	global time_youself_disconnect

	global peer_disc_fin_flag
	global go_time
	global beut_address
	global disc_list_fun
	global file_spread_flag


	udpSocketListen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print ("universe >>")
	print (sys.stderr, 'My server at. host: %s, port: %s' % loc_serv_addr)
	print ("")
	udpSocketListen.bind(loc_serv_addr)
	while True:
		data, address = udpSocketListen.recvfrom(65535)

		data = data.decode()

		packetID = data[0:4]


		if packetID == "0000":
			# node received a peer discovery and will broadcast to known nodes
			if (time_first_discover == ""):
				time_first_discover = "First node discovered at: " + str(time.time())
			# breaking the received discovery list into a comparable form 
			rec_port, disc_list_pakg_rec = at_break(data)
			disc_list_rec = disc_list_break(disc_list_pakg_rec)
			# now have disc_list and disc_list_rec that can be compared
			print ("Recieved a peer discovery packet from: " + address[0] + " " + rec_port)

			address = (address[0],int(rec_port))

			new_disc_list = compare_lists(disc_list_rec)
			peerDiscACKPack = "0001" + "*" + starAddr + "*" + str(starPort) + "@" + disc_list_pakg
			sent = udpSocketListen.sendto(peerDiscACKPack.encode(), address)
			#print "sent acknowledgements back"
			#print new_disc_list
			#print disc_list
			if len(disc_list) != len(new_disc_list):
				#print "inside the diff list length"
				beut_address = address
				go_time = 1
				disc_list_fun = new_disc_list

				disc_list = new_disc_list
				# now send peer disc request to all discovered nodes if the list has any new ones (expect back to the sender (already handled above))
			

		if packetID == "0001":	
			print ("received a POC ACK")
			if (time_first_discover == ""):
				time_first_discover = "First node discovered at: " + str(time.time())		
			rec_port, new_disc_list_pakg = at_break(data)
			#print new_disc_list_pakg
			#print "star-node received a peer-discovery ACK, from address: " + address[0] + " port: " + rec_port
			new_disc_list = disc_list_break(new_disc_list_pakg)
			disc_list = compare_lists(new_disc_list)
			peer_disc_fin_flag = 1
			peerCheck = 1

		if packetID == "0010":
			#print "star-node received a keep-alive"
			rec_port, all_nodes_pakg_list = at_break(data)
			disc_list_rec = disc_list_break(all_nodes_pakg_list)
			disc_list = compare_lists(disc_list_rec)
			network_already_live = 1
			address = (address[0], int(rec_port))
			keep_alive_pac_ACK = "0011" + "*" + starAddr + "*" + str(starPort)
			sent = udpSocketListen.sendto(keep_alive_pac_ACK.encode(), address)



		if packetID == "0011":
			#print "star-node received a keep-alive ACK"
			keep_alive_flag = 1

		if packetID == "0100":
			#print "star-node received an RTT check"
			time_rtt_requests = time_rtt_requests + "Received and RTT request at time: " + str(time.time()) + ", " 
			rec_port, sentTimeVar = at_break(data)
			rttCalcACK = "0101" + "*" + str(starAddr) + "*" + str(starPort) + "@" + sentTimeVar
			address = (address[0], int(rec_port))
			sent = udpSocketListen.sendto(rttCalcACK.encode(), address)

		if packetID == "0101":
			#print "star-node received an RTT check ACK"
			time_rtt_respnses = time_rtt_respnses + "Received and RTT response at time: " + str(time.time()) + ", " 
			rec_port, sentTime = at_break(data)
			rtt_indv_time = time.time() - float(sentTime)
			
			waitingRes = 1


		if packetID == "0110":
			#print "star-node received a RTT sum request"

			rec_port, loc_nothing = at_break(data)
			if my_rtt_sum != 0:
				rttCalcACK = "0111" + "*" + str(starAddr) + "*" + str(starPort) + "@" + str(my_rtt_sum)
				address = (address[0], int(rec_port))
				sent = udpSocketListen.sendto(rttCalcACK.encode(), address)
			else:
				rttCalcACK = "1111" + "*" + str(starAddr) + "*" + str(starPort) + "@" + str(my_rtt_sum)
				address = (address[0], int(rec_port))
				sent = udpSocketListen.sendto(rttCalcACK.encode(), address)



		if packetID == "0111":
			#print "star-node received an RTT sum ACK"
			time_rtt_sum_other_nodes = time_rtt_sum_other_nodes + "Received a new RTT sum from another node at: " + str(time.time()) + ", "
			rec_port, loc_pass = at_break(data)	
			rec_rtt_sum = float(loc_pass)		
			waitingResSum = 1

		if packetID == "1111":
			#print "star-node received an RTT sum ACK but the sender wasnt ready yet"
			rec_port, loc_pass = at_break(data)	
			rec_rtt_sum = float(loc_pass)		
			waitingResSum = 0


		if packetID == "1000":
			try:
				rec_port, data_message = at_break(data)
				#print "$$$$"
				print ("star-node received message data and you are the hub")
				print ("$$$")
				print (data_message)
				print ("$$$")
				print ("** hit the enter/return button please **")
				f = open(date_cur, "a+")
				f.write(data_message)
				f.write(".")
				f.close()
				data_message_ACK = "1001" + "*" + str(starAddr) + "*" + str(starPort) + "@"
				address = (address[0], int(rec_port))
				address_pass_hub = address
				sent = udpSocketListen.sendto(data_message_ACK.encode(), address)
			
				#address_pass_hub = address
				data_message_pass_hub = data_message		
				disp_flag = 1
			except:
				print ("star-node is hub and broke when received data to spread")
					

		if packetID == "1001":
			time_messages_received = time_messages_received + "Node receivd message at: " + str(time.time()) + ", "
			print ("star-node received a message ACK")
			try:
				rec_port, loc_nothing = at_break(data)
				print ("recieved from port")
				print (rec_port)
				print ("*******************")
				loc_list_flag = [socket.gethostname(), str(rec_port)]
				#loc_list_flagONL = [address[0], str(rec_port)]
				itself_hub_ac = 1
				message_rec_flag = 1
				
			except:
				print ("ACK BROKEN")


		if packetID == "1010":
			try:
				rec_port, data_message = at_break(data)
				#print "$$$$"
				print ("star-node received message data and you are a regular node")
				print ("")
				print (data_message)
				print ("")
				print ("** hit the enter/return button please **")
				f = open(date_cur, "a+")
				f.write(data_message)
				f.write(".")
				f.close()
				data_message_ACK = "1001" + "*" + str(starAddr) + "*" + str(starPort) + "@"
				address = (address[0], int(rec_port))
				
				sent = udpSocketListen.sendto(data_message_ACK.encode(), address)
			except:
				print ("it took this long to do this... wow")

		if packetID == "1011":
			try:
				rec_port, data_file = at_break(data)
				#print "$$$$"
				print ("star-node received file data and you are the hub")
				print ("")
				print ("received a file, check directory")
				print ("")
				#write to a file
				fh = open("image_ATtime_" + str(time.time()) + ".png", "wb")
				fh.write(data_file.decode('base64'))
				fh.close()
				print ("** hit the enter/return button please **")
				data_message_ACK = "1001" + "*" + str(starAddr) + "*" + str(starPort) + "@"
				address = (address[0], int(rec_port))
				address_pass_hub = address
				sent = udpSocketListen.sendto(data_message_ACK.encode(), address)
				
				#address_pass_hub = address
				data_message_pass_hub = data_file	
				file_spread_flag = 1	
				disp_flag = 1
			except:
				print ("star-node is hub and broke when received data to spread")

		if packetID == "1100":
			#you are a regular node
			try:
				rec_port, data_file = at_break(data)
				#print "$$$$"
				print ("star-node received file data and you are a regular node")
				print ("")
				print ("received a file, check directory")
				print ("")
				#write to a file
				fh = open("image_ATtime_" + str(time.time()) + ".png", "wb")
				fh.write(data_file.decode('base64'))
				fh.close()
				print ("** hit the enter/return button please **")
				data_message_ACK = "1001" + "*" + str(starAddr) + "*" + str(starPort) + "@"
				address = (address[0], int(rec_port))
				
				sent = udpSocketListen.sendto(data_message_ACK.encode(), address)
			except:
				print ("it took this long to do this... wow")

def peer_discovery():
	global starAddr
	global starPort
	global poc_serv_addr
	global peerCheck
	global starPoCAddr
	global time_out
	global network_already_live


	time_out = time.time()

	if str(starPoCPort) == "0":
		peerCheck = 3
	else:
		# create udp socket
		udpSocketPeerDisc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		print ("universe >>")
		print (sys.stderr, 'Peer Discovery at PoC: %s, port: %s' % poc_serv_addr)
		print ("")

		while peerCheck == 0 and network_already_live == 0:
			start = - 5
			try:
				while True and peerCheck == 0 and network_already_live == 0:
					if (time.time() - start >= 5):	
						#       id  * this sn address  * this sn port @ disc_list	 				
						#print "send to my POC every 5 seconds "
						peerDiscPack = "0000" + "*" + str(starAddr) + "*" + str(starPort) + "@" + disc_list_pakg
						sent = udpSocketPeerDisc.sendto(peerDiscPack.encode(), poc_serv_addr)
						start = time.time()
			except:
				print ("peer discovery broke")
		udpSocketPeerDisc.close()
	


# have peer discovery thread be its own thread and then client and keep-alive are there own threads and start after peer discovery
def client():
	global peerCheck
	global N_nodes
	global loc_serv_addr
	global disc_list
	global disc_list_pakg
	global hub_flag
	global hub_tuple
	global message_rec_flag
	global disconnect
	global itself_hub_ac
	global need_to_print
	global time_out
	global hold_for_print
	global rtt_calc_list
	global rtt_list_for_user
	global rtt_sum_list	
	global time_first_discover
	global time_first_node_die
	global time_rtt_requests
	global time_rtt_respnses
	global time_rtt_sum_values
	global time_rtt_sum_other_nodes
	global time_hub_sections
	global time_messages_sent
	global time_forwarded_messages
	global time_messages_received
	global time_retransmitted_messages
	global time_nodes_disconnect
	global time_youself_disconnect
	global date_cur

	disconnect = 0

	log_counter = 0

	while len(disc_list) < N_nodes:
		if time.time() - time_out > 30.0:
			print ("")
			print ("**** Peer Disocvery Timed Out ****")
			break

	while len(disc_list) < N_nodes:
		wait = True

	while hub_flag == 0:
		wait = True
	uInput = ""
	# uInput stores the user's input 
	sTime = time.time()
	while time.time() - sTime < .3:
		wait = True

	while disconnect == 0:
		print ("")
		try:
			uInput = input('Star-node command: ')
		except:
			print ("ok what>.....")
		#print uInput[0:4]

		#if uInput == "$$$$":
		#	while hold_for_print == 0:
		#		wait = True
		#		print "spam"
		#	hold_for_print = 0

		retransmit_flag = 0

		data = uInput[4:]

		udpSocketClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		if uInput[0:4] == "send":
			#new_universe
			f = open(date_cur, "a+")
			f.write(uInput)
			f.write(".")
			f.close()
			time_messages_sent = time_messages_sent + "Message sent at: " + str(time.time()) + ", "
			file_flag = 0
			if uInput[0:9] == "send file":
				file_flag = 1
				#print "the file you are sending is" + uInput[10:]
				with open(uInput[10:], "rb") as imageFile:
					string_read = base64.b64encode(imageFile.read())
				#print "string_read is"
				#print string_read

			if hub_tuple == (starAddr, str(starPort)):
				nodes_alive_current = copy.deepcopy(nodes_alive)
				#print "^^^^nodes_alive^^^"
				#print nodes_alive
				for i in nodes_alive_current:
					#print "nodes to sends to_____ cur"
					#print nodes_alive_current
					#print "__________"
					if i[0] != starAddr or i[1] != str(starPort):
						#print "$$ 1here $$"
						itself_hub_ac = 0
						while itself_hub_ac == 0:
							print ("$$ 2here $$")
							if retransmit_flag == 0:
								retransmit_flag = 1
								time_retransmitted_messages = time_retransmitted_messages + "Retransmitted message at: " + str(time.time()) + ", "
							try:
								time_forwarded_messages = time_forwarded_messages + "Hub (you) forwarded message at: " + str(time.time()) + ", "
								#print "you are hub so spreadddddddd"
								if file_flag == 0:
									#print "sending message: " + data + " to address: " + i[0] + i[1]
									data_mess_packet = "1010" + "*" + str(starAddr) + "*" + str(starPort) + "@" + "received from address: " + str(starAddr) + " at port: " + str(starPort) + ", message: " + data
									sent = udpSocketClient.sendto(data_mess_packet.encode(), (i[0], int(i[1])))
								else:
									data_mess_packet = "1100" + "*" + str(starAddr) + "*" + str(starPort) + "@" + string_read
									sent = udpSocketClient.sendto(data_mess_packet.encode(), (i[0], int(i[1])))
								
								sleepTime = time.time()
								while time.time() - sleepTime < 1.5:
									wait = True
							except:
								"package sending error"
						#itself_hub_ac = 0
			else :
				#print "made it in the send"
				# need to figure out what to do if it is a file the user wants to send
				retransmit_flag = 0
				message_rec_flag = 0
				while message_rec_flag == 0:
					if retransmit_flag == 0:
						retransmit_flag = 1
						time_retransmitted_messages = time_retransmitted_messages + "Retransmitted message at: " + str(time.time()) + ", "
					try:
						#print "you are not the hub so send to hubbbbbbbbb"
						if file_flag == 0:
							data_mess_packet = "1000" + "*" + str(starAddr) + "*" + str(starPort) + "@" + "received from address: " + str(starAddr) + " at port: " + str(starPort) + ", message: " + data
							sent = udpSocketClient.sendto(data_mess_packet.encode(), (hub_tuple[0], int(hub_tuple[1])))
						else: 
							data_mess_packet = "1011" + "*" + str(starAddr) + "*" + str(starPort) + "@" + string_read
							sent = udpSocketClient.sendto(data_mess_packet.encode(), (hub_tuple[0], int(hub_tuple[1])))
						sleepTime = time.time()
						while time.time() - sleepTime < 1.5:
							wait = True
					except:
						"package sending error"
				#message_rec_flag = 0

		if uInput[0:10] == "summarize":
			f = open(date_cur)
			contents = f.read()
			f.close()
			print (contents)
			summary_results = _run_article_summary(contents)
			print (summary_results)

			time_messages_sent = time_messages_sent + "Message sent at: " + str(time.time()) + ", "
			file_flag = 0
			

			if hub_tuple == (starAddr, str(starPort)):
				nodes_alive_current = copy.deepcopy(nodes_alive)
				#print "^^^^nodes_alive^^^"
				#print nodes_alive
				for i in nodes_alive_current:
					#print "nodes to sends to_____ cur"
					#print nodes_alive_current
					#print "__________"
					if i[0] != starAddr or i[1] != str(starPort):
						#print "$$ 1here $$"
						itself_hub_ac = 0
						while itself_hub_ac == 0:
							print ("$$ 2here $$")
							if retransmit_flag == 0:
								retransmit_flag = 1
								time_retransmitted_messages = time_retransmitted_messages + "Retransmitted message at: " + str(time.time()) + ", "
							try:
								time_forwarded_messages = time_forwarded_messages + "Hub (you) forwarded message at: " + str(time.time()) + ", "
								#print "you are hub so spreadddddddd"
								if file_flag == 0:
									#print "sending message: " + data + " to address: " + i[0] + i[1]
									data_mess_packet = "1010" + "*" + str(starAddr) + "*" + str(starPort) + "@" + "received from address: " + str(starAddr) + " at port: " + str(starPort) + ", message: " + contents
									sent = udpSocketClient.sendto(data_mess_packet.encode(), (i[0], int(i[1])))
								else:
									data_mess_packet = "1100" + "*" + str(starAddr) + "*" + str(starPort) + "@" + string_read
									sent = udpSocketClient.sendto(data_mess_packet.encode(), (i[0], int(i[1])))
								
								sleepTime = time.time()
								while time.time() - sleepTime < 1.5:
									wait = True
							except:
								"package sending error"
						#itself_hub_ac = 0
			else :
				#print "made it in the send"
				# need to figure out what to do if it is a file the user wants to send
				retransmit_flag = 0
				message_rec_flag = 0
				while message_rec_flag == 0:
					if retransmit_flag == 0:
						retransmit_flag = 1
						time_retransmitted_messages = time_retransmitted_messages + "Retransmitted message at: " + str(time.time()) + ", "
					try:
						#print "you are not the hub so send to hubbbbbbbbb"
						if file_flag == 0:
							data_mess_packet = "1000" + "*" + str(starAddr) + "*" + str(starPort) + "@" + "received from address: " + str(starAddr) + " at port: " + str(starPort) + ", message: " + contents
							sent = udpSocketClient.sendto(data_mess_packet.encode(), (hub_tuple[0], int(hub_tuple[1])))
						else: 
							data_mess_packet = "1011" + "*" + str(starAddr) + "*" + str(starPort) + "@" + string_read
							sent = udpSocketClient.sendto(data_mess_packet.encode(), (hub_tuple[0], int(hub_tuple[1])))
						sleepTime = time.time()
						while time.time() - sleepTime < 1.5:
							wait = True
					except:
						"package sending error"
				#message_rec_flag = 0


		if uInput[0:12] == "show-status":
			print ("")
			print ("the alive nodes and the rtt to each")
			print (rtt_sum_list)
			print ("")
			print ("the hub_node is:")
			print (hub_tuple)
			print ("")

		if uInput[0:9] == "show-log":
			print ("")
			print ("log #" + str(log_counter) + " recorded to file in directory")
			text_file = open("output_log" + str(log_counter)+ ".txt", "w")
			text_file.write(time_first_discover + "\n")
			text_file.write(time_first_node_die + "\n")
			text_file.write(time_rtt_requests + "\n")
			text_file.write(time_rtt_sum_values + "\n")
			text_file.write(time_rtt_sum_other_nodes + "\n")
			text_file.write(time_hub_sections + "\n")
			text_file.write(time_messages_sent + "\n")
			text_file.write(time_forwarded_messages + "\n")
			text_file.write(time_messages_received + "\n")
			text_file.write(time_retransmitted_messages + "\n")
			text_file.write(time_nodes_disconnect + "\n")
			text_file.write(time_youself_disconnect + "\n")
			text_file.close()
			log_counter = log_counter + 1

		#print "what is happenign to disconioneont"
		#print uInput[0:11]
		if uInput[0:11] == "disconnect":
			disconnect = 1

def keep_alive():
	global N_nodes
	global disc_list
	global nodes_alive
	global hub_flag
	global hub_tuple
	global disconnect
	global my_rtt_sum
	global rtt_sum_list
	global keep_alive_flag
	global starAddr
	global starPort
	global rtt_calc_list
	global network_already_live

	global time_first_discover
	global time_first_node_die
	global time_rtt_requests
	global time_rtt_respnses
	global time_rtt_sum_values
	global time_rtt_sum_other_nodes
	global time_hub_sections
	global time_messages_sent
	global time_forwarded_messages
	global time_messages_received
	global time_retransmitted_messages
	global time_nodes_disconnect
	global time_youself_disconnect
	global the_flag

	while len(disc_list) < N_nodes:
		wait = True
	
	while the_flag == 0:
		wait = True

	sTime = time.time()
	while time.time() - sTime < .4:
		wait = True
	
	print ("*(*)*(*)*(*)*( disc_list )*(*)*(*)*(*)*")
	print (disc_list)
	nodes_alive = disc_list
	#print "@@@@@@@@@@@@@@ 1"
	get_rtt_calc()
	#print "@@@@@@@@@@@@@@ 2"
	get_rtt_sum()
	#print "@@@@@@@@@@@@@@ 3"

	print ("")
	print ("list of connected nodes: ")
	print (nodes_alive)
	print ("")
	print ("your rtt sum is : ")
	print (my_rtt_sum)
	print ("")
	print ("your rtt sum list is:")
	print (rtt_sum_list)
	print ("")
	print ("your hub-tuple is:")
	print (hub_tuple)
	print ("")

	# make a call to RTT calc and RTT sum to get the hub setup 
	print ("keep alive running")
	# keep alive will run and whenever a nodes dies/wakes up do RTT calc again
	while disconnect == 0:
		# keep alive will run and whenever a nodes dies/wakes up do RTT calc again
		node_die_time = time.time()
		skip_node = 0
		udpSocketKEEPALIVE = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		old_nodes_alive = nodes_alive
		new_nodes_alive = []
		new_nodes_alive.append([starAddr, str(starPort)])
		for i in disc_list:
			if i[1] != str(starPort):
				while keep_alive_flag == 0:
					if time.time() - node_die_time > 2.0:
						skip_node = 1
						keep_alive_flag = 2
					if skip_node == 0:
						keep_alive_pac = "0010" + "*" + starAddr + "*" + str(starPort) + "@" + disc_list_pakg
						sent = udpSocketKEEPALIVE.sendto(keep_alive_pac.encode(), (i[0], int(i[1])))
						wait_time = time.time()
						while time.time() - wait_time < .25:
							wait = True
				if keep_alive_flag == 1:
					new_nodes_alive.append([i[0], i[1]])
				node_die_time = time.time()
				skip_node = 0
				keep_alive_flag = 0	
		
		nodes_alive = new_nodes_alive
		#print "nodes_alive after keep_alive: "
		#print nodes_alive
		
		
		#print "old_nodes_alive ()())()()()()())()()"
		#print old_nodes_alive
		#print "nodes_alive ()())()()()()())()()"
		#print nodes_alive

		need_recalc = 0
		for i in old_nodes_alive:
			flag = 0
			for l in nodes_alive:
				if l == i:
					flag = 1
			if flag == 0:
				need_recalc = 1
				break
			flag = 0

		need_recalc2 = 0
		for i in nodes_alive:
			flag = 0
			for l in old_nodes_alive:
				if l == i:
					flag = 1
			if flag == 0:
				need_recalc2 = 1
				break
			flag = 0
	
		if need_recalc == 1 or need_recalc2 == 1:
			print ("")
			print ("************ recalculating network ************")
			if time_first_node_die == "":
				time_first_node_die = "Discovered a a node going offline at: " + str(time.time())
			#print ")( 1"
			#print my_rtt_sum

			my_rtt_sum = 0
			#print ")( 2"
			#print my_rtt_sum
			get_rtt_calc()
			hold_on = time.time()
			while time.time() - hold_on < 3.0:
				wait = True
			#print ")( 3"
			#print my_rtt_sum
			get_rtt_sum()

			#get_rtt_calc()
			#get_rtt_sum()
			print ("************ network recalculated ************")

		#print "&&& nodes_alive &&&"
		#print nodes_alive	
		#print "______hub_tuple is________"
		#print hub_tuple
		#print "- - - - - - -rtt_sum_list -- - -- - -  - -"
		#print rtt_sum_list
		keep_time = time.time()
		while time.time() - keep_time < 3.0:
			wait = True


def intel_method(value):
	if value == 1:
		server()
	if value == 2:
		peer_discovery()
	if value == 3:
		client()
	if value == 4:
		keep_alive()
	if value == 5:
		hub_sep_send()


def process_threads():
	while True:
		intel_method(threads_queue.get())
		threads_queue.task_done()


threads_queue = queue.Queue()

threads_queue.put(1)
threads_queue.put(2)
threads_queue.put(3)
threads_queue.put(4)
threads_queue.put(5)


for i in range(5):
	t = threading.Thread(target=process_threads)
	t.daemon = True
	t.start()

while disconnect == 0:
	wait = True
#start = time.time()

# python ./star-node.py LaddsNode 3001 networklab2.cc.gatech.edu 3000 3
# python ./star-node.py LaddsOtherNode 3000 0 0 3
# python ./star-node.py LaddsOtherOtherNode 3002 networklab2.cc.gatech.edu 3000 3