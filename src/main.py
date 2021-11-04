import rtmidi
from pprint import pprint
import asyncio
import pulsectl_asyncio
from dbus_next.aio import MessageBus
import subprocess
import yaml
import sys


config_file = open(sys.argv[1])
config = yaml.load(config_file.read(), Loader=yaml.Loader)

pprint(config)

def light_on(midiout, note):
    note_on = [176, note, 127]
    midiout.send_message(note_on)

def light_off(midiout, note):
    note_on = [176, note, 0]
    midiout.send_message(note_on)

async def set_sink_input_volume(input_sinks, apps, pulse, value):
    for app in apps:
        if app in input_sinks:
            sink = input_sinks[app]
            value = map_midi_to_percent(value)
            print(f"set {app} master volume to {value}")
            await pulse.volume_set_all_chans(sink, value)

def map_midi_to_percent(value):
    return (value / 127 ) * 1

async def main():

    midiout = rtmidi.MidiOut()
    midiin = rtmidi.MidiIn()

    for i in range(0, midiin.get_port_count()):
        port_name = midiin.get_port_name(i)
        if port_name.find("nanoKONTROL2") != -1:
            print(f"Opening in port with index {i} and name {port_name}")
            midiin.open_port(i)


    for i in range(0, midiout.get_port_count()):
        port_name = midiout.get_port_name(i)
        if port_name.find("nanoKONTROL2") != -1:
            print(f"Opening out port with index {i} and name {port_name}")
            midiout.open_port(i)


    pulse = pulsectl_asyncio.PulseAsync()
    await pulse.connect()


    input_sinks = {}
    
    for sink in await pulse.sink_input_list():
        input_sinks[sink.name] = sink


    with midiin:

        light_off(midiout, 41)
        light_off(midiout, 42)

        while True:
            message = midiin.get_message()
            if message:
                pprint(message)

                ((channel, note, value), duration) = message



                # Show button being pressed
                if value == 127:
                    light_on(midiout, note)

                if value == 0:
                    light_off(midiout, note)


                for slider in config['sliders']:
                    if slider['note'] == note:
                        print(f"Setting volume for note {note}: {value} {slider['matches']}")
                        await set_sink_input_volume(input_sinks, slider['matches'], pulse, value)


                for button in config['buttons']:
                    if button['note'] == note:
                        print(f"Doing something for note {note}: {value} {slider}")
                        if 'light-on' in button:
                            light_on(midiout, button['light-on'])
                        if 'light-off' in button:
                            light_off(midiout, button['light-off'])
                        if 'command' in button:
                            subprocess.run(button['command'])

             
                


        await loop.create_future()


    del midiout


# Run event loop until main_task finishes
loop = asyncio.get_event_loop()
loop.run_until_complete(main())