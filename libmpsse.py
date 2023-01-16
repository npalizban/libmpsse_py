import ctypes

dll = ctypes.cdll.LoadLibrary(r'C:\Windows\System32\libmpsse.dll')

class DeviceInfo(ctypes.Structure):
    _fields_ = [
        ('Flags', ctypes.c_ulong),
        ('Type', ctypes.c_ulong),
        ('ID', ctypes.c_ulong),
        ('LocID', ctypes.c_ulong),
        ('SerialNumber', ctypes.c_ubyte*16),
        ('Description', ctypes.c_ubyte*64),
        ('ftHandle', ctypes.c_void_p)]

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

    @staticmethod
    def getChannelInfo(chn_no):
        dev_info = DeviceInfo()
        ret = dll.SPI_GetChannelInfo(chn_no, ctypes.byref(dev_info))
        if ret: raise SPI.SpiError("Error: getChannelInfo ret=%d" % ret)

        chn_info = {
            'Flags': dev_info.Flags,
            'Type':  dev_info.Type,
            'ID': dev_info.ID,
            'LocID': dev_info.LocID,
            'SerialNumber': ''.join(map(chr, dev_info.SerialNumber)).split('\x00')[0],
            'Description': ''.join(map(chr, dev_info.Description)).split('\x00')[0]
        }

        return chn_info

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

class I2C:

    I2C_CLOCK_STANDARD_MODE = 100000
    I2C_CLOCK_FAST_MODE = 400000
    I2C_CLOCK_FAST_MODE_PLUS = 1000000
    I2C_CLOCK_HIGH_SPEED_MODE = 3400000

    I2C_CMD_GETDEVICEID_RD = 0xF9
    I2C_CMD_GETDEVICEID_WR = 0xF8
    I2C_GIVE_ACK = 1
    I2C_GIVE_NACK = 0

    I2C_ENABLE_3PHASE_CLOCKING = 0x00
    I2C_DISABLE_3PHASE_CLOCKING = 0x01
    I2C_DISABLE_ONLY_ZERO = 0x00
    I2C_ENABLE_DRIVE_ONLY_ZERO = 0x02

    I2C_TRANSFER_OPTIONS_START_BIT = 0x01
    I2C_TRANSFER_OPTIONS_STOP_BIT = 0x02
    I2C_TRANSFER_OPTIONS_BREAK_ON_NACK = 0x04
    I2C_TRANSFER_OPTIONS_NACK_LAST_BYTE = 0x08
    I2C_TRANSFER_OPTIONS_FAST_TRANSFER = 0x30
    I2C_TRANSFER_OPTIONS_FAST_TRANSFER_BYTES = 0x10
    I2C_TRANSFER_OPTIONS_FAST_TRANSFER_BITS = 0x20
    I2C_TRANSFER_OPTIONS_NO_ADDRESS = 0x40

    I2C_TRANSFER_OPTIONS_DEFAULT = I2C_TRANSFER_OPTIONS_START_BIT + \
                                   I2C_TRANSFER_OPTIONS_STOP_BIT + \
                                   I2C_TRANSFER_OPTIONS_FAST_TRANSFER_BYTES

    class ChannelConfig(ctypes.Structure):
        _fields_ = [("ClockRate", ctypes.c_uint32),
                    ("LatencyTimer",ctypes.c_uint8),
                    ("Options", ctypes.c_uint32)]

    class I2cError(Exception):
        pass

    @staticmethod
    def getNumChannels():
        chn_count = ctypes.c_uint32()
        ret = dll.I2C_GetNumChannels(ctypes.byref(chn_count))
        if ret: raise I2cError("Error: getNumChannels ret=%d" % ret)
        return chn_count.value

    @staticmethod
    def getChannelInfo(chn_no):
        dev_info = DeviceInfo()
        ret = dll.I2C_GetChannelInfo(chn_no, ctypes.byref(dev_info))
        if ret: raise I2C.I2cError("Error: getChannelInfo ret=%d" % ret)

        chn_info = {
            'Flags': dev_info.Flags,
            'Type':  dev_info.Type,
            'ID': dev_info.ID,
            'LocID': dev_info.LocID,
            'SerialNumber': ''.join(map(chr, dev_info.SerialNumber)).split('\x00')[0],
            'Description': ''.join(map(chr, dev_info.Description)).split('\x00')[0]
        }

        return chn_info


    def __init__(self, chn_no):
        self.chn_no = chn_no
        self.handle = ctypes.c_void_p()

    def openChannel(self):
        ret = dll.I2C_OpenChannel(self.chn_no, ctypes.byref(self.handle))
        if ret: raise I2C.I2cError("Error: Could not open channel %d ret=%d" % (chn_no, ret))

    def closeChannel(self):
        ret = dll.I2C_CloseChannel(self.handle)
        if ret: raise I2C.I2cError("Error: Could not close channel ret=%d" % ret)

    def initChannel(self, clk, latency = 1, options = 0x00):
        chn_conf = I2C.ChannelConfig(clk, latency, options)
        ret = dll.I2C_InitChannel(self.handle, ctypes.byref(chn_conf))
        if ret: raise I2C.I2cError("Error: could not initialize channel ret=%d" % ret)

    def deviceRead(self, device_address, size_bytes, options = I2C_TRANSFER_OPTIONS_DEFAULT):

        device_address = device_address & 0x7F

        buffer = ctypes.create_string_buffer(size_bytes)

        size_to_transfer = ctypes.c_uint32()
        size_to_transfer.value = size_bytes

        size_transfered = ctypes.c_uint32()

        ret = dll.I2C_DeviceRead(
                self.handle,
                device_address,
                size_to_transfer,
                buffer,
                ctypes.byref(size_transfered),
                options
        )

        if ret: raise I2C.I2cError("Error: deviceRead ret=%d" % ret)

        if size_transfered.value != size_to_transfer.value:
            raise I2C.I2cError("Error: transfer=%d != transferred=%d",
                               size_to_transfer.value,
                               size_transfered.value)

        return [ord(buffer[i]) for i in range(size_bytes)]


    def deviceWrite(self, device_address, buffer, size_bytes = None, options = I2C_TRANSFER_OPTIONS_DEFAULT):

        if size_bytes == None: size_bytes = len(write_buffer)

        out_buffer = ctypes.create_string_buffer(size_bytes)

        for i in range(size_bytes): out_buffer[i] = buffer[i]

        size_transfered = ctypes.c_uint32()

        ret = dll.I2C_DeviceWrite(
                self.handle,
                device_address,
                size_bytes,
                out_buffer,
                ctypes.byref(size_transfered),
                options
        )

        if ret: raise I2C.I2cError("Error: deviceWrite ret=%d" % ret)

        if size_transfered.value != size_bytes:
            raise I2C.I2cError("Error: transfer=%d != transferred=%d",
                               size_bytes,
                               size_transfered.value)


if __name__ == '__main__':

    print("#####  test SPI ##### ")
    num_channels = SPI.getNumChannels()
    print("num_channels = %d" % num_channels)

    if num_channels:

        channel_info = [SPI.getChannelInfo(chn_no) for chn_no in range(num_channels)]
        for chn in channel_info: print(chn)

        spi = SPI(chn_no = 0)

        spi.openChannel()

        spi.initChannel(clk = 1000000)

        write = [0x80, 0x29]
        print("write %02x-%02x" % (write[0], write[1]))

        read = spi.readWrite(write)
        print("read  %02x-%02x" % (read[0], read[1]))

        spi.closeChannel()

    print("##### test I2C #####")
    num_channels = I2C.getNumChannels()
    print("num_channels = %d" % num_channels)

    if num_channels:

        channel_info = [I2C.getChannelInfo(chn_no) for chn_no in range(num_channels)]
        for chn in channel_info: print(chn)

        i2c = I2C(chn_no = 0)
        i2c.openChannel()
        i2c.initChannel(clk = I2C.I2C_CLOCK_STANDARD_MODE)
        i2c.closeChannel()
