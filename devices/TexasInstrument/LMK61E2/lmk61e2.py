import time
import smbus

#All register info concerning all LMK parameters
LMKParamInfo = {
#   addr, loc,    mask, regs, min,     max  (if min=max=0, read-only, min=max=1 Self-clearing)
    {            "VNDRID",   0,   0,   0xFFFF,   2,   0,       0}, # LMK61E2_VNDRID
    {            "PRODID",   2,   0,     0xFF,   1,   0,       0}, # LMK61E2_PRODID
    {             "REVID",   3,   0,     0xFF,   1,   0,       0}, # LMK61E2_REVID
    {          "SLAVEADR",   8,   1,     0xFE,   1,   0,       0}, # LMK61E2_SLAVEADR
    {             "EEREV",   9,   0,     0xFF,   1,   0,       0}, # LMK61E2_EEREV
    {           "PLL_PDN",  10,   6,     0x40,   1,   0,       1}, # LMK61E2_PLL_PDN
    {             "ENCAL",  10,   1,      0x2,   1,   1,       1}, # LMK61E2_ENCAL
    {          "AUTOSTRT",  10,   0,      0x1,   1,   0,       1}, # LMK61E2_AUTOSTRT
    {        "XO_CAPCTRL",  16,   0,   0xFF03,   2,   0,    1023}, # LMK61E2_XO_CAPCTRL    # warning: bits are positioned in oddly in registers
    {       "DIFF_OUT_PD",  21,   7,     0x80,   1,   0,       1}, # LMK61E2_DIFF_OUT_PD
    {           "OUT_SEL",  21,   0,      0x3,   1,   0,       3}, # LMK61E2_OUT_SEL
    {           "OUT_DIV",  22,   0,    0x1FF,   2,   5,     511}, # LMK61E2_OUT_DIV
    {              "NDIV",  25,   0,    0xFFF,   2,   1,    4095}, # LMK61E2_NDIV
    {           "PLL_NUM",  27,   0, 0x3FFFFF,   3,   0, 4194303}, # LMK61E2_PLL_NUM
    {           "PLL_DEN",  30,   0, 0x3FFFFF,   3,   1, 4194303}, # LMK61E2_PLL_DEN
    {      "PLL_DTHRMODE",  33,   2,      0xC,   1,   0,       3}, # LMK61E2_PLL_DTHRMODE    # Only certain values allowed
    {         "PLL_ORDER",  33,   0,      0x3,   1,   0,       3}, # LMK61E2_PLL_ORDER    # Only certain values allowed
    {             "PLL_D",  34,   5,     0x20,   1,   0,       1}, # LMK61E2_PLL_D
    {            "PLL_CP",  34,   0,      0xF,   1,   4,       8}, # LMK61E2_PLL_CP   # Only certain values allowed
    {"PLL_CP_PHASE_SHIFT",  35,   4,     0x70,   1,   0,       7}, # LMK61E2_PLL_CP_PHASE_SHIFT
    {     "PLL_ENABLE_C3",  35,   2,      0x4,   1,   0,       1}, # LMK61E2_PLL_ENABLE_C3
    {         "PLL_LF_R2",  36,   0,     0xFF,   1,   1,     255}, # LMK61E2_PLL_LF_R2
    {         "PLL_LF_C1",  37,   0,      0x7,   1,   0,       7}, # LMK61E2_PLL_LF_C1   # true value of C1 = 5 + 50*PLL_LF_C1
    {         "PLL_LF_R3",  38,   0,     0x7F,   1,   0,     127}, # LMK61E2_PLL_LF_R3
    {        "PLL_LF_C3 ",  39,   0,      0x7,   1,   0,       7}, # LMK61E2_PLL_LF_C3   # true value of C1 = 5 + 50*PLL_LF_C1
    {      "PLL_CLSDWAIT",  42,   2,      0xC,   1,   0,       3}, # LMK61E2_PLL_CLSDWAIT
    {       "PLL_VCOWAIT",  42,   0,      0x3,   1,   0,       3}, # LMK61E2_PLL_VCOWAIT
    {           "NVMSCRC",  47,   0,     0xFF,   1,   0,       0}, # LMK61E2_NVMSCRC
    {            "NVMCNT",  48,   0,     0xFF,   1,   0,       0}, # LMK61E2_NVMCNT
    {         "REGCOMMIT",  49,   6,     0x40,   1,   1,       1}, # LMK61E2_REGCOMMIT
    {         "NVMCRCERR",  49,   5,     0x20,   1,   0,       0}, # LMK61E2_NVMCRCERR
    {        "NVMAUTOCRC",  49,   4,     0x10,   1,   0,       1}, # LMK61E2_NVMAUTOCRC
    {         "NVMCOMMIT",  49,   3,      0x8,   1,   1,       1}, # LMK61E2_NVMCOMMIT
    {           "NVMBUSY",  49,   2,      0x4,   1,   0,       0}, # LMK61E2_NVMBUSY
    {          "NVMERASE",  49,   1,      0x2,   1,   1,       1}, # LMK61E2_NVMERASE
    {              "PROG",  49,   0,      0x1,   1,   1,       1}, # LMK61E2_PROG
    {            "MEMADR",  51,   0,     0x7F,   1,   0,     127}, # LMK61E2_MEMADR
    {            "NVMDAT",  52,   0,     0xFF,   1,   0,       0}, # LMK61E2_NVMDAT
    {            "RAMDAT",  53,   0,     0xFF,   1,   0,     255}, # LMK61E2_RAMDAT
    {           "NVMUNLK",  56,   0,     0xFF,   1,   0,     255}, # LMK61E2_NVMUNLK    # Protection to prevent inadvertent programming on EEPROM, trend carefully
    {               "LOL",  66,   1,      0x2,   1,   0,       0}, # LMK61E2_LOL
    {               "CAL",  66,   0,      0x1,   1,   0,       0}, # LMK61E2_CAL
    {           "SWR2PLL",  72,   1,      0x2,   1,   1,       1}  # LMK61E2_SWR2PLL
}

i2c_ch = 0

# lmk61e2 address on the I2C bus
i2c_address = 0x58

# Register addresses
VNDRID = 0x00


# Read temperature registers and calculate Celsius
def read_reg():

    # Read register
    val = bus.read_i2c_block_data(i2c_address, VNDRID, 2)

    return val

# Initialize I2C (SMBus)
bus = smbus.SMBus(i2c_ch)

read_reg()
