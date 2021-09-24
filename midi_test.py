import mido
from mido import MidiFile
import time

print(mido.get_output_names())
port = mido.open_output()
# print(port)


msg = mido.Message('note_on', note=60, time=5)
port.send(msg)
time.sleep(msg.time)
port.send(mido.Message('note_off', note=60))
