import mido
from mido import MidiFile
import time

print(mido.get_output_names())
port = mido.open_output()
print(port)
port.send(mido.Message('note_on', note=60))
time.sleep(5)
port.send(mido.Message('note_off'))
