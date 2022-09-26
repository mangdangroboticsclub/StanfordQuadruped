import filecmp
import os
import sys
import multiprocessing
import time
import netifaces as ni
from joystick_sim.joystick import Joystick

def runner():
    sys.path.append('/home/ubuntu/StanfordQuadruped')
    import run_robot


def test_is_ip_displayed():
    os.system("rm -f /tmp/Display.log")
    os.system("rm -f /tmp/HardwareInterface.log")
    proc = multiprocessing.Process(target=runner, args=())
    proc.start()
    time.sleep(1)
    proc.terminate()
    if 'wlan0' in ni.interfaces() and ni.AF_INET in ni.ifaddresses('wlan0').keys():
        ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
        text = "IP: %s" % str(ip)
        with open('/tmp/Display.exp'.log_file, 'w') as fh:
            fh.write("%s\n" % text)
        assert filecmp.cmp('/tmp/Display.exp', '/tmp/Display.log')
    elif 'eth0' in ni.interfaces() and ni.AF_INET in ni.ifaddresses('eth0').keys():
        ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
        text = "IP: %s" % str(ip)
        with open('/tmp/Display.exp'.log_file, 'w') as fh:
            fh.write("%s\n" % text)
        assert filecmp.cmp('/tmp/Display.exp', '/tmp/Display.log')
    else:
        assert filecmp.cmp(os.path.join(os.path.dirname(__file__), 'expected_results', 'display_ip'),
                           '/tmp/Display.log')


def test_activate_deactivate():
    os.system("rm -f /tmp/Display.log")
    os.system("rm -f /tmp/HardwareInterface.log")
    proc = multiprocessing.Process(target=runner, args=())
    proc.start()
    joystick = Joystick()
    joystick.start()
    joystick.activate()
    joystick.push_L1()
    time.sleep(1)
    joystick.push_L1()
    time.sleep(1)
    joystick.deactivate()
    joystick.stop()
    proc.terminate()
    assert filecmp.cmp(os.path.join(os.path.dirname(__file__), 'expected_results', 'display_1'),
                       '/tmp/Display.log')
    assert filecmp.cmp(os.path.join(os.path.dirname(__file__), 'expected_results', 'hardwareinterface_1'),
                       '/tmp/HardwareInterface.log')

if __name__ == "__main__":
    test_activate_deactivate()
