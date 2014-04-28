#!/usr/bin/python2 -u

import argparse
import socket
import sys
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(description='Stream video from Zmodo DVR')
    parser.add_argument('host', type=str, 
                       help='the host to connect to')
    parser.add_argument('channel', type=int, 
                       help='what channel to retrieve (1, 2, 3, etc)')
    parser.add_argument('-p', '--port', type=int, default=9000,
                       help='the port to connect on (default 9000)')

    return parser.parse_args()

def hex2bin(hex):
    return ''.join('{:02x}'.format(x) for x in hex).decode('hex')

def get_request_bytes():
    data = [  
        0x00, 0x00, 0x00, 0x01, 
        0x00, 0x00, 0x00, 0x03, 
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x68, 
        0x00, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 
        0x01, # the channel to return, 1, 2, 4, 8, etc
        0x00, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 
        0x00, 0x10, 0x00, 0x00, 
        0x04, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 
        0x01, 0x00, 0x00, 0x00, 
        0x00, 0x00, 0x00, 0x00,
        0x13, 0x32, 0x46, 0x77, 
        0x06, 0x61, 0x48, 0x77, 
        0xfa, 0x31, 0x46, 0x77,
    ]

    # pad with 0s to 500 bytes 
    data.extend([0]*(500-len(data)))

    return data

def main():
    args = parse_args()
    print args

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((args.host, args.port))

    request = get_request_bytes()
    # set the channel number byte
    request[31] = 2**(args.channel - 1)

    client.send(hex2bin(request))

    # stream directly into mplayer
    mplayer = subprocess.Popen(['mplayer', '-really-quiet', '-fps', '3', 
                                '-demuxer', 'h264es', '-'], stdin=subprocess.PIPE)

    try:
        while 1:
            data = client.recv(512)
            if not data: break
            mplayer.stdin.write(data)

    except IOError:
        pass

    client.close()


if __name__ == '__main__':
    main()
