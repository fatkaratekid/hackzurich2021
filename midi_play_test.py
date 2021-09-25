import mido

port = mido.open_output()

mid = mido.MidiFile('music.mid')
for msg in mid.play():
    try:
        print(msg)
        port.send(msg)
    except KeyboardInterrupt:
        print("Press Ctrl-C to terminate while statement")
        pass