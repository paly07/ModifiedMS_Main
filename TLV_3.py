import pigpio
import math
from time import sleep
import numpy as np

class TLV493D:
    
    """Class of 3D Magnetic Sensor TLV493D.
    """
                                                                                                                                                      
      
    bx = 0
    by = 0
    bz = 0 
    temp = 0
    data =[]
    pi = pigpio.pi()

    addr = 0x35
    channel = 1
    parity_bit = ""
    bit2set = ""
    regData = [ 0x80,0x80, 0x80, 0x80, 0x00, 0x00,
                    0x60, 0x80, 0x7F, 0x80, 0x7F,0x80, 0x7F, 0x38, 0x38, 0x38,
                    0x01, 0x00, 0x00, 0x00, 0x00,0x00, 0xC9,]

    #regData = [resetValues[i] for i in range(23)]
    def set_regs(self, bit2set, data):
        #regValue = 0
        if bit2set =="FP":
            regValue = self.regData[17]
            regValue &= ~(0x80)
            regValue |= (data << 7) & 0x80
            self.regData[17] = regValue
        elif bit2set =="PR":
            regValue = self.regData[17]
            regValue &= ~(0x10)
            regValue |= (data<< 4) & 0x10
            self.regData[17] = regValue
        elif bit2set == "TRIG":
            regValue = self.regData[16]
            regValue &= ~(0x30)
            regValue |= (data<< 4) & 0x30
            self.regData[16] = regValue
        elif bit2set == "MCM":
            print(self.regData[17])
            regValue = self.regData[17]
            print(regValue)
            regValue &= ~(0x03)
            print(~(0x03))
            print(regValue)
            regValue |= (data<< 0) & 0x03
            print(regValue)
            self.regData[17] = regValue
    def calcParity(self, parity_bit):
        y = 0
        if ((parity_bit != "FP") and (parity_bit != "PR")):
            return

        elif parity_bit =="FP":
            self.set_regs("FP", 1)
            y ^= self.regData[17]
            y ^= self.regData[19] >> 5 #upper 3 bits
        
        elif (parity_bit == "CP"):
            
            for i in range(7,13):
                y ^= self.regData[i]
        
            y ^= (self.regData[13] & 0x7F)#ignoring WA
            y ^= (self.regData[14] & 0x3F)#ignoring TST
            y ^= (self.regData[15] & 0x3F)#ignoring PH
            y ^= self.regData[16]
        # combine all bits of this byte (assuming each register is one byte)
        y = y ^ (y >> 1)
        y = y ^ (y >> 2)
        y = y ^ (y >> 4)
        # parity is in the LSB of y
        self.set_regs(parity_bit, y & 0x01)
    
    h = pi.i2c_open(channel, addr)
    (count, data) = pi. i2c_read_device(h, 23)
    print(count,"             ",data)
    
    
    

    def initialize(self): 
        """ Read data from register
        """
        global data
        #self.bus.write_byte_data(self.addr, 0x05,0x20)
        # self.regData[17] = 20
        # self.calcParity("FP")
        # print("Mod_1 Reg:", self.regData[17])
        # self.pi.i2c_write_byte_data(self.h, 0x11, self.regData[17])
        # self.pi.i2c_write_byte_data(self.h, 0x11, self.regData[17])
        # # rdata = self.pi.i2c_read_i2c_block_data(self.h, 0x00, 23)
        # # print(rdata)
        # # self.regData = [rdata[i] for i in range(24)]
        # self.set_regs("MCM", 1)
        # self.set_regs("TRIG", 1)
        # self.calcParity("CP")
        # self.calcParity("FP")
        # print("Mod_1 Reg:", self.regData[17])
        # print("Config Reg:", self.regData[16])
        # self.pi.i2c_write_byte_data(self.h, 0x10, self.regData[16])
        # self.pi.i2c_write_byte_data(self.h, 0x11, self.regData[17])
        # self.pi.i2c_write_byte_data(self.h, 0x10, self.regData[16])
        # self.pi.i2c_write_byte_data(self.h, 0x11, self.regData[17])
        # sleep(1)
        self.pi.i2c_write_byte_data(self.h, 0x11, 21)
        self.pi.i2c_write_byte_data(self.h, 0x10, 32)
        sleep(60e-6)
        (count, data) = self.pi.i2c_read_device(self.h, 23)
        print(data) 
        #
        #data = self.bus.read_i2c_block_data(self.addr, 0x00, 10)
    def initialize_FM(self):
        self.pi.i2c_write_byte_data(self.h, 0x11, 0x13)
        self.pi.i2c_write_byte_data(self.h, 0x10, 0x00)
        sleep(60e-6)
    def update_data (self):
        global data
        (count, data) = self.pi.i2c_read_device(self.h, 6)
        print(data) 

    def get_x(self):
        """ Get the value of X coordinate
            
            Returns:
            
            int: X coordinate
        """
        
        self.bx = (data[0] << 8) or (((data[4] >> 4) & 0x0f)<<4)
        self.bx >>= 4
        
        self.bx *=0.13
            
        return self.bx
    
    
    
    
    def get_y(self):
        """ Get the value of Y coordinate
            
            Returns:
            
            int: Y coordinate
        """
        self.by = (data[1] << 8) or ((data[4] & 0x0f)<<4)
        self.by >>= 4
        
        self.by *=0.13          
        return self.by
    
    
    
    
    def get_z(self):
        """ Get the value of Z coordinate
            
            Returns:
            
            int: Z coordinate
        """
        
        self.bz = (data[2] << 8) or ((data[5] & 0x0f)<<4)
        
        self.bz >>= 4
        
        self.bz *=0.13
        return self.bz
    
    
    
    def get_br(self):
        """ Calculate the radial value
            
            Returns:
            
            double : radial value
        """
        
        br = math.sqrt(self.bx*self.bx+self.by*self.by+self.bz*self.bz)
        
        return br
    
    
    
    
    def get_polar(self):
        """ Calculate the polar value
            
            Returns:
            
            double: polar value
        """
        
        polar = math.cos(math.atan2(self.bz,math.sqrt(self.bx*self.bx+self.by*self.by)))
        
        return polar
    
    
    
    
    def get_azimuth(self):
        """ Calculate the azimuthal value
            
            Returns:
            
            double: azimuthal value
        """
        
        azimuth = math.atan2(self.by,self.bx)
        
        return azimuth
  


def main():
    tlv493d = TLV493D()
    tlv493d.initialize()
    tlv493d.initialize()
    while True:
        tlv493d.update_data()
        x = tlv493d.get_x()
        y = tlv493d.get_y()
        z = tlv493d.get_z()

        print("x: ", x, "y: ", y, "z: ",z)
        sleep (500e-6)

if __name__ =="__main__":
    main()