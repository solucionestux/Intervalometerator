# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied 
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.  If not, see 
# <http://www.gnu.org/licenses/>.
#
# This script is part of the Intervalometerator project, a time-lapse camera controller for DSLRs:
# https://github.com/greiginsydney/Intervalometerator
# https://greiginsydney.com/Intervalometerator
# https://intvlm8r.com
#
#
# Thank you https://docs.python.org/2/howto/urllib2.html
#
# This script is executed every time the Pi boots. It reads the Arduino's time and sets same in the Pi (as the 
#  Pi's time is volatile - it's lost every time it powers-off).
# It runs BEFORE the cameraTransfer.py script.


from urllib2 import urlopen, URLError
from datetime import datetime
import logging
import os
import re
import subprocess

LOGFILE_PATH = os.path.expanduser('/home/pi')
LOGFILE_NAME = os.path.join(LOGFILE_PATH, 'setTime.log')

htmltext = ''
newTime = 'Unknown'


def main():
    logging.basicConfig(filename=LOGFILE_NAME, filemode='w', format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=logging.DEBUG)
    try:
        response = urlopen('http://localhost/')
        log('Response code = ' + str(response.getcode()))
        htmltext = response.read()
        tempTime = re.search(('id="dateTime">(.*)</div>'), htmltext)
        if tempTime != None:
            newTime = tempTime.group(1)
            log('New time is ' + newTime)
        else:
            log('Failed to detect the time')

    except URLError as e:
        if hasattr(e, 'reason'):
            log(str(e.reason))
        elif hasattr(e, 'code'):
            log(str(e.code))
    except Exception as e:
        log('Unhandled web error: ' + str(e))

    try:
        #convert it to a form the date command will accept: Incoming is "2018 Nov 29 21:58:00"
        if "Unknown" not in newTime:
            timeCommand = ['/bin/date', '--set=%s' % datetime.strptime(newTime,'%Y %b %d %H:%M:%S')]
            result = subprocess.Popen(timeCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            (stdoutdata, stderrdata) = result.communicate()
            if stdoutdata != None:
                log('Result = ' + str(stdoutdata))
            if stderrdata != None:
                log('Error = ' + str(stderrdata))
    except Exception as e:
        log('Unhandled time error: ' + str(e))


def log(message):
    try:
        logging.info(message)
    except Exception as e:
        #print 'error:' + str(e)
        pass


if __name__ == '__main__':
    main()
