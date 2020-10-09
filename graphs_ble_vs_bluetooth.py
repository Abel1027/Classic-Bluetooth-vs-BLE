import matplotlib.pyplot as plt
import os

if not os.path.isdir('graphs'): os.mkdir('graphs')
logs_dirs = os.listdir('logs')

x = []
time = []
inq_find_sc = []
collision = []
inq_energy = []
sc_energy = []
for index, log_dir in enumerate(logs_dirs):
	file = open('logs/' + log_dir + '/bluetooth0.log')
	lines = file.readlines()
	file.close()
	
	for ix, line in enumerate(lines):
		if index == 0:
			x.append(line.split('|')[0])
			time.append(float(line.split('|')[1]))
			inq_find_sc.append(int(line.split('|')[2]))
			collision.append(int(line.split('|')[3]))
			inq_energy.append(int(line.split('|')[4]))
			sc_energy.append(int(line.split('|')[5]))
		else:
			time[ix] = time[ix] + float(line.split('|')[1])
			inq_find_sc[ix] = inq_find_sc[ix] + int(line.split('|')[2])
			collision[ix] = collision[ix] + int(line.split('|')[3])
			inq_energy[ix] = inq_energy[ix] + int(line.split('|')[4])
			sc_energy[ix] = sc_energy[ix] + int(line.split('|')[5])

time = [i/len(logs_dirs) for i in time]
inq_find_sc = [i/len(logs_dirs) for i in inq_find_sc]
collision = [i/len(logs_dirs) for i in collision]
inq_energy = [i/len(logs_dirs) for i in inq_energy]
sc_energy = [i/len(logs_dirs) for i in sc_energy]

x_ = []
time_ = []
inq_find_sc_ = []
collision_ = []
inq_energy_ = []
sc_energy_ = []
for index, log_dir in enumerate(logs_dirs):
	file = open('logs/' + log_dir + '/ble0.log')
	lines = file.readlines()
	file.close()
	
	for ix, line in enumerate(lines):
		if index == 0:
			x_.append(line.split('|')[0])
			time_.append(float(line.split('|')[1]))
			inq_find_sc_.append(int(line.split('|')[2]))
			collision_.append(int(line.split('|')[3]))
			inq_energy_.append(int(line.split('|')[4]))
			sc_energy_.append(int(line.split('|')[5]))
		else:
			time_[ix] = time_[ix] + float(line.split('|')[1])
			inq_find_sc_[ix] = inq_find_sc_[ix] + int(line.split('|')[2])
			collision_[ix] = collision_[ix] + int(line.split('|')[3])
			inq_energy_[ix] = inq_energy_[ix] + int(line.split('|')[4])
			sc_energy_[ix] = sc_energy_[ix] + int(line.split('|')[5])

time_ = [i/len(logs_dirs) for i in time_]
inq_find_sc_ = [i/len(logs_dirs) for i in inq_find_sc_]
collision_ = [i/len(logs_dirs) for i in collision_]
inq_energy_ = [i/len(logs_dirs) for i in inq_energy_]
sc_energy_ = [i/len(logs_dirs) for i in sc_energy_]

plt.plot(x, time, label='Classic Bluetooth')
plt.plot(x_, time_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Elapsed time for all inquirers to find a scanner')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Time (s)')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/time_0.png')
plt.show()

plt.plot(x, inq_find_sc, label='Classic Bluetooth')
plt.plot(x_, inq_find_sc_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Total number of inquirers that find at least one scanner')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Number of inquirers')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/inq_find_sc_0.png')
plt.show()

plt.plot(x, collision, label='Classic Bluetooth')
plt.plot(x_, collision_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Total collisions')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Number of collisions')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/collisions_0.png')
plt.show()

plt.plot(x, inq_energy, label='Classic Bluetooth')
plt.plot(x_, inq_energy_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Units of energy spent by inquirers')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Energy')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/inq_energy_0.png')
plt.show()

plt.plot(x, sc_energy, label='Classic Bluetooth')
plt.plot(x_, sc_energy_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Units of energy spent by scanners')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Energy')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/sc_energy_0.png')
plt.show()

#########################################################

x = []
time = []
inq_find_sc = []
collision = []
inq_energy = []
sc_energy = []
for index, log_dir in enumerate(logs_dirs):
	file = open('logs/' + log_dir + '/bluetooth1.log')
	lines = file.readlines()
	file.close()
	
	for ix, line in enumerate(lines):
		if index == 0:
			x.append(line.split('|')[0])
			time.append(float(line.split('|')[1]))
			inq_find_sc.append(int(line.split('|')[2]))
			collision.append(int(line.split('|')[3]))
			inq_energy.append(int(line.split('|')[4]))
			sc_energy.append(int(line.split('|')[5]))
		else:
			time[ix] = time[ix] + float(line.split('|')[1])
			inq_find_sc[ix] = inq_find_sc[ix] + int(line.split('|')[2])
			collision[ix] = collision[ix] + int(line.split('|')[3])
			inq_energy[ix] = inq_energy[ix] + int(line.split('|')[4])
			sc_energy[ix] = sc_energy[ix] + int(line.split('|')[5])

time = [i/len(logs_dirs) for i in time]
inq_find_sc = [i/len(logs_dirs) for i in inq_find_sc]
collision = [i/len(logs_dirs) for i in collision]
inq_energy = [i/len(logs_dirs) for i in inq_energy]
sc_energy = [i/len(logs_dirs) for i in sc_energy]

x_ = []
time_ = []
inq_find_sc_ = []
collision_ = []
inq_energy_ = []
sc_energy_ = []
for index, log_dir in enumerate(logs_dirs):
	file = open('logs/' + log_dir + '/ble1.log')
	lines = file.readlines()
	file.close()
	
	for ix, line in enumerate(lines):
		if index == 0:
			x_.append(line.split('|')[0])
			time_.append(float(line.split('|')[1]))
			inq_find_sc_.append(int(line.split('|')[2]))
			collision_.append(int(line.split('|')[3]))
			inq_energy_.append(int(line.split('|')[4]))
			sc_energy_.append(int(line.split('|')[5]))
		else:
			time_[ix] = time_[ix] + float(line.split('|')[1])
			inq_find_sc_[ix] = inq_find_sc_[ix] + int(line.split('|')[2])
			collision_[ix] = collision_[ix] + int(line.split('|')[3])
			inq_energy_[ix] = inq_energy_[ix] + int(line.split('|')[4])
			sc_energy_[ix] = sc_energy_[ix] + int(line.split('|')[5])

time_ = [i/len(logs_dirs) for i in time_]
inq_find_sc_ = [i/len(logs_dirs) for i in inq_find_sc_]
collision_ = [i/len(logs_dirs) for i in collision_]
inq_energy_ = [i/len(logs_dirs) for i in inq_energy_]
sc_energy_ = [i/len(logs_dirs) for i in sc_energy_]

plt.plot(x, time, label='Classic Bluetooth')
plt.plot(x_, time_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Elapsed time for all inquirers to find a scanner')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Time (s)')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/time_1.png')
plt.show()

plt.plot(x, inq_find_sc, label='Classic Bluetooth')
plt.plot(x_, inq_find_sc_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Total number of inquirers that find at least one scanner')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Number of inquirers')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/inq_find_sc_1.png')
plt.show()

plt.plot(x, collision, label='Classic Bluetooth')
plt.plot(x_, collision_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Total collisions')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Number of collisions')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/collisions_1.png')
plt.show()

plt.plot(x, inq_energy, label='Classic Bluetooth')
plt.plot(x_, inq_energy_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Units of energy spent by inquirers')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Energy')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/inq_energy_1.png')
plt.show()

plt.plot(x, sc_energy, label='Classic Bluetooth')
plt.plot(x_, sc_energy_, label='Bluetooth Low Energy')
plt.yscale('log')
plt.title('Units of energy spent by scanners')
plt.xlabel('Total inquirers vs Total scanners')
plt.ylabel('Energy')
plt.legend(loc='best', shadow=True)
plt.grid(True)
plt.savefig('graphs/sc_energy_1.png')
plt.show()