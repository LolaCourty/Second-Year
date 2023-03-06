import asyncio
from bleak import BleakClient

address = "84:0D:8E:1E:C4:2A"
ALL_UUID = "f83fc688-5941-453d-b69b-37ef567d2391"
R2_UUID = "182c9f1e-c180-4a09-92d1-70f374e14b99"
R3_UUID = "2276902f-092b-4d69-bd29-be1ff7d54010"
R4_UUID = "e86cc57b-753e-4982-9298-f2be9eeebed1"
R5_UUID = "42031044-26ab-4c2f-8422-dd73368b00ed"

async def main(address):
    async with BleakClient(address) as client:
        while True:
            #all_task = asyncio.create_task(client.read_gatt_char(ALL_UUID))
            r2_task = asyncio.create_task(client.read_gatt_char(R2_UUID))
            r3_task = asyncio.create_task(client.read_gatt_char(R3_UUID))
            r4_task = asyncio.create_task(client.read_gatt_char(R4_UUID))
            r5_task = asyncio.create_task(client.read_gatt_char(R5_UUID))

            #print("all value: {}".format(await all_task))
            print("R2 value: {}".format(int.from_bytes(await r2_task, 'little')), end=' ')
            print("R3 value: {}".format(int.from_bytes(await r3_task, 'little')), end=' ')
            print("R4 value: {}".format(int.from_bytes(await r4_task, 'little')), end=' ')
            print("R5 value: {}".format(int.from_bytes(await r5_task, 'little')), end=' ')
            print()
            #print("--------------------------------------------------")

asyncio.run(main(address))
