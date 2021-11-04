import time
import rtmidi
from pprint import pprint

import asyncio

import pulsectl_asyncio


from dbus_next.aio import MessageBus
import subprocess


def light_on(midiout, note):
    note_on = [176, note, 127]
    midiout.send_message(note_on)

def light_out(midiout, note):
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


    output_sinks = await pulse.sink_list()
    
    for sink in output_sinks:
        print(sink)

    input_sinks = {}
    
    for sink in await pulse.sink_input_list():
        input_sinks[sink.name] = sink


    # bus = await MessageBus().connect()
    # introspection = await bus.introspect('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2')

    # obj = bus.get_proxy_object('org.mpris.MediaPlayer2.spotify', '/org/mpris/MediaPlayer2', introspection)
    # player = obj.get_interface('org.mpris.MediaPlayer2.Player')
    # properties = obj.get_interface('org.freedesktop.DBus.Properties')


    # # call methods on the interface (this causes the media player to play)
    # # await player.call_play()

    # volume = await player.get_volume()
    # print(f'current volume: {volume}, setting to 0.5')

    # # await player.set_volume(0.5)

    # # listen to signals
    # def on_properties_changed(interface_name, changed_properties, invalidated_properties):
    #     for changed, variant in changed_properties.items():
    #         print(f'property changed: {changed} - {variant.value}')

    # properties.on_properties_changed(on_properties_changed)




    with midiin:

        light_out(midiout, 41)
        light_out(midiout, 42)

        while True:
            message = midiin.get_message()
            if message:
                pprint(message)

                ((channel, note, value), duration) = message

                # Master volume
                if note == 7:
                    print(f"set master volume to {value}")
                

                if value == 127:
                    light_on(midiout, note)

                if value == 0:
                    light_out(midiout, note)




                # Play
                if note == 41 and value == 0:
                    light_on(midiout, 41)
                    light_out(midiout, 42)
                    subprocess.run(["playerctl", "-p", "spotify", "play"])


      
                # Pause
                if note == 42 and value == 0:
                    light_out(midiout, 41)
                    subprocess.run(["playerctl", "pause"])

                # Spotify / music
                if note == 0:
                    await set_sink_input_volume(input_sinks, ['Spotify'], pulse, value)
            

                # Signal, discord etc
                if note == 1:
                    await set_sink_input_volume(input_sinks, ["Signal", "Discord"], pulse, value)        
                    
    
        await loop.create_future()


    del midiout

# Run event loop until main_task finishes
loop = asyncio.get_event_loop()
loop.run_until_complete(main())