# libmpsse_py
Tiny python wrapper for FTDI MPSSE DLL (libmpsse.dll) for I2C and SPI.
It is tried to provide very similar interface as actual FTDI "AN_178" and "AN_177" documents.

FTDI SPI document: https://ftdichip.com/wp-content/uploads/2020/08/AN_178_User-Guide-for-LibMPSSE-SPI-1.pdf
FTDI I2C document: http://www.ftdichip.com/Support/Documents/AppNotes/AN_177_User_Guide_For_LibMPSSE-I2C.pdf

Also check: https://ftdichip.com/software-examples/mpsse-projects/libmpsse-spi-examples/

# Limitation
SPI Tested only with FTDI 2232H on windows platform.
I2C is not tested and no supported yet.
Does not have GPIO functions.

# Dependencies
On windows, need copy libmpsse.dll from FTDI site or this repository to C:\Windows\System32\libmpsse.dll.
If dll is in a different directory, change the dll_path variable inside libmpsse.py accordingly.

# Usage SPI

from libmpsse import SPI

num_channels = SPI.getNumChannels()

channel_info = [SPI.getChannelInfo(chn_no) for chn_no in range(num_channels)]

spi = SPI(chn_no = 0)

spi.openChannel()

spi.initChannel(clk = 1000000)

read = spi.readWrite([0x80 0x29])

spi.closeChannel()

# Usage I2C

num_channels = I2C.getNumChannels()

channel_info = [I2C.getChannelInfo(chn_no) for chn_no in range(num_channels)]

i2c = I2C(chn_no = 0)

i2c.openChannel()

i2c.initChannel(clk = I2C.I2C_CLOCK_STANDARD_MODE)

i2c.closeChannel()
