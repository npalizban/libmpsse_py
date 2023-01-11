import ctypes

dll = ctypes.cdll.LoadLibrary(r'C:\Windows\System32\libmpsse.dll')

class SPI:

    SPI_CONFIG_OPTION_MODE0 = 0x00
    SPI_CONFIG_OPTION_MODE1 = 0x01
    SPI_CONFIG_OPTION_MODE2 = 0x02
    SPI_CONFIG_OPTION_MODE3	= 0x03
    SPI_CONFIG_OPTION_CS_DBUS3 = 0x00
    SPI_CONFIG_OPTION_CS_DBUS4 = 0x04
    SPI_CONFIG_OPTION_CS_DBUS5 = 0x08
    SPI_CONFIG_OPTION_CS_DBUS6 = 0x0C
    SPI_CONFIG_OPTION_CS_DBUS7 = 0x10
    SPI_CONFIG_OPTION_CS_ACTIVEHIGH = 0x00
    SPI_CONFIG_OPTION_CS_ACTIVELOW = 0x20

    SPI_TRANSFER_OPTIONS_SIZE_IN_BYTES = 0x00
    SPI_TRANSFER_OPTIONS_SIZE_IN_BITS = 0x01
    SPI_TRANSFER_OPTIONS_CHIPSELECT_ENABLE = 0x02
    SPI_TRANSFER_OPTIONS_CHIPSELECT_DISABLE = 0x04
    SPI_TRANSFER_OPTIONS_LSB_FIRST = 0x08

    SPI_TRANSFER_OPTIONS_DEFAULT = SPI_TRANSFER_OPTIONS_SIZE_IN_BYTES + \
                                   SPI_TRANSFER_OPTIONS_CHIPSELECT_ENABLE + \
                                   SPI_TRANSFER_OPTIONS_CHIPSELECT_DISABLE

    class ChannelConfig(ctypes.Structure):
        _fields_ = [("ClockRate", ctypes.c_uint32),
                    ("LatencyTimer",ctypes.c_uint8),
                    ("Options", ctypes.c_uint32),
                    ("Pins", ctypes.c_uint32),
                    ("reserved", ctypes.c_uint16)]

    class SpiError(Exception):
        pass

    @staticmethod
    def getNumChannels():
        chn_count = ctypes.c_uint32()
        ret = dll.SPI_GetNumChannels(ctypes.byref(chn_count))
        if ret: raise SPI.SpiError("Error: getNumChannels ret=%d" % ret)
        return chn_count.value

    def __init__(self, chn_no):
        self.handle = ctypes.c_void_p()
        self.chn_no = chn_no

    def openChannel(self):
        ret = dll.SPI_OpenChannel(self.chn_no, ctypes.byref(self.handle))
        if ret: raise SPI.SpiError("Error: Could not open channel %d ret=%d" % (chn_no, ret))

    def closeChannel(self):
        ret = dll.SPI_CloseChannel(self.handle)
        if ret: raise SPI.SpiError("Error: Could not close channel ret=%d" % ret)

    def initChannel(self, clk,
                    latency=1,
                    config=SPI_CONFIG_OPTION_CS_ACTIVELOW,
                    pins=0xffffffff):

        chn_conf = SPI.ChannelConfig(clk, latency, config, pins, 0xff)
        ret = dll.SPI_InitChannel(self.handle, ctypes.byref(chn_conf))
        if ret: raise SPI.SpiError("Error: could not initialize channel ret=%d" % ret)

    def readWrite(self, write_buffer, size_bytes = None, options = SPI_TRANSFER_OPTIONS_DEFAULT):

        if size_bytes == None: size_bytes = len(write_buffer)

        out_buffer = ctypes.create_string_buffer(size_bytes)
        in_buffer = ctypes.create_string_buffer(size_bytes)

        for i in range(size_bytes):
            out_buffer[i] = write_buffer[i]

        size_to_transfer = ctypes.c_uint32()
        size_to_transfer.value = size_bytes

        size_transfered = ctypes.c_uint32()

        ret = dll.SPI_ReadWrite(
                self.handle,
                in_buffer,
                out_buffer,
                size_to_transfer,
                ctypes.byref(size_transfered),
                options
        )

        if ret: raise SPI.SpiErrir("Error: read write failed ret=%d" % ret)

        if size_transfered.value != size_to_transfer.value:
            raise SPI.SpiError("Error: transfer=%d != transferred=%d",
                               size_to_transfer.value,
                               size_transfered.value)

        return [ord(in_buffer[i]) for i in range(size_bytes)]

if __name__ == '__main__':

    print(SPI.getNumChannels())

    spi = SPI(chn_no = 0)

    spi.openChannel()

    spi.initChannel(clk = 1000000)

    read = spi.readWrite([0x80, 0x29])
    print(read)

    spi.closeChannel()
