#!/usr/bin/python3

def run_sync_client():
	# UNIT = 0x01
	UNIT = 1
	from pymodbus.client.sync import ModbusTcpClient
	from pymodbus.payload import BinaryPayloadDecoder
	from pymodbus.constants import Endian
	import struct
	import copy

	client = ModbusTcpClient('172.31.39.101')
	client.connect()
	
	r = client.read_holding_registers(131, 2, unit=UNIT)
	assert(not r.isError())
	decoder = BinaryPayloadDecoder.fromRegisters(r.registers,byteorder=Endian.Big,wordorder=Endian.Big)
#	print(decoder.decode_32bit_int())
#	value=decoder.decode_32bit_int()
#	valint = value/65536
#	print(int(valint * 10**3) / 10.0**3)
#	print((valint * 800) / 5)

#	print(decoder.decode_16bit_int())
#	print(decoder.decode_16bit_int())
	print(hex(r.registers[1]))
	print(hex(r.registers[0]))
	
	

###  get the time on the device ###
	# client = ModbusTcpClient('172.31.39.101')
	# client.connect()
	# r = client.read_holding_registers(84, 4, unit=UNIT)
	# assert(not r.isError())
	# decoder = BinaryPayloadDecoder.fromRegisters(r.registers,byteorder=Endian.Big,wordorder=Endian.Little)
	# print(decoder.decode_8bit_uint())
	# print(decoder.decode_8bit_uint())
	# print(decoder.decode_8bit_uint())
	# print(decoder.decode_8bit_uint())
	# print(decoder.decode_8bit_uint())
	# print(decoder.decode_8bit_uint())
	# print(decoder.decode_8bit_uint())
	# print(decoder.decode_8bit_uint())

####### get the instant frequency ########
	# r = client.read_holding_registers(168, 2, unit=UNIT)
	# assert(not r.isError())
	# decoder = BinaryPayloadDecoder.fromRegisters(r.registers,byteorder=Endian.Big,wordorder=Endian.Big)
	# value = decoder.decode_32bit_int()
	# print(hex(value))
	# print(int(value))
	# print(int(value)/65536)
########################################

#######  ########
#	r = client.read_holding_registers(11900, 2, unit=UNIT)
#	assert(not r.isError())
#	reg = copy.deepcopy(r)
#	decoder = BinaryPayloadDecoder.fromRegisters(reg.registers,byteorder=Endian.Big,wordorder=Endian.Little)
#	print(hex(decoder.decode_16bit_uint()))
#	print(hex(decoder.decode_16bit_uint()))

#	decoder = BinaryPayloadDecoder.fromRegisters(r.registers,byteorder=Endian.Big,wordorder=Endian.Big)
#	value = decoder.decode_32bit_int()
#	print(hex(value))
#	print(int(value))
#	print(str(int(value)/65536) + " ")
########################################










	# decoder = BinaryPayloadDecoder.fromRegisters(r.registers,byteorder=Endian.Big,wordorder=Endian.Little)
	# print(hex(decoder.decode_8bit_uint()))
	# print(hex(decoder.decode_8bit_uint()))
	# print(hex(decoder.decode_8bit_uint()))
	# print(hex(decoder.decode_8bit_uint()))


	# print(decoder.decode_16bit_uint())
	# print(decoder.decode_16bit_uint())
	# print(reg.registers[1].to_bytes(2, byteorder='big', signed=False) + reg.registers[0].to_bytes(2, byteorder='big', signed=False))


# rr = client.read_input_registers(1, 8, unit=UNIT)
# assert(not rr.isError())     # test that we are not an error
	# its not modicxon 4x, so -1 on the register 

	# rr = client.read_holding_registers(11900, 1, unit=UNIT)
	     # test that we are not an error     
	# assert(rr.registers == [20]*8)      # test the expected value
	# https://pymodbus.readthedocs.io/en/latest/source/example/modbus_payload.html
	
	# decoder = BinaryPayloadDecoder.fromRegisters(r.registers,byteorder=Endian.Big,wordorder=Endian.Big)
	# decoded = decoder.decode_32bit_int()


	# print(decoded/65536)	
	# print(rr.registers[0])
	# print(r.registers[0].to_bytes(8, byteorder='big', signed=False))
	# print(r.registers[1].to_bytes(8, byteorder='big', signed=False))

	# print(r.registers[0].to_bytes(8, byteorder='little', signed=False))
	# print(r.registers[1].to_bytes(8, byteorder='little', signed=False))


	# import copy
	# copy = copy.deepcopy(decoder)
	# # print(copy.decode_32bit_int()/65536)
	# print(copy.decode_32bit_int())
	# print(decoder.decode_16bit_uint())
	# print(decoder.decode_16bit_uint())
	# value = r.registers[1].to_bytes(2, byteorder='big', signed=False) + r.registers[0].to_bytes(2, byteorder='big', signed=False)
	# print(hex(r.registers[0]))
	# print(hex(r.registers[1]))
	# print(hex(r.registers[0]) + hex(r.registers[1]))
	# value = struct.pack('<ii', r.registers[0], r.registers[1])
	# value = struct.unpack('>q', r.registers[0].to_bytes(8, byteorder='big', signed=False), )
	# value2 = int.from_bytes(value, byteorder='little', signed=True)/65536
	# print(value)
	# print(value2)

if __name__ == "__main__":
	run_sync_client()
