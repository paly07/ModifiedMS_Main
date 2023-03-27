#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <errno.h> // Error integer and strerror() function
#include <unistd.h>
#include <termios.h>
#include <linux/types.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>

int tle493d_write(int handle, unsigned char addr, unsigned char reg, unsigned char value);


int tle493d_write(int handle, unsigned char addr, unsigned char reg, unsigned char value) {
    unsigned char outbuf[2];
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[1];

    messages[0].addr  = addr;
    messages[0].flags = 0;
    messages[0].len   = sizeof(outbuf);
    messages[0].buf   = outbuf;

    outbuf[0] = reg;
    outbuf[1] = value;

    packets.msgs  = messages;
    packets.nmsgs = 1;
    if(ioctl(handle, I2C_RDWR, &packets) < 0) {
        return 0;
    }

    return 1;
}

int main(){

    int result;
    int i2c_hd;          /**< I2C interface handle*/


    const int freqHz = 400000;    /**< I2C frequency in Hz*/
    const int count = 7;
    unsigned char data[7];

    char devname[20];
    int dev_index = 1;

    snprintf(devname, 19, "/dev/i2c-%d", dev_index);
    i2c_hd = open(devname, O_RDWR);
    if(ioctl(i2c_hd, I2C_SLAVE, 53) < 0){
        printf("Error in creating handle \n \r");
        return 0;
    }

    
    // Configuring Mod1, for 1-byte read mode, clock stretching enabled, /INT disabled and Master Controlled mode, check FP bit odd parity between Mod2 & Mod1
    result = tle493d_write(i2c_hd, 0x35, 0x11, 0x15);
    if (result == 0){
        printf("Error in writing \n \r");
        return 0;
    }

    // Configuring Config, for Temp & Bz measuremnt enabled, ADC trigger on read before MSB, full range, no temperature compensation, check CP bit protected by even parity
    result = tle493d_write(i2c_hd, 0x35, 0x10, 0x11);
    if (result == 0){
        printf("Error in writing \n \r");
        return 0;
    }
    printf("Magnetic field values: \n \r");
    while(1){
        int bytes;
        //read first 7 data registers for measuring Bz, By, Bz
        bytes = read(i2c_hd, &data, 7);
        if( bytes != count){
            printf("bytes = %d", bytes);
            printf("Error in reading \n \r");
            return 0;
        }
        
        //12-bit data
        __int16_t X = (__int16_t)((data[0]<<8) | (data[4] & 0xF0)) >> 4;
        __int16_t Y = (__int16_t)((data[1]<<8) | ((data[4] & 0x0F) << 4)) >> 4;
        __int16_t Z = (__int16_t)((data[2]<<8) | ((data[5] & 0x0F) << 4)) >> 4;
        
        __uint16_t T = (data[3] << 4) | (data[5] >> 4);

        /*---------------------------------------------------------------------------------------------*/
        /*----------------------------------Enter your code here---------------------------------------*/
        /*---------------------------------------------------------------------------------------------*/

        printf("Bx = %d\t By = %d\t Bz = %d \n\r", X, Y, Z);
    }
}