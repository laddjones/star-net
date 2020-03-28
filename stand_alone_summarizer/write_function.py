import datetime

print "enter text you want saved in an external file"
uInput = ""
while True:
	try:
		uInput = raw_input('Star-node command: ')
	except:
		print "ok what>....."
	
	if uInput == "exit":
		break

	date = datetime.datetime.today()
	if uInput != "":
		date = str(date) + ".txt"
		f = open(date, "w+")
		f.write(uInput)
		f.close()
		print "things were added to your file"
		uInput = ""