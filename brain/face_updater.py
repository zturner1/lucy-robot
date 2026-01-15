#!/usr/bin/env python3
"""
Lucy Face State Updater
Simple module to send state updates to Lucy's face display
"""

import socket
import json

FACE_HOST = 'localhost'
FACE_PORT = 5555

def update_face_state(talking=False, listening=False):
    """
    Send state update to Lucy's face

    Args:
        talking: True if Lucy is currently speaking
        listening: True if Lucy is currently listening
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect((FACE_HOST, FACE_PORT))

        state = json.dumps({
            'talking': talking,
            'listening': listening
        })

        sock.send(state.encode())
        sock.close()
        return True
    except Exception as e:
        # Silently fail if face isn't running
        return False

def set_talking():
    """Set face to talking mode"""
    return update_face_state(talking=True, listening=False)

def set_listening():
    """Set face to listening mode"""
    return update_face_state(talking=False, listening=True)

def set_idle():
    """Set face to idle mode"""
    return update_face_state(talking=False, listening=False)

if __name__ == "__main__":
    # Test the face updater
    import time

    print("Testing face states...")

    print("Setting to listening...")
    set_listening()
    time.sleep(3)

    print("Setting to talking...")
    set_talking()
    time.sleep(3)

    print("Setting to idle...")
    set_idle()

    print("Done!")
