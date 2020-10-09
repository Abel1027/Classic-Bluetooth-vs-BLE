import simpy
import random
import os

def inquiry(env, index, blePower, finishTime, timeResolution, printLogs):
	############### Inquiry ###############
	global band24
	global collisionListBand24
	global totalCollisions24Band
	global totalEnergy24BandInquirer
	global inquiringEnd
	global afterRelayFoundTimer

	back_off = random.randint(0, 10)
	#yield env.timeout(timeResolution*back_off)
	timeSteps = 0
	advPDUCollisioned = False
	# Informs that the BLE backoff has expired (True) or not (False).
	inquirerBackOffTimeOut = True
	# Timer.
	inquirerBackOffTimer = 0
	while True:
		if inquiringEnd[index] == False:
			if inquirerBackOffTimeOut == True:
				# Advertising.
				# If timeSteps is 0-10 timeSteps or 224-234 timeSteps or 448-458 timeSteps, the inquirer 
				# sends various advertising PDU parts.
				if (timeSteps >= 0 and timeSteps <= 10) or \
					(timeSteps >= 224 and timeSteps <= 234) or \
					(timeSteps >= 448 and timeSteps <= 458):

					if timeSteps == 0 or timeSteps == 224 or timeSteps == 448:
						# Informs that the interval for advertising PDU transmission has started.
						sendFirstPDU = True

						# Informs that there are no collisions yet.
						advPDUCollisioned = False

						# The channel used for inquiring is 0, 1, or 2 (CH37, CH38, CH39), respectively.
						if timeSteps == 0: freq = 0 # CH37
						elif timeSteps == 224: freq = 1 # CH38
						elif timeSteps == 448: freq = 2 #CH39

					if sendFirstPDU == True:
						if band24[freq] != None or collisionListBand24[freq] != None:
							# Informs that a collision occurred for at least one advertising PDU part transmission.
							advPDUCollisioned = True

							# Prints logs for the inquirer including timestamp, device index, 
							# and the notification of the collision.
							if printLogs == True: print(env.now, 'us: Inquirer (' + str(index) + \
								'): Collision freq=' + str(freq))

							# Free the channel for next transmissions.
							band24[freq] = None

							# Sets the channel as a conflictive channel. Collisions will occur
							# for other devices transmitting at the same time in this channel.
							collisionListBand24[freq] = 'collision'

							# Add 1 to the number of collisions in the 2.4GHz band.
							totalCollisions24Band += 1

							# Informs that occured a collision and no signal was transmitted.
							signalTransmitted = False

							# If the advertising PDU transmission ends, informs that the interval 
							# for advertising PDU transmission has ended.
							if (timeSteps == 10 or timeSteps == 234 or timeSteps == 458): sendFirstPDU = False
						# If the channel is empty, the device can send the inquiring signal.
						else:
							# If the advertising PDU transmission ends, and if there were no collisions, informs
							# that a inquiring packet has been sent.
							if (timeSteps == 10 or timeSteps == 234 or timeSteps == 458) and advPDUCollisioned == False:
								# Prints logs for the inquirer including timestamp, device index, 
								# and the notification of the transmission of the inquiring signal.
								if printLogs == True: print(env.now, 'us: Inquirer (' + str(index) + \
									'): Inquiry packet sent in frequency: ' + str(freq))

								# Sets the channel with the inquiring signal.
								band24[freq] = 'inquiry_' + str(index) + '_' + str(env.now)

								# Informs that the interval for advertising PDU transmission has ended.
								sendFirstPDU = False
							# If the advertising PDU transmission ends, and if there were collisions, do nothing.
							# Maybe next time the device finds a relay ;)
							elif (timeSteps == 10 or timeSteps == 234 or timeSteps == 458) and advPDUCollisioned == True:
								# Prints logs for the inquirer including timestamp, device index, 
								# and the notification of the NO transmission of the inquiring signal.
								if printLogs == True: print(env.now, 'us: Inquirer (' + str(index) + \
									'): Inquiry packet NOT sent in frequency: ' + str(freq))

								# Informs that the interval for advertising PDU transmission has ended.
								sendFirstPDU = False
							# If the advertising PDU transmission has not ended, continues transmitting
							# advertising PDU messages.
							else:
								# Prints logs for the requester including timestamp, device index, 
								# and the notification of the transmission of the advertising PDU part.
								if printLogs == True: print(env.now, 'us: Inquirer (' + str(index) + \
									'): Advertising PDU part sent in frequency: ' + str(freq))

								# Sets the channel with a part of the advertising PDU.
								band24[freq] = 'advPDU'

							# Informs that an advertising PDU part was transmitted.
							signalTransmitted = True

						# Add 'blePower' to the total energy spent in the 2.4GHz band.
						totalEnergy24BandInquirer += blePower

				# Scanning after advertising.
				# If the device is not transmitting inquiring signals, the inquirer is listening to
				# inquiring responses from nearby relays.
				if (timeSteps > 10 and timeSteps < 224) or \
					(timeSteps > 234 and timeSteps < 448) or \
					(timeSteps > 458):
					
					# Scanning channel 37.
					if timeSteps > 10 and timeSteps < 224:
						freq = 0
					# Scanning channel 38.
					elif timeSteps > 234 and timeSteps < 448:
						freq = 1
					# Scanning channel 39.
					elif timeSteps > 458:
						freq = 2

					# Prints logs for the requester including timestamp, device index, 
					# and the frequency where the requester is listening to.
					if printLogs == True: print(env.now, 'us: Inquirer (' + str(index) + \
						') -> Scanning at frequency:', freq)
					
					# If the 2.4GHz channel is occupied, and the message contains the word 'scan', 
					# and the message contains this inquirer identifier (index), the inquirer knows 
					# the message is a response for the inquiring message the inquirer sent before. Now, 
					# the requester knows another device has been found.
					if band24[freq] != None and band24[freq].split('_')[0] == 'scan' and \
						band24[freq].split('_')[1] == str(index):

						# Prints logs for the requester including timestamp, and the device index.
						if printLogs == True: print(env.now, 'us: RELAY FOUND for device with index ' + \
							band24[freq].split('_')[1])
						
						# Stops the discovery because a device has been found.
						inquiringEnd[index] = True

						# Informs the exact timestamp which this device found a nearby device.
						afterRelayFoundTimer = env.now

			#############################################
			yield env.timeout(timeResolution) # Time step.
			#############################################

			# Increments by 1 the time step.
			timeSteps += 1

			# If the time step is 640, the advertising interval has expired.
			# Therefore, the time step restarts from zero.
			if timeSteps == 640: # advInterval = 20000 #us -> 20 ms
				timeSteps = 0

				if inquirerBackOffTimeOut == True:
					inquirerBackOffTimeOut = False
					inquirerBackOffTimer = env.now

					# As part of the BLE algorithm, a backoff is computed before discovering
					# devices again.
					back_off = random.randint(0, 10)

					# Prints logs for the inquirer including timestamp, device index, 
					# and backoff.
					if printLogs == True: print(env.now, 'us: Inquirer (' + str(index) + \
						') BACKOFF: ' + str(1000*back_off))

					# Applies the computed backoff.
					inquirerBackOffInterval = 1000*back_off
			# The inquirer backoff has expired.
			if inquirerBackOffTimeOut == False and env.now - inquirerBackOffTimer >= inquirerBackOffInterval:
				inquirerBackOffTimeOut = True
				inquirerBackOffTimer = env.now

				# Resetting parameters.
				timeSteps = 0

			# Cleaning signals.
			# If it was transmitted a signal in the 2.4GHz band, now
			# is time to empty the used channel.
			if signalTransmitted == True:
				if printLogs == True: print(env.now, 'us: CLEANED by Inquirer (' + str(index) + ')')
				signalTransmitted = False
				band24[freq] = None

			collisionListBand24 = [None for i in range(3)]
		else:
			yield env.timeout(finishTime)

def scanner(env, index, blePower, finishTime, timeResolution, printLogs):
	############### Scanner ###############
	global band24
	global collisionListBand24
	global totalCollisions24Band
	global totalEnergy24BandScanner
	global inquiringEnd

	back_off = random.randint(0, 100)
	#yield env.timeout(timeResolution*back_off)
	timeSteps = 0
	deviceConfigured = False
	signalReceived = False
	sendFirstPDU = False
	signalTransmitted = False
	respPDUCollisioned = False
	# Informs that the BLE backoff has expired (True) or not (False).
	scannerBackOffTimeOut = True
	# Time to wait to response to inquiring messages.
	timeToResponse = timeResolution*4.8 # 150us Tifs.
	# Timers.
	msgTimestamp = 0
	scannerBackOffTimer = 0
	while True:
		# If there are devices that have not discovered other devices, the scanner continues scanning.
		if False in inquiringEnd:
			if scannerBackOffTimeOut == True:
				# Configures the scanner parameters the first time its tasks are executed.
				if deviceConfigured == False:
					# Informs that this device D2D technology has been configured.
					deviceConfigured = True

					# timeSteps is used to set the start of the discovery procedure.
					timeSteps = 0

					# Randomly sets the first frequency the relay will listen to.
					freq = random.choice([0, 1, 2]) # Channels 37 (0), 38 (1), and 39 (2).

				if timeSteps <= 800: # scanWindow = 25000 #us -> 25 ms

					# Listens to discovery messages in 2.4GHz band.
					# If this scanner has not received a signal and this scanner finds a message
					# in the 2.4GHz band, and the message contains the word 'inquiry', the relay 
					# knows an inquirer is looking for scanners.
					if signalReceived == False and sendFirstPDU == False and band24[freq] != None and \
						band24[freq].split('_')[0] == 'inquiry':

						# Index of the requester that sent the message.
						msgRequester = band24[freq].split('_')[1]

						# Timestamp which the message sent by the requester was received.
						msgTimestamp = env.now
						
						# Prints logs for the scanner including timestamp, device index, 
						# and the channel where the signal was received.
						if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + \
							') DISCOVERY SIGNAL ARRIVED in freq=' + str(freq))
						
						# Channel where this requester will send back the acknowledge message to the requester.
						frequencyForResponse = freq

						# Informs an inquiring signal as arrived (useful to free the channel later).
						signalReceived = True

					# If this scanner received an inquiring signal from an inquirer and the time
					# to wait to reply has expired, the scanner will reply with an acknowledge
					# message to the inquirer.
					if signalReceived == True and sendFirstPDU == False and env.now - msgTimestamp >= timeToResponse:
						signalReceived = False
						sendFirstPDU = True
						# Counts the timesteps after receiving a discovery signal.
						stepsCounter = 0

					if sendFirstPDU == True:
						if band24[freq] != None or collisionListBand24[freq] != None:
							# Informs that a collision occurred for at least one response PDU part transmission.
							respPDUCollisioned = True

							# Prints logs for the scanner including timestamp, device index, 
							# and the notification of the collision.
							if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + \
								'): Collision freq=' + str(freq))

							# Free the channel for next transmissions.
							band24[freq] = None

							# Sets the channel as a conflictive channel. Collisions will occur
							# for other devices transmitting at the same time in this channel.
							collisionListBand24[freq] = 'collision'

							# Add 1 to the number of collisions in the 2.4GHz band.
							totalCollisions24Band += 1

							# Informs that occured a collision and no signal was transmitted.
							signalTransmitted = False

							if (stepsCounter == 10):
								respPDUCollisioned = False
						# If the channel is empty, the device can send the inquiring signal.
						else:
							# If the response PDU transmission ends, and if there were no collisions, informs
							# that a response packet has been sent.
							if (stepsCounter == 10) and respPDUCollisioned == False:
								# Prints logs for the scanner including timestamp, device index, 
								# and the notification of the transmission of the response signal.
								if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + \
									'): Response packet sent in frequency: ' + str(freq))

								# Sets the channel with the response signal.
								band24[freq] = 'scan_' + msgRequester + '_' + str(index) + '_' + str(env.now)

								respPDUCollisioned = False
							# If the response PDU transmission ends, and if there were collisions, do nothing.
							elif (stepsCounter == 10) and respPDUCollisioned == True:
								# Prints logs for the scanner including timestamp, device index, 
								# and the notification of the NO transmission of the response signal.
								if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + \
									'): Response packet NOT sent in frequency: ' + str(freq))

								respPDUCollisioned = False
							# If the response PDU transmission has not ended, continues transmitting
							# response PDU messages.
							else:
								# Prints logs for the scanner including timestamp, device index, 
								# and the notification of the transmission of the response PDU part.
								if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + \
									'): Response PDU part sent in frequency: ' + str(freq))

								# Sets the channel with a part of the advertising PDU.
								band24[freq] = 'respPDU'

							# Informs that a response PDU part was transmitted.
							signalTransmitted = True

						# Add 'blePower' to the total energy spent in the 2.4GHz band.
						totalEnergy24BandScanner += blePower

						stepsCounter += 1
						if stepsCounter == 11:
							# Informs that the interval for response PDU transmission has ended.
							sendFirstPDU = False

			#############################################
			yield env.timeout(timeResolution) # Time step.
			#############################################

			# Increments by 1 the time step.
			timeSteps += 1

			# If the time step is 1600, the scanning interval has expired.
			# Therefore, the time step restarts from zero.
			if timeSteps == 1600: # scanInterval = 50000 #us -> 50 ms
				timeSteps = 0

				# This is the next frequency the scanner will listen to.
				freq += 1
				if freq > 2:
					freq = 0

				if scannerBackOffTimeOut == True:
					scannerBackOffTimeOut = False
					scannerBackOffTimer = env.now

					# Backoff applied to avoid collisions when two scanners receive an inquiring
					# message in the same frequency at the same time.
					back_off = random.randint(1, 16304) # 10240ms - 50ms (window) = 10190ms -> 10190ms/0.625ms = 16304 (integer)

					scannerBackOffInterval = 625*back_off - timeResolution
					# Prints logs for the scanner including timestamp, device index, 
					# and backoff.
					if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + \
						') BACKOFF after scanning interval: ' + str(scannerBackOffInterval))
			# The scanner backoff has expired.
			if scannerBackOffTimeOut == False and env.now - scannerBackOffTimer >= scannerBackOffInterval:
				scannerBackOffTimeOut = True
				scannerBackOffTimer = env.now

				# Resetting parameters.
				timeSteps = 0
				freq = 0

			# Cleaning signals.
			# If it was transmitted a signal in the 2.4GHz band, now
			# is time to empty the used channel.
			if signalTransmitted == True:
				if printLogs == True: print(env.now, 'us: CLEANED by Scanner (' + str(index) + ')')
				signalTransmitted = False
				band24[freq] = None

			collisionListBand24 = [None for i in range(3)]
		else:
			yield env.timeout(finishTime)

def main(totalInquirers, totalScanners, forFile, printLogs, seed):
	random.seed(seed)

	global band24
	band24 = [None for i in range(3)]
	global collisionListBand24
	collisionListBand24 = [None for i in range(3)]
	global totalCollisions24Band
	totalCollisions24Band = 0
	global totalEnergy24BandInquirer
	totalEnergy24BandInquirer = 0
	global totalEnergy24BandScanner
	totalEnergy24BandScanner = 0
	global inquiringEnd
	inquiringEnd = [False for i in range(totalInquirers)]
	global afterRelayFoundTimer
	afterRelayFoundTimer = 0
	blePower = 1

	print('Total Inquirers: ', totalInquirers)
	print('Total Scanners: ', totalScanners)
	print('Executing...')
	env = simpy.Environment()
	timeResolution = 31.25
	finishTime = 6*10**7 # 1 minute.
	for inq_ix in range(totalInquirers):
		env.process(inquiry(env, inq_ix, blePower, finishTime, timeResolution, printLogs))
	for inq_ix in range(totalScanners):
		env.process(scanner(env, inq_ix, blePower, finishTime, timeResolution, printLogs))
	env.run(until=finishTime)
	print('---------- Simulation complete ----------')
	total_inq_find_sc = 0
	for i in inquiringEnd:
		if i == True: total_inq_find_sc += 1
	if total_inq_find_sc != totalInquirers: afterRelayFoundTimer = finishTime
	print('Total inquirers that found a relay: ', total_inq_find_sc, ' of ', totalInquirers)
	print('Total collisions: ', totalCollisions24Band)
	print('Energy dropped by Inquirers Tx: ', totalEnergy24BandInquirer)
	print('Energy dropped by Scanners Tx: ', totalEnergy24BandScanner)
	print('\n\n')

	if not os.path.isdir('logs'): os.mkdir('logs')
	if not os.path.isdir('logs/logs' + str(seed)): os.mkdir('logs/logs' + str(seed))
	file = open('logs/logs' + str(seed) + '/ble' + forFile + '.log', 'a')
	file.write(str(totalInquirers) + '/' + str(totalScanners) + '|' + str(afterRelayFoundTimer) \
		+ '|' + str(total_inq_find_sc) + '|' + str(totalCollisions24Band) + '|' + str(totalEnergy24BandInquirer)\
		 + '|' + str(totalEnergy24BandScanner) + '\n')
	file.close()

if __name__ == '__main__':
	for seed in range(10):
		totalScanners = 10
		for i in range(10, 110, 10):
			main(i, totalScanners, '0', False, seed)

		totalInquirers = 10
		for i in range(10, 110, 10):
			main(totalInquirers, i, '1', False, seed)