# libmpsse_py
Tiny python wrapper around libmpsse.dll provided by FTDI.
It is tried to be very similar to actual FTDI document "AN_178 user guid for libmpsse SPI"

# Limitation
Supports windows only.
Supports SPI interface only.

# Dependencies
Need to download libmpsse.dll from FTDI site and copy it at C:\Windows\System32\libmpsse.dll
Or change the dll_path variable and point to right location.

# Usage example

from libmpsse_spi import SPI

spi = SPI()

spi.getNumChannels()

spi.openChannel(chn_no = 0)

spi.closeChannel()

spi.initChannel(clk=1000000, latency=1, config=SPI.SPI_CONFIG_OPTION_CS_ACTIVELOW)

write_buffer = [0x80, 0x29] # list of bytes to transfer on MOSI, MSB first

read_buffer = spi.readWrite(write_buffer) # returns read data from MISO
