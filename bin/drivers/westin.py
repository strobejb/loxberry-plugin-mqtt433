import time
import sys

import tx433

NUM_ATTEMPTS = 15
TRANSMIT_PIN = 27

# commands directly supported by the Westin Stratus fan
COMMANDS = dict(
    power  = '0000001111100',
    light  = '0000001111101',
    speed0 = '',
    speed1 = '',
    speed2 = '0000001111110',
    speed3 = '0000001111100101110',
    speed4 = '0000001111100101010',
    timer  = '0000001111100101100',
)

# these commands not supported by Westin. Define them so that
# they still 'work' - this makes it simpler for Loxone
# to just use a single 'speed' command 
COMMANDS['speed0'] = COMMANDS['speed1'] = COMMANDS['power']

# timings needed for transmitting the RF codes
TIMES = dict(
    SHORT_DELAY    = 0.000256, #0.00045
    LONG_DELAY     = 0.00058,  #0.00090
    EXTENDED_DELAY = 0.0162,   #0.01326 #0.0096
)


def transmit_command(device, command):
    #
    # very simple command processing - all commands already defined
    # we ignore the targetted device and just lookup the code for each command
    # 
    if command in COMMANDS:
        code = COMMANDS[command]
        print('Transmitting code:', code)
        tx433.transmit_code(code, TRANSMIT_PIN=TRANSMIT_PIN, NUM_ATTEMPTS=NUM_ATTEMPTS, **TIMES)
        return True
    else:
        print('Unknown command:', command)
        return False
 
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: Transmit <command>')
        sys.exit(0)

    for argument in sys.argv[1:]:
        print(argument)
        if not argument.isdigit():
            code = COMMANDS[argument]
        else:
            # assume argument is a binary code
            code = argument
        print('sending: ', code)
        tx433.transmit_code(code, TRANSMIT_PIN=TRANSMIT_PIN, NUM_ATTEMPTS=NUM_ATTEMPTS, **TIMES)

