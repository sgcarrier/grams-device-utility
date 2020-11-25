
import fcntl, struct, termios


driverFD = open("/dev/axi_dma_ic", 'rw')

if(driverFD == 0):
    print("Could not open dma. Exiting...")
    exit(2)

if (fcntl.ioctl(driverFD, termios.IOCTL_REINIT_DMA) != 0):
    print("ERROR: failed to reinitialize the axi dma peripheral. killing the dma-consumer.")
    exit(3)

print("INFO: resetting the dma callback stats.\n")
if (fcntl.ioctl(driverFD, termios.IOCTL_RESET_STATS) != 0):
    print("ERROR: failed to reset the dma callback stats.")