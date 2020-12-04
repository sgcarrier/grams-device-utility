
import fcntl, struct, termios, mmap
import logging

_logger = logging.getLogger(__name__)

# number of block of data in the circular DMA
DMA_BUFFER_BLOCK_COUNT = 16
# number of bytes in DMA data
DMA_DATA_BYTE_SIZE = 8
# How many megabytes (MB) the dma will use per block (for performance improvement)
DMA_BUFFER_BLOCK_MB = 8
DMA_BUFFER_BLOCK_MAX_DMA_DATA_QTY = DMA_BUFFER_BLOCK_MB * (1024*1024) / DMA_DATA_BYTE_SIZE


C_DMA_PERIOD_SIZE = DMA_BUFFER_BLOCK_MAX_DMA_DATA_QTY
C_DMA_PERIOD_COUNT = DMA_BUFFER_BLOCK_COUNT
C_DMA_DATA_BYTE_LEN = DMA_DATA_BYTE_SIZE

C_BUFFER_SIZE = C_DMA_PERIOD_SIZE * C_DMA_PERIOD_COUNT * C_DMA_DATA_BYTE_LEN


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


circularBuffer = mmap.mmap(0, C_BUFFER_SIZE, mmap.PROT_READ | mmap.PROT_WRITE, mmap.MAP_SHARED, driverFD, 0)

if circularBuffer == 0:
    _logger.error("circularBuffer not mapped correctly")
    exit(4)
elif circularBuffer == -1:
    _logger.error("Circular buffer is -1")
    exit(5)
else:
    _logger.info("Mapped " + str(C_BUFFER_SIZE) + "bytes using mmap")

_logger.info("ready to receive the first valid transfer info from the dma")

driverFD.close()