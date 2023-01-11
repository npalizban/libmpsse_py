# libmpsse_py
Tiny python wrapper for libmpsse.dll for FTDI.
It is tried to provide very similar interface as actual FTDI "AN_178 user guid for libmpsse SPI" document.

User guide: https://ftdichip.com/wp-content/uploads/2020/08/AN_178_User-Guide-for-LibMPSSE-SPI-1.pdf

Also check: https://ftdichip.com/software-examples/mpsse-projects/libmpsse-spi-examples/

# Limitation
Supports SPI interface only.

# Dependencies
On windows, need to download libmpsse.dll from FTDI site and copy it at C:\Windows\System32\libmpsse.dll.
If dll is not in this directory or using different platforms, change the dll_path variable inside libmpsse_py.py and point to right location.

# Usage example

from libmpsse_spi import SPI

num_channels = SPI.getNumChannels()

spi = SPI(chn_no = 0)

spi.openChannel()

spi.initChannel(clk=1000000, latency=1, config=SPI.SPI_CONFIG_OPTION_CS_ACTIVELOW)

write_buffer = [0x80, 0x29] # list of bytes to transfer on MOSI. Big endian MSB first.

read_buffer = spi.readWrite(write_buffer) # returns read data from MISO

spi.closeChannel()
