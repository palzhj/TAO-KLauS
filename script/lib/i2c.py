#!/usr/bin/python           
# This is i2c.py file
# author: zhj@ihep.ac.cn
# 2019-06-18 created
import rbcp

I2C_BASE_ADDR = 0x100
CLK_FREQ_MHZ = 125 # MHz
I2C_FREQ_KHZ = 100 # kHz

I2C_PRER_LO_ADDR = I2C_BASE_ADDR
I2C_PRER_HI_ADDR = I2C_BASE_ADDR + 0x1
I2C_CTR_ADDR     = I2C_BASE_ADDR + 0x2
I2C_RXR_ADDR     = I2C_BASE_ADDR + 0x3
I2C_TXR_ADDR     = I2C_BASE_ADDR + 0x3
I2C_CR_ADDR      = I2C_BASE_ADDR + 0x4
I2C_SR_ADDR      = I2C_BASE_ADDR + 0x4

I2C_CTR_EN      = 0b10000000 # I2C core enable bit
I2C_CTR_IEN     = 0b01000000 # I2C core interrupt enable bit. 

I2C_TXR_WR      = 0b00000000 # writing to slave 
I2C_TXR_RD      = 0b00000001 # reading from slave 

I2C_CR_STA      = 0b10000000 # generate (repeated) start condition 
I2C_CR_STO      = 0b01000000 # generate stop condition 
I2C_CR_RD       = 0b00100000 # read from slave 
I2C_CR_WR       = 0b00010000 # write to slave 
I2C_CR_NACK     = 0b00001000 # when a receiver, sent ACK (ACK = ‘0’) or NACK (ACK = ‘1’) 
I2C_CR_IACK     = 0b00000001 # Interrupt acknowledge. When set, clears a pending interrupt. 

I2C_SR_NORXACK  = 0b10000000 # No acknowledge received from slave. 
I2C_SR_BUSY     = 0b01000000 # I2C bus busy 
I2C_SR_AL       = 0b00100000 # Arbitration lost 
I2C_SR_TIP      = 0b00000010 # Transfer in progress 
I2C_SR_IF       = 0b00000001 # Interrupt Flag 

class I2CError(Exception):
    """
    I2C Error Exception class.
    """
    pass

class i2c(object):
    """Class for communicating with an I2C device using the adafruit-pureio pure
    python smbus library, or other smbus compatible I2C interface. Allows reading
    and writing 8-bit, 16-bit, and byte array values to registers
    on the device."""
    def __init__(self, address):
        """Create an instance of the I2C device at the specified address on the
        specified I2C bus number."""
        self._address = address
        self._rbcp = rbcp.Rbcp()

        clk_count = int(CLK_FREQ_MHZ*1000/5/I2C_FREQ_KHZ - 1)
        prer_hi = (clk_count >> 8) & 0xFF
        prer_hi = bytes([prer_hi])
        prer_lo = clk_count & 0xFF
        prer_lo = bytes([prer_lo])
        
        if prer_lo != self._rbcp.write(I2C_PRER_LO_ADDR, prer_lo):
            raise ValueError("i2c communication ERROR.")
            return
        self._rbcp.write(I2C_PRER_HI_ADDR, prer_hi)
        self._rbcp.write(I2C_CTR_ADDR, bytes([I2C_CTR_EN])) # enable

    # write
    def write8(self, value, with_internal_addr = False, internal_addr = 0):
        """Write an 8-bit value to the specified register."""
        value = value & 0xFF
        internal_addr = internal_addr & 0xFF

        self._rbcp.write(I2C_TXR_ADDR, bytes([self._address|I2C_TXR_WR])) # present slave address, set write-bit

        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_STA|I2C_CR_WR]))    # set command (start, write)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:        # check tip bit
            pass

        if with_internal_addr:
            self._rbcp.write(I2C_TXR_ADDR, bytes([internal_addr]))      # present internal address
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR]))           # set command (write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:    # check tip bit
               pass

        if (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_NORXACK:
            print("I2C ERROR: No acknowledge received")

        self._rbcp.write(I2C_TXR_ADDR, bytes([value]))                  # present slave's data
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR|I2C_CR_STO]))    # set command (write, stop)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:        # check tip bit
           pass
        # if with_internal_addr:
        #     self._logger.debug("Wrote 0x%02X to register 0x%02X", value, internal_addr)
        # else:
        #     self._logger.debug("Wrote 0x%02X", value)

    def write16(self, value, with_internal_addr = False, internal_addr = 0):
        """Write a 16-bit value to the specified register."""
        value = value & 0xFFFF
        internal_addr = internal_addr & 0xFF

        self._rbcp.write(I2C_TXR_ADDR, bytes([self._address|I2C_TXR_WR])) # present slave address, set write-bit
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_STA|I2C_CR_WR]))    # set command (start, write)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:        # check tip bit
            pass

        if with_internal_addr:
            self._rbcp.write(I2C_TXR_ADDR, bytes([internal_addr]))      # present internal address
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR]))           # set command (write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:    # check tip bit
               pass

        if (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_NORXACK:
            print("I2C ERROR: No acknowledge received")

        self._rbcp.write(I2C_TXR_ADDR, bytes([value & 0xFF]))           # present slave's data
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR]))               # set command (write)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:        # check tip bit
           pass

        self._rbcp.write(I2C_TXR_ADDR, bytes([(value >> 8) & 0xFF]))    # present slave's data
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR|I2C_CR_STO]))    # set command (write, stop)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:        # check tip bit
           pass
        # if with_internal_addr:
        #     self._logger.debug("Wrote 0x%04X to register pair 0x%02X, 0x%02X", value, internal_addr, internal_addr+1)
        # else:
        #     self._logger.debug("Wrote 0x%04X to register pair", value)

    def writeBytes(self, data, with_internal_addr = False, internal_addr = 0):
        """
        Write to i2c Device.
        :type register: int
        :param register: Register address to write.
        :type data: bytes or bytearray or str
        :param data: Write data (Python byte like object).
        """
        data = rbcp.to_bytes(data)
        internal_addr = internal_addr & 0xFF

        self._rbcp.write(I2C_TXR_ADDR, bytes([self._address|I2C_TXR_WR])) # present slave address, set write-bit
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_STA|I2C_CR_WR]))    # set command (start, write)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:        # check tip bit
            pass

        if with_internal_addr:
            self._rbcp.write(I2C_TXR_ADDR, bytes([internal_addr]))      # present internal address
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR]))           # set command (write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:    # check tip bit
               pass

        if (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_NORXACK:
            print("I2C ERROR: No acknowledge received")

        for i in range(len(data)-1):
            self._rbcp.write(I2C_TXR_ADDR, bytes([data[i]]))            # present slave's data
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR]))           # set command (write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:    # check tip bit
               pass

        self._rbcp.write(I2C_TXR_ADDR, bytes([data[len(data)-1]]))      # present slave's data
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR|I2C_CR_STO]))    # set command (write, stop)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:        # check tip bit
           pass
        # if with_internal_addr:
        #     self._logger.debug("Wrote to register 0x%02X: %s", internal_addr, data)
        # else:
        #     self._logger.debug("Wrote: %s", data)
        # 

    ###########################################################################
    # read
    def read8(self, with_internal_addr = False, internal_addr = 0):
        """Read an 8-bit value on the bus (without register)."""
        internal_addr = internal_addr & 0xFF
        if with_internal_addr:
            self._rbcp.write(I2C_TXR_ADDR, bytes([self._address|I2C_TXR_WR])) # present slave address, set write-bit
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_STA|I2C_CR_WR]))    # set command (start, write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:        # check tip bit
                pass

            self._rbcp.write(I2C_TXR_ADDR, bytes([internal_addr]))          # present internal address
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR]))               # set command (write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:        # check tip bit
                pass

        self._rbcp.write(I2C_TXR_ADDR, bytes([self._address|I2C_TXR_RD]))   # present slave address, set read-bit
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_STA|I2C_CR_WR]))        # set command (restart, write)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:            # check tip bit
            pass

        if (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_NORXACK:
            print("I2C ERROR: No acknowledge received")
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_RD|I2C_CR_NACK|I2C_CR_STO])) # set command (read, nack, stop)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:            # check tip bit
            pass
        result = self._rbcp.read(I2C_RXR_ADDR, 1)[0] & 0xFF
        # if with_internal_addr:
        #     self._logger.debug("Read 0x%02X from register 0x%02X", result, internal_addr)
        # else:
        #     self._logger.debug("Read 0x%02X", result)
        return result

    def read16(self, with_internal_addr = False, internal_addr = 0, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        internal_addr = internal_addr & 0xFF
        if with_internal_addr:
            self._rbcp.write(I2C_TXR_ADDR, bytes([self._address|I2C_TXR_WR]))   # present slave address, set write-bit
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_STA|I2C_CR_WR]))        # set command (start, write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:            # check tip bit
                pass

            self._rbcp.write(I2C_TXR_ADDR, bytes([internal_addr]))              # present internal address
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR]))                   # set command (write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:            # check tip bit
                pass

        self._rbcp.write(I2C_TXR_ADDR, bytes([self._address|I2C_TXR_RD]))       # present slave address, set read-bit
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_STA|I2C_CR_WR]))            # set command (restart, write)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:                # check tip bit
            pass

        if (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_NORXACK:
            print("I2C ERROR: No acknowledge received")

        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_RD]))                       # set command (read)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:                # check tip bit
            pass
        temp = self._rbcp.read(I2C_RXR_ADDR, 1)[0] 

        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_RD|I2C_CR_NACK|I2C_CR_STO]))# set command (read, nack, stop)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:                # check tip bit
            pass
        result = ((self._rbcp.read(I2C_RXR_ADDR, 1)[0] << 8) + temp) & 0xFFFF
        # if with_internal_addr:        
        #     self._logger.debug("Read 0x%04X from register pair 0x%02X, 0x%02X", result, internal_addr, internal_addr+1)
        # else:
        #     self._logger.debug("Read 0x%04X", result)

        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def readBytes(self, length, with_internal_addr = False, internal_addr = 0):
        """Read a length number of bytes from the specified register.  Results
        will be returned as a bytearray."""
        internal_addr = internal_addr & 0xFF
        if with_internal_addr:
            self._rbcp.write(I2C_TXR_ADDR, bytes([self._address|I2C_TXR_WR]))   # present slave address, set write-bit
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_STA|I2C_CR_WR]))        # set command (start, write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:            # check tip bit
                pass

            self._rbcp.write(I2C_TXR_ADDR, bytes([internal_addr]))              # present internal address
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_WR]))                   # set command (write)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:            # check tip bit
                pass

        self._rbcp.write(I2C_TXR_ADDR, bytes([self._address|I2C_TXR_RD]))       # present slave address, set read-bit
        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_STA|I2C_CR_WR]))            # set command (restart, write)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:                # check tip bit
            pass

        if (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_NORXACK:
            print("I2C ERROR: No acknowledge received")

        result = bytes()

        for i in range(length-1):
            self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_RD]))                   # set command (read)
            while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:            # check tip bit
                pass
            result += self._rbcp.read(I2C_RXR_ADDR, 1) 

        self._rbcp.write(I2C_CR_ADDR, bytes([I2C_CR_RD|I2C_CR_NACK|I2C_CR_STO]))# set command (start, write)
        while (self._rbcp.read(I2C_SR_ADDR, 1)[0]) & I2C_SR_TIP:                # check tip bit
            pass
        result += self._rbcp.read(I2C_RXR_ADDR, 1) 
        # if with_internal_addr:
        #     self._logger.debug("Read the following from register 0x%02X: %s", internal_addr, results)
        # else:
        #     self._logger.debug("Read the following: %s", results)
        return result
