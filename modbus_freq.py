#!/usr/bin/python3

def run_sync_client():
	# UNIT = 0x01
	UNIT = 1
	from pymodbus.client.sync import ModbusTcpClient
	from pymodbus.payload import BinaryPayloadDecoder
	from pymodbus.constants import Endian
	# import struct

####### get the instant frequency ########
	client = ModbusTcpClient('172.31.39.101')
	client.connect()

	r = client.read_holding_registers(168, 2, unit=UNIT)
	assert(not r.isError())
	decoder = BinaryPayloadDecoder.fromRegisters(r.registers,byteorder=Endian.Big,wordorder=Endian.Big)
	value = decoder.decode_32bit_int()
	valint = int(value)/65536
	print(int(valint * 10**3) / 10.0**3)
########################################


if __name__ == "__main__":
	run_sync_client()