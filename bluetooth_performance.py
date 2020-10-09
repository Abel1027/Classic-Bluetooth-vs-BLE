import simpy
import random
import os

def binary_to_decimal(b_num):
	return int(b_num, 2)

def decimal_to_binary(d_num):
	return bin(d_num)

def inquiry(env, index, blePower, finishTime, timeResolution, printLogs):
	############### Inquiry ###############
	global band24
	global collisionListBand24
	global totalCollisions24Band
	global totalEnergy24BandInquirer
	global inquiringEnd
	global afterRelayFoundTimer

	# Randomly selecting the 'off' initiator of the 28-bit clock generator.
	off_list = [0, 16]
	off = random.choice(off_list)
	max_num_bits = 28
	clock = '0b'
	for i in range(max_num_bits):
		clock = clock + '0'

	# Counts the number of 312.5us intervals every four 312.5us.
	counter = -1
	# Counts the number of time steps.
	stepsCounter = 0
	advPDUCollisioned = False
	sendFirstPDU = False

	back_off = random.randint(0, 10)
	#yield env.timeout(timeResolution*back_off)
	while True:
		# Range 0us-312.5us.
		for step in range(10):
			if inquiringEnd[index] == False:
				# At the first step of range 0us-312.5us, selects a new frequency.
				if step == 0:
					if len(list(clock)) < max_num_bits + 2:
						chunk = ''
						for j in range(max_num_bits + 2 - len(list(clock))):
							chunk = chunk + '0'
						clock = '0b' + chunk + clock.split('0b')[-1]
					CLK_16_12 = binary_to_decimal('0b' + clock[-17:-12])
					CLK_4_2_0 = binary_to_decimal('0b' + clock[-5:-2] + clock[-1])
					# Generating frequency.
					freq = (CLK_16_12 + off + (CLK_4_2_0 - CLK_16_12) % 16) % 32
					clock = decimal_to_binary(binary_to_decimal(clock) + 1)

					counter += 1
					if counter > 3: counter = 0

				# Inquiring intervals.
				if counter == 0 or counter == 1:
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
						if (step == 9): 
							sendFirstPDU = False
							advPDUCollisioned = False
					# If the channel is empty, the device can send the inquiring signal.
					else:
						# If the advertising PDU transmission ends, and if there were no collisions, informs
						# that a inquiring packet has been sent.
						if (step == 9) and advPDUCollisioned == False:
							# Prints logs for the inquirer including timestamp, device index, 
							# and the notification of the transmission of the inquiring signal.
							if printLogs == True: print(env.now, 'us: Inquirer (' + str(index) + \
								'): Inquiry packet sent in frequency: ' + str(freq))

							# Sets the channel with the inquiring signal.
							band24[freq] = 'inquiry_' + str(index) + '_' + str(env.now)

							# Informs that the interval for advertising PDU transmission has ended.
							sendFirstPDU = False

							advPDUCollisioned = False
						# If the advertising PDU transmission ends, and if there were collisions, do nothing.
						# Maybe next time the device finds a relay ;)
						elif (step == 9) and advPDUCollisioned == True:
							# Prints logs for the inquirer including timestamp, device index, 
							# and the notification of the NO transmission of the inquiring signal.
							if printLogs == True: print(env.now, 'us: Inquirer (' + str(index) + \
								'): Inquiry packet NOT sent in frequency: ' + str(freq))

							# Informs that the interval for advertising PDU transmission has ended.
							sendFirstPDU = False

							advPDUCollisioned = False
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
				# Scanning intervals.
				elif counter == 2 or counter == 3:
					if band24[freq] != None and band24[freq].split('_')[0] == 'scan' and band24[freq].split('_')[1] == str(index):
						# Prints logs for the requester including timestamp, and the device index.
						if printLogs == True: print(env.now, 'us: RELAY FOUND (' + band24[freq].split('_')[2] \
							+ ') for device with index ' + band24[freq].split('_')[1])

						# Stops the discovery because a device has been found.
						inquiringEnd[index] = True
						
						# Informs the exact timestamp which this device found a nearby device.
						afterRelayFoundTimer = env.now
				
				#############################################
				yield env.timeout(timeResolution) # Time step.
				#############################################

				# Cleaning signals.
				# If it was transmitted a signal in the 2.4GHz band, now
				# is time to empty the used channel.
				if signalTransmitted == True:
					if printLogs == True: print(env.now, 'us: CLEANED by Inquirer (' + str(index) + ')')
					signalTransmitted = False
					band24[freq] = None

				collisionListBand24 = [None for i in range(32)]

				stepsCounter += 1
			else:
				yield env.timeout(finishTime)

		# After 11.25ms generates backoff.
		if stepsCounter >= 360:
			stepsCounter = 0
			#back_off = random.randint(0, 10)
			back_off = random.choice([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
			if printLogs == True: print(env.now, 'us: Inquirer (' + str(index) + ') BACKOFF=' + str(timeResolution*back_off))
			yield env.timeout(timeResolution*back_off) # Waits [0, ..., 10]*31.25us to start again.

def scanner(env, index, blePower, finishTime, timeResolution, printLogs):
	############### Scanner ###############
	global band24
	global collisionListBand24
	global totalCollisions24Band
	global totalEnergy24BandScanner
	global inquiringEnd

	# 'off' initiator of the 28-bit clock generator.
	off = 0
	max_num_bits = 28
	clock = '0b'
	for i in range(max_num_bits):
		clock = clock + '0'

	# Counts the number of 312.5us intervals every four 312.5us.
	counter = 0
	# Counts the timesteps after receiving a discovery signal.
	stepsCounter = 0
	sendFirstPDU = False
	signalReceived = False
	signalTransmitted = False
	respPDUCollisioned = False
	txEnd = False
	# N of the 28-bit clock frequency generator.
	N = -1

	# Random start.
	back_off = random.randint(0, 100)
	#yield env.timeout(timeResolution*back_off)
	while True:
		# Scanning for 11.25ms.
		for step in range(360):
			if False in inquiringEnd:
				if step == 0:
					if len(list(clock)) < max_num_bits + 2:
						chunk = ''
						for j in range(max_num_bits + 2 - len(list(clock))):
							chunk = chunk + '0'
						clock = '0b' + chunk + clock.split('0b')[-1]
					CLK_16_12 = binary_to_decimal('0b' + clock[-17:-12])
					if clock[-1] == '0':
						N += 1
					# Generating the scanning frequency.
					freq = (CLK_16_12 + N) % 32
					clock = decimal_to_binary(binary_to_decimal(clock) + 2)

				if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + \
						') Scanning in freq=' + str(freq))

				if signalReceived == False and band24[freq] != None and band24[freq].split('_')[0] == 'inquiry':
					msgRequester = band24[freq].split('_')[1] + '_' + str(counter)
					# Prints logs for the scanner including timestamp, device index, 
					# and the channel where the signal was received.
					if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + \
						') DISCOVERY SIGNAL ARRIVED in freq=' + str(freq))

					signalReceived = True

				if signalReceived == True and counter - int(msgRequester.split('_')[1]) == 9:
					signalReceived = False
					sendFirstPDU = True
					# Counts the timesteps after receiving a discovery signal.
					stepsCounter = 0

				if sendFirstPDU == True:
					# Transmits back.
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
							txEnd = True
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
							band24[freq] = 'scan_' + msgRequester.split('_')[0] + '_' + str(index) + '_' + str(env.now)

							txEnd = True

							respPDUCollisioned = False
						# If the response PDU transmission ends, and if there were collisions, do nothing.
						elif (stepsCounter == 10) and respPDUCollisioned == True:
							# Prints logs for the scanner including timestamp, device index, 
							# and the notification of the NO transmission of the response signal.
							if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + \
								'): Response packet NOT sent in frequency: ' + str(freq))

							txEnd = True

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
				yield env.timeout(timeResolution) # Time step. Scan 360 times within 11.25ms.
				#############################################

				# Cleaning signals.
				# If it was transmitted a signal in the 2.4GHz band, now
				# is time to empty the used channel.
				if signalTransmitted == True:
					if printLogs == True: print(env.now, 'us: CLEANED by Scanner (' + str(index) + ')')
					signalTransmitted = False
					band24[freq] = None

				if txEnd == True:
					txEnd = False
					random_timer = random.randint(0, 127)*timeResolution*20
					yield env.timeout(random_timer) # Waits [0,..., 127]*11.25 ms to scan again.

				collisionListBand24 = [None for i in range(32)]

				counter += 1
			else:
				yield env.timeout(finishTime)
		signalReceived = False
		signalTransmitted = False
		if printLogs == True: print(env.now, 'us: Scanner (' + str(index) + ') waiting 0.64 seconds to scan again')
		yield env.timeout(40960/2*timeResolution) # Waits 0.64 seconds to scan again.

def main(totalInquirers, totalScanners, forFile, printLogs, seed):
	random.seed(seed)

	global band24
	band24 = [None for i in range(32)]
	global collisionListBand24
	collisionListBand24 = [None for i in range(32)]
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
	file = open('logs/logs' + str(seed) + '/bluetooth' + forFile + '.log', 'a')
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