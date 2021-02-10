import time
import logging
from periphery import SPI, GPIO

_logger = logging.getLogger(__name__)

class LMK04610:

    DEVICE_NAME = "LMK04610"

    #All register info concerning all LMK parameters
    REGISTERS_INFO = {
    #  if min=max=0, read-only, min=max=1 Self-clearing)
                        "SWRST_CPY": { "addr":   0x00, "loc":  0, "mask":   0x01, "regs": 1, "min": 1, "max":   1},  # RESET,
                    "LSB_FIRST_CPY": { "addr":   0x00, "loc":  1, "mask":   0x02, "regs": 1, "min": 1, "max":   1},  # LSB_FIRST_CPY,
                  "ADDR_ASCEND_CPY": { "addr":   0x00, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":   1},  #ADDR_ASCEND_CPY,
                   "SDO_ACTIVE_CPY": { "addr":   0x00, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":   1},  #SDO_ACTIVE_CPY,
                       "SDO_ACTIVE": { "addr":   0x00, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":   1},  #SDO_ACTIVE,
                      "ADDR_ASCEND": { "addr":   0x00, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":   1},  #ADDR_ASCEND,
                        "LSB_FIRST": { "addr":   0x00, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":   1},  #LSB_FIRST,
                            "SWRST": { "addr":   0x00, "loc":  7, "mask":   0x80, "regs": 1, "min": 1, "max":   1},  #SWRST,
                         "CHIPTYPE": { "addr":   0x03, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":   0},  # CHIPTYPE,
                            "DEVID": { "addr":   0x03, "loc":  6, "mask":   0xC0, "regs": 1, "min": 0, "max":   0},  # DEVID,
                           "CHIPID": { "addr":   0x04, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   0},  #CHIPID,
                          "CHIPVER": { "addr":   0x06, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":   0},  # CHIPVER,
                         "VENDORID": { "addr":   0x0C, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":   0},  # VENDORID,
                           "PLL1EN": { "addr":   0x10, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":   1},  # PLL1EN,
                           "PLL2EN": { "addr":   0x10, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":   1},  # PLL2EN,
                         "CH1TO5EN": { "addr":   0x10, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":   1},  # CH1TO5EN,
                        "CH6TO10EN": { "addr":   0x10, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":   1},  # CH6TO10EN,
               "CLKINBLK_LOSLDO_EN": { "addr":   0x10, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":   1},  # CLKINBLK_LOSLDO_EN,
                       "OUTCH_MUTE": { "addr":   0x10, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":   1},  # OUTCH_MUTE,
                      "DEV_STARTUP": { "addr":   0x11, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":   1},  # DEV_STARTUP,
                  "PORCLKAFTERLOCK": { "addr":   0x12, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":   1},  # PORCLKAFTERLOCK,
                  "PLL2_DIG_CLK_EN": { "addr":   0x12, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":   1},  # PLL2_DIG_CLK_EN,
                       "DIG_CLK_EN": { "addr":   0x12, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":   1},  # DIG_CLK_EN,
              "PLL2_REF_DIGCLK_DIV": { "addr":   0x13, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":  31},  # PLL2_REF_DIGCLK_DIV,
                      "GLOBAL_SYNC": { "addr":   0x14, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":   1},  # GLOBAL_SYNC,
                    "SYNC_PIN_FUNC": { "addr":   0x14, "loc":  1, "mask":   0x06, "regs": 1, "min": 0, "max":   3},  # SYNC_PIN_FUNC,
          "INV_SYNC_INPUT_SYNC_CLK": { "addr":   0x14, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":   1},  # INV_SYNC_INPUT_SYNC_CLK,
                    "GLOBAL_SYSREF": { "addr":   0x14, "loc":  4, "mask":   0x10, "regs": 1, "min": 1, "max":   1},  # GLOBAL_SYSREF,
               "GLOBAL_CONT_SYSREF": { "addr":   0x14, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":   1},  # GLOBAL_CONT_SYSREF,
                 "EN_SYNC_PIN_FUNC": { "addr":   0x14, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":   1},  # EN_SYNC_PIN_FUNC,
                    "CLKINSEL1_INV": { "addr":   0x15, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # CLKINSEL1_INV,
                      "CLKIN_SWRST": { "addr":   0x15, "loc":  2, "mask":   0x04, "regs": 1, "min": 1, "max":       1},  # CLKIN_SWRST,
                 "CLKIN_STAGGER_EN": { "addr":   0x15, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # CLKIN_STAGGER_EN,
          "CLKINBLK_EN_BUF_BYP_PLL": { "addr":   0x16, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # CLKINBLK_EN_BUF_BYP_PLL,
          "CLKINBLK_EN_BUF_CLK_PLL": { "addr":   0x16, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # CLKINBLK_EN_BUF_CLK_PLL,
                   "CLKINSEL1_MODE": { "addr":   0x16, "loc":  5, "mask":   0x60, "regs": 1, "min": 0, "max":       2},  # CLKINSEL1_MODE,
                  "CLKINBLK_ALL_EN": { "addr":   0x16, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # CLKINBLK_ALL_EN,
                      "CLKIN0_PRIO": { "addr":   0x19, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":       4},  # CLKIN0_PRIO,
                   "CLKIN0_SE_MODE": { "addr":   0x19, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # CLKIN0_SE_MODE,
                        "CLKIN0_EN": { "addr":   0x19, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # CLKIN0_EN,
            "CLKIN0_LOS_FRQ_DBL_EN": { "addr":   0x19, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # CLKIN0_LOS_FRQ_DBL_EN,
                  "CLKIN0_PLL1_INV": { "addr":   0x19, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # CLKIN0_PLL1_INV,
                      "CLKIN1_PRIO": { "addr":   0x1A, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":       4},  # CLKIN1_PRIO,
                   "CLKIN1_SE_MODE": { "addr":   0x1A, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # CLKIN1_SE_MODE,
                        "CLKIN1_EN": { "addr":   0x1A, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # CLKIN1_EN,
            "CLKIN1_LOS_FRQ_DBL_EN": { "addr":   0x1A, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # CLKIN1_LOS_FRQ_DBL_EN,
                  "CLKIN1_PLL1_INV": { "addr":   0x1A, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # CLKIN1_PLL1_INV,
                 "CLKIN0_PLL1_RDIV": { "addr":   0x1F, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # CLKIN0_PLL1_RDIV,
                 "CLKIN1_PLL1_RDIV": { "addr":   0x21, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # CLKIN1_PLL1_RDIV,
               "CLKIN0_LOS_REC_CNT": { "addr":   0x27, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CLKIN0_LOS_REC_CNT,
               "CLKIN0_LOS_LAT_SEL": { "addr":   0x28, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CLKIN0_LOS_LAT_SEL,
               "CLKIN1_LOS_REC_CNT": { "addr":   0x29, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CLKIN1_LOS_REC_CNT,
               "CLKIN1_LOS_LAT_SEL": { "addr":   0x2A, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CLKIN1_LOS_LAT_SEL,
                    "SW_CLKLOS_TMR": { "addr":   0x2B, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":      31},  # SW_CLKLOS_TMR,
                    "SW_LOS_CH_SEL": { "addr":   0x2C, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":      15},  # RISE_VALID_PRI,
                      "SW_REFINSEL": { "addr":   0x2C, "loc":  4, "mask":   0xF0, "regs": 1, "min": 0, "max":      15},  # FALL_VALID_PRI,
                 "SW_ALLREFSON_TMR": { "addr":   0x2D, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":      31},  # SW_ALLREFSON_TMR,
                 "OSCIN_BUF_LOS_EN": { "addr":   0x2E, "loc":  0, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # OSCIN_BUF_LOS_EN,
                 "OSCIN_BUF_REF_EN": { "addr":   0x2E, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # OSCIN_BUF_REF_EN,
              "OSCIN_OSCINSTAGE_EN": { "addr":   0x2E, "loc":  2, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OSCIN_OSCINSTAGE_EN,
           "OSCIN_BUF_TO_OSCOUT_EN": { "addr":   0x2E, "loc":  3, "mask":   0xC0, "regs": 1, "min": 0, "max":       1},  # OSCIN_BUF_TO_OSCOUT_EN,
                    "OSCIN_SE_MODE": { "addr":   0x2E, "loc":  4, "mask":   0x30, "regs": 1, "min": 0, "max":       1},  # OSCIN_SE_MODE,
                     "OSCIN_PD_LDO": { "addr":   0x2E, "loc":  5, "mask":   0x0C, "regs": 1, "min": 0, "max":       1},  # OSCIN_PD_LDO,
                   "OSCOUT_SEL_SRC": { "addr":   0x2F, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OSCOUT_SEL_SRC,
                     "OSCOUT_SWRST": { "addr":   0x2F, "loc":  1, "mask":   0x02, "regs": 1, "min": 1, "max":       1},  # OSCOUT_SWRST,
                 "OSCOUT_DIV_CLKEN": { "addr":   0x2F, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # OSCOUT_DIV_CLKEN,
                   "OSCOUT_SEL_VBG": { "addr":   0x2F, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # OSCOUT_SEL_VBG,
                "OSCOUT_PINSEL_DIV": { "addr":   0x2F, "loc":  4, "mask":   0x30, "regs": 1, "min": 0, "max":       0},  # OSCOUT_PINSEL_DIV,
            "OSCOUT_DIV_REGCONTROL": { "addr":   0x2F, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OSCOUT_DIV_REGCONTROL,
         "OSCOUT_LVCMOS_WEAK_DRIVE": { "addr":   0x2F, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OSCOUT_LVCMOS_WEAK_DRIVE,
                       "OSCOUT_DIV": { "addr":   0x30, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # OSCOUT_DIV,
                  "OSCOUT_DRV_MODE": { "addr":   0x31, "loc":  0, "mask":   0x3F, "regs": 1, "min": 0, "max":      63},  # OSCOUT_DRV_MODE,
                  "OSCOUT_DRV_MUTE": { "addr":   0x31, "loc":  6, "mask":   0xC0, "regs": 1, "min": 0, "max":       3},  # OSCOUT_DRV_MUTE,
                        "CH1_SWRST": { "addr":   0x32, "loc":  0, "mask":   0x01, "regs": 1, "min": 1, "max":       1},  # CH1_SWRST,
                        "CH2_SWRST": { "addr":   0x32, "loc":  1, "mask":   0x02, "regs": 1, "min": 1, "max":       1},  # CH2_SWRST,
                       "CH34_SWRST": { "addr":   0x32, "loc":  2, "mask":   0x04, "regs": 1, "min": 1, "max":       1},  # CH34_SWRST,
                        "CH5_SWRST": { "addr":   0x32, "loc":  3, "mask":   0x08, "regs": 1, "min": 1, "max":       1},  # CH5_SWRST,
                        "CH6_SWRST": { "addr":   0x32, "loc":  4, "mask":   0x10, "regs": 1, "min": 1, "max":       1},  # CH6_SWRST,
                       "CH78_SWRST": { "addr":   0x32, "loc":  5, "mask":   0x20, "regs": 1, "min": 1, "max":       1},  # CH78_SWRST,
                        "CH9_SWRST": { "addr":   0x32, "loc":  6, "mask":   0x40, "regs": 1, "min": 1, "max":       1},  # CH9_SWRST,
                       "CH10_SWRST": { "addr":   0x32, "loc":  7, "mask":   0x80, "regs": 1, "min": 1, "max":       1},  # CH10_SWRST,
                  "OUTCH1_LDO_MASK": { "addr":   0x33, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH1_LDO_MASK,
              "OUTCH1_LDO_BYP_MODE": { "addr":   0x33, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH1_LDO_BYP_MODE,
                 "OUTCH1_DIV_CLKEN": { "addr":   0x34, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH1_DIV_CLKEN,
                   "DIV_DCC_EN_CH1": { "addr":   0x34, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH1,
                 "OUTCH1_DRIV_MODE": { "addr":   0x34, "loc":  2, "mask":   0xFC, "regs": 1, "min": 0, "max":      63},  # OUTCH1_DRIV_MODE,
                 "OUTCH2_DRIV_MODE": { "addr":   0x35, "loc":  0, "mask":   0x2F, "regs": 1, "min": 0, "max":      63},  # OUTCH2_DRIV_MODE,
                  "OUTCH2_LDO_MASK": { "addr":   0x35, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH2_LDO_MASK,
              "OUTCH2_LDO_BYP_MODE": { "addr":   0x35, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH2_LDO_BYP_MODE,
                 "OUTCH2_DIV_CLKEN": { "addr":   0x36, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH2_DIV_CLKEN,
                   "DIV_DCC_EN_CH2": { "addr":   0x36, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH2,
                "OUTCH34_DRIV_MODE": { "addr":   0x37, "loc":  0, "mask":   0x2F, "regs": 1, "min": 0, "max":      63},  # OUTCH34_DRIV_MODE,
                 "OUTCH34_LDO_MASK": { "addr":   0x37, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH34_LDO_MASK,
             "OUTCH34_LDO_BYP_MODE": { "addr":   0x37, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH34_LDO_BYP_MODE,
                "OUTCH34_DIV_CLKEN": { "addr":   0x38, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH34_DIV_CLKEN,
                 "DIV_DCC_EN_CH3_4": { "addr":   0x38, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH3_4,
                 "OUTCH4_DRIV_MODE": { "addr":   0x38, "loc":  2, "mask":   0xFC, "regs": 1, "min": 0, "max":      63},  # OUTCH4_DRIV_MODE,
                 "OUTCH5_DRIV_MODE": { "addr":   0x39, "loc":  0, "mask":   0x2F, "regs": 1, "min": 0, "max":      63},  # OUTCH5_DRIV_MODE,
                  "OUTCH5_LDO_MASK": { "addr":   0x39, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH5_LDO_MASK,
              "OUTCH5_LDO_BYP_MODE": { "addr":   0x39, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH5_LDO_BYP_MODE,
                 "OUTCH5_DIV_CLKEN": { "addr":   0x3A, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH5_DIV_CLKEN,
                   "DIV_DCC_EN_CH5": { "addr":   0x3A, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH5,
                  "OUTCH6_LDO_MASK": { "addr":   0x3B, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH6_LDO_MASK,
              "OUTCH6_LDO_BYP_MODE": { "addr":   0x3B, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH6_LDO_BYP_MODE,
                 "OUTCH6_DIV_CLKEN": { "addr":   0x3C, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH6_DIV_CLKEN,
                   "DIV_DCC_EN_CH6": { "addr":   0x3C, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH6,
                 "OUTCH6_DRIV_MODE": { "addr":   0x3C, "loc":  2, "mask":   0xFC, "regs": 1, "min": 0, "max":      63},  # OUTCH6_DRIV_MODE,
                 "OUTCH7_DRIV_MODE": { "addr":   0x3D, "loc":  0, "mask":   0x2F, "regs": 1, "min": 0, "max":      63},  # OUTCH7_DRIV_MODE,
                 "OUTCH78_LDO_MASK": { "addr":   0x3D, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH78_LDO_MASK,
             "OUTCH78_LDO_BYP_MODE": { "addr":   0x3D, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH78_LDO_BYP_MODE,
                "OUTCH78_DIV_CLKEN": { "addr":   0x3E, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH78_DIV_CLKEN,
                 "DIV_DCC_EN_CH7_8": { "addr":   0x3E, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH7_8,
                 "OUTCH8_DRIV_MODE": { "addr":   0x3E, "loc":  2, "mask":   0xFC, "regs": 1, "min": 0, "max":      63},  # OUTCH8_DRIV_MODE,
                  "OUTCH9_LDO_MASK": { "addr":   0x3F, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH9_LDO_MASK,
              "OUTCH9_LDO_BYP_MODE": { "addr":   0x3F, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH9_LDO_BYP_MODE,
                 "OUTCH9_DIV_CLKEN": { "addr":   0x40, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH9_DIV_CLKEN,
                   "DIV_DCC_EN_CH9": { "addr":   0x40, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH9,
                 "OUTCH9_DRIV_MODE": { "addr":   0x40, "loc":  2, "mask":   0xFC, "regs": 1, "min": 0, "max":      63},  # OUTCH9_DRIV_MODE,
                "OUTCH10_DRIV_MODE": { "addr":   0x41, "loc":  0, "mask":   0x2F, "regs": 1, "min": 0, "max":      63},  # OUTCH10_DRIV_MODE,
                 "OUTCH10_LDO_MASK": { "addr":   0x41, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH10_LDO_MASK,
             "OUTCH10_LDO_BYP_MODE": { "addr":   0x41, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH10_LDO_BYP_MODE,
                "OUTCH10_DIV_CLKEN": { "addr":   0x42, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH10_DIV_CLKEN,
                  "DIV_DCC_EN_CH10": { "addr":   0x42, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH10,
                       "OUTCH1_DIV": { "addr":   0x43, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # OUTCH1_DIV,
                       "OUTCH2_DIV": { "addr":   0x45, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # OUTCH2_DIV,
                      "OUTCH34_DIV": { "addr":   0x47, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # OUTCH34_DIV,
                       "OUTCH5_DIV": { "addr":   0x49, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # OUTCH5_DIV,
                       "OUTCH6_DIV": { "addr":   0x4B, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # OUTCH6_DIV,
                      "OUTCH78_DIV": { "addr":   0x4D, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # OUTCH78_DIV,
                       "OUTCH9_DIV": { "addr":   0x4F, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # OUTCH9_DIV,
                      "OUTCH10_DIV": { "addr":   0x51, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # OUTCH10_DIV,
                   "OUTCH1_DIV_INV": { "addr":   0x53, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH1_DIV_INV,
                   "OUTCH2_DIV_INV": { "addr":   0x53, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # OUTCH2_DIV_INV,
                  "OUTCH34_DIV_INV": { "addr":   0x53, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # OUTCH34_DIV_INV,
                   "OUTCH5_DIV_INV": { "addr":   0x53, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # OUTCH5_DIV_INV,
                   "OUTCH6_DIV_INV": { "addr":   0x53, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # OUTCH6_DIV_INV,
                  "OUTCH78_DIV_INV": { "addr":   0x53, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # OUTCH78_DIV_INV,
                   "OUTCH9_DIV_INV": { "addr":   0x53, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH9_DIV_INV,
                  "OUTCH10_DIV_INV": { "addr":   0x53, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH10_DIV_INV,
                "PLL1_LDO_WAIT_TMR": { "addr":   0x54, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":      15},  # PLL1_LDO_WAIT_TMR,
                "PLL1_DIR_POS_GAIN": { "addr":   0x54, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL1_DIR_POS_GAIN,
                       "PLL1_PD_LD": { "addr":   0x54, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # PLL1_PD_LD,
               "PLL1_EN_REGULATION": { "addr":   0x54, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # PLL1_EN_REGULATION,
                        "PLL1_F_30": { "addr":   0x54, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # PLL1_F_30,
           "PLL1_PFD_DOWN_HOLDOVER": { "addr":   0x55, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # PLL1_PFD_DOWN_HOLDOVER,
             "PLL1_PFD_UP_HOLDOVER": { "addr":   0x55, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # PLL1_PFD_UP_HOLDOVER,
                     "PLL1_BYP_LOS": { "addr":   0x55, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # PLL1_BYP_LOS,
                   "PLL1_FBCLK_INV": { "addr":   0x55, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL1_FBCLK_INV,
             "PLL1_LCKDET_LOS_MASK": { "addr":   0x55, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # PLL1_LCKDET_LOS_MASK,
                   "PLL1_FAST_LOCK": { "addr":   0x55, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # PLL1_FAST_LOCK,
                "PLL1_LCKDET_BY_32": { "addr":   0x55, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # PLL1_LCKDET_BY_32,
                    "PLL1_NDIV_4CY": { "addr":   0x56, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # PLL1_NDIV_4CY,
                  "PLL1_NDIV_CLKEN": { "addr":   0x56, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # PLL1_NDIV_CLKEN,
                    "PLL1_RDIV_4CY": { "addr":   0x56, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # PLL1_RDIV_4CY,
                  "PLL1_RDIV_CLKEN": { "addr":   0x56, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # PLL1_RDIV_CLKEN,
                 "PLL1_LOL_NORESET": { "addr":   0x56, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL1_LOL_NORESET,
                       "PLL1_SWRST": { "addr":   0x57, "loc":  0, "mask":   0x01, "regs": 1, "min": 1, "max":       1},  # PLL1_SWRST,
      "PLL1_HOLDOVER_LOCKDET_SWRST": { "addr":   0x57, "loc":  1, "mask":   0x02, "regs": 1, "min": 1, "max":       1},  # PLL1_HOLDOVER_LOCKDET_SWRST,
           "PLL1_HOLDOVERCNT_SWRST": { "addr":   0x57, "loc":  2, "mask":   0x04, "regs": 1, "min": 1, "max":       1},  # PLL1_HOLDOVERCNT_SWRST,
                  "PLL1_NDIV_SWRST": { "addr":   0x57, "loc":  3, "mask":   0x08, "regs": 1, "min": 1, "max":       1},  # PLL1_NDIV_SWRST,
                  "PLL1_RDIV_SWRST": { "addr":   0x57, "loc":  4, "mask":   0x10, "regs": 1, "min": 1, "max":       1},  # PLL1_RDIV_SWRST,
          "PLL1_HOLDOVER_DLD_SWRST": { "addr":   0x57, "loc":  5, "mask":   0x20, "regs": 1, "min": 1, "max":       1},  # PLL1_HOLDOVER_DLD_SWRST,
                "PLL1_LD_WNDW_SIZE": { "addr":   0x58, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # PLL1_LD_WNDW_SIZE,
                        "PLL1_INTG": { "addr":   0x59, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":      15},  # PLL1_INTG,
                     "PLL1_INTG_FL": { "addr":   0x59, "loc":  4, "mask":   0xF0, "regs": 1, "min": 0, "max":      15},  # PLL1_INTG_FL,
                        "PLL1_PROP": { "addr":   0x5A, "loc":  0, "mask":   0x7F, "regs": 1, "min": 0, "max":     127},  # PLL1_PROP,
                     "PLL1_PROP_FL": { "addr":   0x5B, "loc":  0, "mask":   0x7F, "regs": 1, "min": 0, "max":     127},  # PLL1_PROP_FL,
         "PLL1_HOLDOVER_RAILDET_EN": { "addr":   0x5C, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # PLL1_HOLDOVER_RAILDET_EN,
        "PLL1_HOLDOVER_LCKDET_MASK": { "addr":   0x5C, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # PLL1_HOLDOVER_LCKDET_MASK,
           "PLL1_HOLDOVER_LOS_MASK": { "addr":   0x5C, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # PLL1_HOLDOVER_LOS_MASK,
         "PLL1_HOLDOVER_MAX_CNT_EN": { "addr":   0x5C, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # PLL1_HOLDOVER_MAX_CNT_EN,
          "PLL1_HOLDOVER_RAIL_MODE": { "addr":   0x5C, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL1_HOLDOVER_RAIL_MODE,
              "PLL1_HOLDOVER_FORCE": { "addr":   0x5C, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # PLL1_HOLDOVER_FORCE,
         "PLL1_STARTUP_HOLDOVER_EN": { "addr":   0x5C, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # PLL1_STARTUP_HOLDOVER_EN,
                 "PLL1_HOLDOVER_EN": { "addr":   0x5C, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # PLL1_HOLDOVER_EN,
            "PLL1_HOLDOVER_MAX_CNT": { "addr":   0x5D, "loc":  0, "mask":   0xFFFFFFFF, "regs": 1, "min": 0, "max":  0xFFFFFFFF},  # PLL1_HOLDOVER_MAX_CNT,
                        "PLL1_NDIV": { "addr":   0x61, "loc":  0, "mask":   0xFFFF, "regs": 1, "min": 0, "max": 65535},  # PLL1_NDIV,
             "PLL1_LOCKDET_CYC_CNT": { "addr":   0x63, "loc":  0, "mask":   0xFFFFFF, "regs": 1, "min": 0, "max":  0xFFFFFF},  # PLL1_LOCKDET_CYC_CNT,
                "PLL1_STORAGE_CELL": { "addr":   0x66, "loc":  0, "mask":   0xFFFFFFFFFF, "regs": 1, "min": 0, "max":  0xFFFFFFFFFF},  # PLL1_STORAGE_CELL,
                  "PLL1_RC_CLK_DIV": { "addr":   0x6B, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":       7},  # PLL1_RC_CLK_DIV,
                   "PLL1_RC_CLK_EN": { "addr":   0x6B, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL1_RC_CLK_EN,
                  "PLL2_GLOBAL_BYP": { "addr":   0x6C, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # PLL2_GLOBAL_BYP,
                     "PLL2_BYP_BOT": { "addr":   0x6C, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # PLL2_BYP_BOT,
                     "PLL2_BYP_TOP": { "addr":   0x6C, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # PLL2_BYP_TOP,
                     "PLL2_BYP_OSC": { "addr":   0x6C, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # PLL2_BYP_OSC,
         "PLL2_VCO_PRESC_LOW_POWER": { "addr":   0x6C, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL2_VCO_PRESC_LOW_POWER,
                       "PLL2_PD_LD": { "addr":   0x6D, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # PLL2_PD_LD,
                 "PLL2_RDIV_DBL_EN": { "addr":   0x6D, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # PLL2_RDIV_DBL_EN,
             "PLL2_LCKDET_LOS_MASK": { "addr":   0x6D, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # PLL2_LCKDET_LOS_MASK,
                  "PLL2_SMART_TRIM": { "addr":   0x6D, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # PLL2_SMART_TRIM,
                  "PLL2_PD_VARBIAS": { "addr":   0x6D, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL2_PD_VARBIAS,
                  "PLL2_DBL_EN_INV": { "addr":   0x6D, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # PLL2_DBL_EN_INV,
                    "PLL2_RDIV_BYP": { "addr":   0x6D, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # PLL2_RDIV_BYP,
                "PLL2_EN_PULSE_GEN": { "addr":   0x6D, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # PLL2_EN_PULSE_GEN,
           "PLL2_EN_BUF_CLK_BOTTOM": { "addr":   0x6E, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # PLL2_EN_BUF_CLK_BOTTOM,
              "PLL2_EN_BUF_CLK_TOP": { "addr":   0x6E, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # PLL2_EN_BUF_CLK_TOP,
               "PLL2_EN_BUF_OSCOUT": { "addr":   0x6E, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # PLL2_EN_BUF_OSCOUT,
          "PLL2_EN_BUF_SYNC_BOTTOM": { "addr":   0x6E, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # PLL2_EN_BUF_SYNC_BOTTOM,
             "PLL2_EN_BUF_SYNC_TOP": { "addr":   0x6E, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL2_EN_BUF_SYNC_TOP,
                  "PLL2_EN_BYP_BUF": { "addr":   0x6E, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # PLL2_EN_BYP_BUF,
             "PLL2_BYP_SYNC_BOTTOM": { "addr":   0x6E, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # PLL2_BYP_SYNC_BOTTOM,
                "PLL2_BYP_SYNC_TOP": { "addr":   0x6E, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # PLL2_BYP_SYNC_TOP,
                       "PLL2_SWRST": { "addr":   0x6F, "loc":  0, "mask":   0x01, "regs": 1, "min": 1, "max":       1},  # PLL2_SWRST,
                  "PLL2_NDIV_SWRST": { "addr":   0x6F, "loc":  1, "mask":   0x02, "regs": 1, "min": 1, "max":       1},  # PLL2_NDIV_SWRST,
                  "PLL2_RDIV_SWRST": { "addr":   0x6F, "loc":  2, "mask":   0x04, "regs": 1, "min": 1, "max":       1},  # PLL2_RDIV_SWRST,
                   "PLL2_R4_LF_SEL": { "addr":   0x70, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":      15},  # PLL2_R4_LF_SEL,
                   "PLL2_C4_LF_SEL": { "addr":   0x70, "loc":  4, "mask":   0xF0, "regs": 1, "min": 0, "max":      15},  # PLL2_C4_LF_SEL,
                   "PLL2_R3_LF_SEL": { "addr":   0x71, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":      15},  # PLL2_R3_LF_SEL,
                   "PLL2_C3_LF_SEL": { "addr":   0x71, "loc":  4, "mask":   0xF0, "regs": 1, "min": 0, "max":      15},  # PLL2_C3_LF_SEL,
                        "PLL2_PROP": { "addr":   0x72, "loc":  0, "mask":   0x3F, "regs": 1, "min": 0, "max":      63},  # PLL2_PROP,
                        "PLL2_NDIV": { "addr":   0x73, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # PLL2_NDIV,
                        "PLL2_RDIV": { "addr":   0x75, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # PLL2_RDIV,
                "PLL2_STRG_INITVAL": { "addr":   0x77, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # PLL2_STRG_INITVAL,
                      "RAILDET_UPP": { "addr":   0x7D, "loc":  0, "mask":   0x3F, "regs": 1, "min": 0, "max":      63},  # RAILDET_UPP,
                      "RAILDET_LOW": { "addr":   0x7E, "loc":  0, "mask":   0x3F, "regs": 1, "min": 0, "max":      63},  # RAILDET_LOW,
                   "PLL2_FAST_ACAL": { "addr":   0x7F, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # PLL2_FAST_ACAL,
                      "PLL2_AC_REQ": { "addr":   0x7F, "loc":  1, "mask":   0x02, "regs": 1, "min": 1, "max":       1},  # PLL2_AC_REQ,
               "PLL2_IDACSET_RECAL": { "addr":   0x7F, "loc":  2, "mask":   0x0C, "regs": 1, "min": 0, "max":       3},  # PLL2_IDACSET_RECAL,
                       "PLL2_PD_AC": { "addr":   0x7F, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL2_PD_AC,
                   "PLL2_AC_CAL_EN": { "addr":   0x7F, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # PLL2_AC_CAL_EN,
                        "PLL2_INTG": { "addr":   0x80, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":      31},  # PLL2_INTG,
                "PLL2_AC_THRESHOLD": { "addr":   0x81, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":      31},  # PLL2_AC_THRESHOLD,
           "PLL2_AC_STRT_THRESHOLD": { "addr":   0x82, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":      31},  # PLL2_AC_STRT_THRESHOLD,
                "PLL2_AC_INIT_WAIT": { "addr":   0x83, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":       15},  # PLL2_AC_INIT_WAIT,
                 "PLL2_AC_CMP_WAIT": { "addr":   0x83, "loc":  4, "mask":   0xF0, "regs": 1, "min": 0, "max":       15},  # PLL2_AC_CMP_WAIT,
                "PLL2_AC_JUMP_STEP": { "addr":   0x84, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":      15},  # PLL2_AC_JUMP_STEP,
                "PLL2_LD_WNDW_SIZE": { "addr":   0x85, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":      255},  # PLL2_LD_WNDW_SIZE, for some reason, datasheet says 1-255 are reserved values
        "PLL2_LD_WNDW_SIZE_INITIAL": { "addr":   0x86, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # PLL2_LD_WNDW_SIZE_INITIAL, for some reason, datasheet says 1-255 are reserved values
             "PLL2_LOCKDET_CYC_CNT": { "addr":   0x87, "loc":  0, "mask":   0xFFFFFF, "regs": 3, "min": 0, "max":     0xFFFFFF},  # PLL2_LD_WNDW_SIZE_INITIAL,
     "PLL2_LOCKDET_CYC_CNT_INITIAL": { "addr":   0x8A, "loc":  0, "mask":   0xFFFFFF, "regs": 3, "min": 0, "max":     0xFFFFFF},  # PLL2_LOCKDET_CYC_CNT_INITIAL,
             "SPI_SDIO_EN_PULLDOWN": { "addr":   0x8D, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # SPI_SDIO_EN_PULLDOWN,
               "SPI_SDIO_EN_PULLUP": { "addr":   0x8D, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # SPI_SDIO_EN_PULLUP,
       "SPI_SDIO_OUTPUT_WEAK_DRIVE": { "addr":   0x8D, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # SPI_SDIO_OUTPUT_WEAK_DRIVE,
              "SPI_SDIO_OUTPUT_INV": { "addr":   0x8D, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # SPI_SDIO_OUTPUT_INV,
             "SPI_SDIO_OUTPUT_MUTE": { "addr":   0x8D, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # SPI_SDIO_OUTPUT_MUTE,
             "SPI_EN_THREE_WIRE_IF": { "addr":   0x8D, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # SPI_EN_THREE_WIRE_IF,
              "SPI_SCS_EN_PULLDOWN": { "addr":   0x8E, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # SPI_SCS_EN_PULLDOWN,
                "SPI_SCS_EN_PULLUP": { "addr":   0x8E, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # SPI_SCS_EN_PULLUP,
              "SPI_SCL_EN_PULLDOWN": { "addr":   0x8E, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # SPI_SCL_EN_PULLDOWN,
                "SPI_SCL_EN_PULLUP": { "addr":   0x8E, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # SPI_SCL_EN_PULLUP,
               "SPI_SDIO_INPUT_M12": { "addr":   0x8F, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       0},  # SPI_SDIO_INPUT_M12,
               "SPI_SDIO_INPUT_Y12": { "addr":   0x8F, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       0},  # SPI_SDIO_INPUT_Y12,
             "SPI_SDIO_OUTPUT_DATA": { "addr":   0x8F, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # SPI_SDIO_OUTPUT_DATA,
           "SPI_SDIO_EN_ML_INSTAGE": { "addr":   0x8F, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # SPI_SDIO_EN_ML_INSTAGE,
             "SPI_SDIO_ENB_INSTAGE": { "addr":   0x8F, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # SPI_SDIO_ENB_INSTAGE,
              "SPI_SDIO_OUTPUT_HIZ": { "addr":   0x8F, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # SPI_SDIO_OUTPUT_HIZ,
                "SPI_SCL_INPUT_M12": { "addr":   0x90, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       0},  # SPI_SCL_INPUT_M12,
                "SPI_SCL_INPUT_Y12": { "addr":   0x90, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       0},  # SPI_SCL_INPUT_Y12,
            "SPI_SCL_EN_ML_INSTAGE": { "addr":   0x90, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # SPI_SCL_EN_ML_INSTAGE,
              "SPI_SCL_ENB_INSTAGE": { "addr":   0x90, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # SPI_SCL_ENB_INSTAGE,
                "SPI_SCS_INPUT_M12": { "addr":   0x91, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       0},  # SPI_SCS_INPUT_M12,
                "SPI_SCS_INPUT_Y12": { "addr":   0x91, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       0},  # SPI_SCS_INPUT_Y12,
            "SPI_SCS_EN_ML_INSTAGE": { "addr":   0x91, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # SPI_SCS_EN_ML_INSTAGE,
              "SPI_SCS_ENB_INSTAGE": { "addr":   0x91, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # SPI_SCS_ENB_INSTAGE,
              "STATUS0_EN_PULLDOWN": { "addr":   0x92, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # STATUS0_EN_PULLDOWN,
                "STATUS0_EN_PULLUP": { "addr":   0x92, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # STATUS0_EN_PULLUP,
        "STATUS0_OUTPUT_WEAK_DRIVE": { "addr":   0x92, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # STATUS0_OUTPUT_WEAK_DRIVE,
               "STATUS0_OUTPUT_INV": { "addr":   0x92, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # STATUS0_OUTPUT_INV,
              "STATUS0_OUTPUT_MUTE": { "addr":   0x92, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # STATUS0_OUTPUT_MUTE,
                  "STATUS0_MUX_SEL": { "addr":   0x92, "loc":  5, "mask":   0xE0, "regs": 1, "min": 0, "max":       7},  # STATUS0_MUX_SEL,
              "STATUS1_EN_PULLDOWN": { "addr":   0x93, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # STATUS1_EN_PULLDOWN,
                "STATUS1_EN_PULLUP": { "addr":   0x93, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # STATUS1_EN_PULLUP,
        "STATUS1_OUTPUT_WEAK_DRIVE": { "addr":   0x93, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # STATUS1_OUTPUT_WEAK_DRIVE,
               "STATUS1_OUTPUT_INV": { "addr":   0x93, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # STATUS1_OUTPUT_INV,
              "STATUS1_OUTPUT_MUTE": { "addr":   0x93, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # STATUS1_OUTPUT_MUTE,
                  "STATUS1_MUX_SEL": { "addr":   0x93, "loc":  5, "mask":   0xE0, "regs": 1, "min": 0, "max":       7},  # STATUS1_MUX_SEL,
                  "STATUS1_INT_MUX": { "addr":   0x94, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":      18},  # STATUS1_INT_MUX,
                  "STATUS0_INT_MUX": { "addr":   0x95, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":      18},  # STATUS0_INT_MUX,
             "PLL2_REF_STATCLK_DIV": { "addr":   0x96, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # PLL2_REF_STATCLK_DIV,
                  "PLL2_REF_CLK_EN": { "addr":   0x96, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":      1},  # PLL2_REF_CLK_EN,
                "STATUS0_INPUT_M12": { "addr":   0x97, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       0},  # STATUS0_INPUT_M12,
                "STATUS0_INPUT_Y12": { "addr":   0x97, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       0},  # STATUS0_INPUT_Y12,
              "STATUS0_OUTPUT_DATA": { "addr":   0x97, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # STATUS0_OUTPUT_DATA,
            "STATUS0_EN_ML_INSTAGE": { "addr":   0x97, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # STATUS0_EN_ML_INSTAGE,
              "STATUS0_ENB_INSTAGE": { "addr":   0x97, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # STATUS0_ENB_INSTAGE,
               "STATUS0_OUTPUT_HIZ": { "addr":   0x97, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # STATUS0_OUTPUT_HIZ,
                "STATUS1_INPUT_M12": { "addr":   0x98, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       0},  # STATUS1_INPUT_M12,
                "STATUS1_INPUT_Y12": { "addr":   0x98, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       0},  # STATUS1_INPUT_Y12,
              "STATUS1_OUTPUT_DATA": { "addr":   0x98, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # STATUS1_OUTPUT_DATA,
            "STATUS1_EN_ML_INSTAGE": { "addr":   0x98, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # STATUS1_EN_ML_INSTAGE,
              "STATUS1_ENB_INSTAGE": { "addr":   0x98, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # STATUS1_ENB_INSTAGE,
               "STATUS1_OUTPUT_HIZ": { "addr":   0x98, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # STATUS1_OUTPUT_HIZ,
                 "SYNC_EN_PULLDOWN": { "addr":   0x99, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # SYNC_EN_PULLDOWN,
                   "SYNC_EN_PULLUP": { "addr":   0x99, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # SYNC_EN_PULLUP,
           "SYNC_OUTPUT_WEAK_DRIVE": { "addr":   0x99, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # SYNC_OUTPUT_WEAK_DRIVE,
                  "SYNC_OUTPUT_INV": { "addr":   0x99, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # SYNC_OUTPUT_INV,
                 "SYNC_OUTPUT_MUTE": { "addr":   0x99, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # SYNC_OUTPUT_MUTE,
                     "SYNC_MUX_SEL": { "addr":   0x99, "loc":  5, "mask":   0xE0, "regs": 1, "min": 0, "max":       7},  # SYNC_MUX_SEL,
            "CLKINSEL1_EN_PULLDOWN": { "addr":   0x9B, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # CLKINSEL1_EN_PULLDOWN,
              "CLKINSEL1_EN_PULLUP": { "addr":   0x9B, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CLKINSEL1_EN_PULLUP,
              "CLKINSEL1_INPUT_M12": { "addr":   0x9C, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       0},  # CLKINSEL1_INPUT_M12,
              "CLKINSEL1_INPUT_Y12": { "addr":   0x9C, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       0},  # CLKINSEL1_INPUT_Y12,
          "CLKINSEL1_EN_ML_INSTAGE": { "addr":   0x9C, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # CLKINSEL1_EN_ML_INSTAGE,
            "CLKINSEL1_ENB_INSTAGE": { "addr":   0x9C, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # CLKINSEL1_ENB_INSTAGE,
           "PLL1_TSTMODE_REF_FB_EN": { "addr":   0xAC, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # PLL1_TSTMODE_REF_FB_EN,
                       "PD_VCO_LDO": { "addr":   0xAD, "loc":  0, "mask":   0x03, "regs": 1, "min": 0, "max":       3},  # PD_VCO_LDO,
           "PLL2_TSTMODE_REF_FB_EN": { "addr":   0xAD, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # PLL2_TSTMODE_REF_FB_EN,
                   "RESET_PLL2_DLD": { "addr":   0xAD, "loc":  4, "mask":   0x30, "regs": 1, "min": 0, "max":       3},  # RESET_PLL2_DLD,
                     "PLL1_LCK_DET": { "addr":   0xBE, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       0},  # PLL1_LCK_DET,
                     "PLL2_LCK_DET": { "addr":   0xBE, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       0},  # PLL2_LCK_DET,
                     "HOLDOVER_LOS": { "addr":   0xBE, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       0},  # HOLDOVER_LOS,
                     "HOLDOVER_LOL": { "addr":   0xBE, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       0},  # HOLDOVER_LOL,
                     "HOLDOVER_DLD": { "addr":   0xBE, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       0},  # HOLDOVER_DLD,
                              "LOS": { "addr":   0xBE, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       0},  # LOS,
                      "PLL2_DLD_EN": { "addr":   0xF6, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # PLL2_DLD_EN,
                "PLL2_DUAL_LOOP_EN": { "addr":   0xF7, "loc":  5, "mask":   0x60, "regs": 1, "min": 0, "max":       3},  # PLL2_DUAL_LOOP_EN,
                         "CH1_DDLY": { "addr":   0xFD, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CH1_DDLY,
                         "CH2_DDLY": { "addr":   0xFF, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CH2_DDLY,
                        "CH34_DDLY": { "addr":  0x101, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CH34_DDLY,
                         "CH5_DDLY": { "addr":  0x103, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CH5_DDLY,
                         "CH6_DDLY": { "addr":  0x105, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CH6_DDLY,
                        "CH78_DDLY": { "addr":  0x107, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CH78_DDLY,
                         "CH9_DDLY": { "addr":  0x109, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CH9_DDLY,
                        "CH10_DDLY": { "addr":  0x10B, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CH10_DDLY,
                      "CH1_ADLY_EN": { "addr":  0x10D, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CH1_ADLY_EN,
                         "CH1_ADLY": { "addr":  0x10D, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      31},  # CH1_ADLY,
                      "CH2_ADLY_EN": { "addr":  0x10E, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CH2_ADLY_EN,
                         "CH2_ADLY": { "addr":  0x10E, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      31},  # CH2_ADLY,
                      "CH3_ADLY_EN": { "addr":  0x110, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CH3_ADLY_EN,
                         "CH3_ADLY": { "addr":  0x110, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      31},  # CH3_ADLY,
                      "CH4_ADLY_EN": { "addr":  0x111, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CH4_ADLY_EN,
                         "CH4_ADLY": { "addr":  0x111, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      31},  # CH4_ADLY,
                      "CH5_ADLY_EN": { "addr":  0x112, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CH5_ADLY_EN,
                         "CH5_ADLY": { "addr":  0x112, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      31},  # CH5_ADLY,
                      "CH6_ADLY_EN": { "addr":  0x115, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CH6_ADLY_EN,
                         "CH6_ADLY": { "addr":  0x115, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      31},  # CH6_ADLY,
                      "CH7_ADLY_EN": { "addr":  0x116, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CH7_ADLY_EN,
                         "CH7_ADLY": { "addr":  0x116, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      31},  # CH7_ADLY,
                      "CH8_ADLY_EN": { "addr":  0x117, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CH8_ADLY_EN,
                         "CH8_ADLY": { "addr":  0x117, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      31},  # CH8_ADLY,
                      "CH9_ADLY_EN": { "addr":  0x119, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # CH9_ADLY_EN,
                         "CH9_ADLY": { "addr":  0x119, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      31},  # CH9_ADLY,
                     "CH10_ADLY_EN": { "addr":  0x11A, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":      1},  # CH10_ADLY_EN,
                        "CH10_ADLY": { "addr":  0x11A, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":     31},  # CH10_ADLY,
                           "CLKMUX": { "addr":  0x124, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":     15},  # CLKMUX,
                      "DRIV_1_SLEW": { "addr":  0x127, "loc":  2, "mask":   0x0C, "regs": 1, "min": 0, "max":      3},  # DRIV_1_SLEW,
                        "HS_EN_CH1": { "addr":  0x127, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":     1},  # HS_EN_CH1,
                      "SYNC_EN_CH1": { "addr":  0x127, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":     1},  # SYNC_EN_CH1,
  "SYSREF_BYP_ANALOGDLY_GATING_CH1": { "addr":  0x127, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_ANALOGDLY_GATING_CH1,
  "SYSREF_BYP_DYNDIGDLY_GATING_CH1": { "addr":  0x127, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_DYNDIGDLY_GATING_CH1,
                      "DRIV_2_SLEW": { "addr":  0x128, "loc":  0, "mask":   0x03, "regs": 1, "min": 0, "max":      3},  # DRIV_2_SLEW,
                        "HS_EN_CH2": { "addr":  0x128, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":     1},  # HS_EN_CH2,
                      "SYNC_EN_CH2": { "addr":  0x128, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":     1},  # SYNC_EN_CH2,
  "SYSREF_BYP_ANALOGDLY_GATING_CH2": { "addr":  0x128, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_ANALOGDLY_GATING_CH2,
  "SYSREF_BYP_DYNDIGDLY_GATING_CH2": { "addr":  0x128, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_DYNDIGDLY_GATING_CH2,
                      "DRIV_3_SLEW": { "addr":  0x129, "loc":  0, "mask":   0x03, "regs": 1, "min": 0, "max":      3},  # DRIV_3_SLEW,
                      "DRIV_4_SLEW": { "addr":  0x129, "loc":  2, "mask":   0x0C, "regs": 1, "min": 0, "max":      3},  # DRIV_4_SLEW,
                      "HS_EN_CH3_4": { "addr":  0x129, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":     1},  # HS_EN_CH3_4,
                    "SYNC_EN_CH3_4": { "addr":  0x129, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":     1},  # SYNC_EN_CH3_4,
"SYSREF_BYP_ANALOGDLY_GATING_CH3_4": { "addr":  0x129, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_ANALOGDLY_GATING_CH3_4,
"SYSREF_BYP_DYNDIGDLY_GATING_CH4_4": { "addr":  0x129, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_DYNDIGDLY_GATING_CH3_4,
                      "DRIV_5_SLEW": { "addr":  0x12A, "loc":  0, "mask":   0x03, "regs": 1, "min": 0, "max":      3},  # DRIV_5_SLEW,
                        "HS_EN_CH5": { "addr":  0x12A, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":     1},  # HS_EN_CH5,
                      "SYNC_EN_CH5": { "addr":  0x12A, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":     1},  # SYNC_EN_CH5,
  "SYSREF_BYP_ANALOGDLY_GATING_CH5": { "addr":  0x12A, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_ANALOGDLY_GATING_CH5,
  "SYSREF_BYP_DYNDIGDLY_GATING_CH5": { "addr":  0x12A, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_DYNDIGDLY_GATING_CH5,
                      "DRIV_6_SLEW": { "addr":  0x12B, "loc":  2, "mask":   0x0C, "regs": 1, "min": 0, "max":      3},  # DRIV_6_SLEW,
                        "HS_EN_CH6": { "addr":  0x12B, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":     1},  # HS_EN_CH6,
                      "SYNC_EN_CH6": { "addr":  0x12B, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":     1},  # SYNC_EN_CH6,
  "SYSREF_BYP_ANALOGDLY_GATING_CH6": { "addr":  0x12B, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_ANALOGDLY_GATING_CH6,
  "SYSREF_BYP_DYNDIGDLY_GATING_CH6": { "addr":  0x12B, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_DYNDIGDLY_GATING_CH6,
                      "DRIV_7_SLEW": { "addr":  0x12C, "loc":  0, "mask":   0x03, "regs": 1, "min": 0, "max":      3},  # DRIV_7_SLEW,
                      "DRIV_8_SLEW": { "addr":  0x12C, "loc":  2, "mask":   0x0C, "regs": 1, "min": 0, "max":      3},  # DRIV_8_SLEW,
                      "HS_EN_CH7_8": { "addr":  0x12C, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":     1},  # HS_EN_CH7_8,
                    "SYNC_EN_CH7_8": { "addr":  0x12C, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":     1},  # SYNC_EN_CH7_8,
"SYSREF_BYP_ANALOGDLY_GATING_CH7_8": { "addr":  0x12C, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_ANALOGDLY_GATING_CH7_8,
"SYSREF_BYP_DYNDIGDLY_GATING_CH7_8": { "addr":  0x12C, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_DYNDIGDLY_GATING_CH7_8,
                      "DRIV_9_SLEW": { "addr":  0x12D, "loc":  2, "mask":   0x0C, "regs": 1, "min": 0, "max":      3},  # DRIV_9_SLEW,
                        "HS_EN_CH9": { "addr":  0x12D, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":     1},  # HS_EN_CH9,
                      "SYNC_EN_CH9": { "addr":  0x12D, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":     1},  # SYNC_EN_CH9,
  "SYSREF_BYP_ANALOGDLY_GATING_CH9": { "addr":  0x12D, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_ANALOGDLY_GATING_CH9,
  "SYSREF_BYP_DYNDIGDLY_GATING_CH9": { "addr":  0x12D, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_DYNDIGDLY_GATING_CH9,
                     "DRIV_10_SLEW": { "addr":  0x12E, "loc":  0, "mask":   0x03, "regs": 1, "min": 0, "max":      3},  # DRIV_10_SLEW,
                       "HS_EN_CH10": { "addr":  0x12E, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":     1},  # HS_EN_CH10,
                     "SYNC_EN_CH10": { "addr":  0x12E, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":     1},  # SYNC_EN_CH10,
 "SYSREF_BYP_ANALOGDLY_GATING_CH10": { "addr":  0x12E, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_ANALOGDLY_GATING_CH10,
 "SYSREF_BYP_DYNDIGDLY_GATING_CH10": { "addr":  0x12E, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":     1},  # SYSREF_BYP_DYNDIGDLY_GATING_CH10,
                     "DYN_DDLY_CH1": { "addr":  0x130, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH1,
                     "DYN_DDLY_CH2": { "addr":  0x131, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH2,
                     "DYN_DDLY_CH3": { "addr":  0x133, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH3,
                     "DYN_DDLY_CH4": { "addr":  0x134, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH4,
                     "DYN_DDLY_CH5": { "addr":  0x135, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH5,
                     "DYN_DDLY_CH6": { "addr":  0x138, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH6,
                     "DYN_DDLY_CH7": { "addr":  0x139, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH7,
                     "DYN_DDLY_CH8": { "addr":  0x13A, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH8,
                     "DYN_DDLY_CH9": { "addr":  0x13C, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH9,
                    "DYN_DDLY_CH10": { "addr":  0x13D, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":      7},  # DYN_DDLY_CH10,
              "OUTCH_SYSREF_PLSCNT": { "addr":  0x140, "loc":  0, "mask":   0x3F, "regs": 1, "min": 0, "max":     63},  # OUTCH_SYSREF_PLSCNT,
                     "SYNC_INT_MUX": { "addr":  0x141, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     18},  # SYNC_INT_MUX,
                   "SYNC_INPUT_M12": { "addr":  0x142, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       0},  # SYNC_INPUT_M12,
                   "SYNC_INPUT_Y12": { "addr":  0x142, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       0},  # SYNC_INPUT_Y12,
                 "SYNC_OUTPUT_DATA": { "addr":  0x142, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # SYNC_OUTPUT_DATA,
               "SYNC_EN_ML_INSTAGE": { "addr":  0x142, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # SYNC_EN_ML_INSTAGE,
                 "SYNC_ENB_INSTAGE": { "addr":  0x142, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # SYNC_ENB_INSTAGE,
                  "SYNC_OUTPUT_HIZ": { "addr":  0x142, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # SYNC_OUTPUT_HIZ,
                     "FBBUF_CH6_EN": { "addr":  0x143, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # FBBUF_CH6_EN,
                     "FBBUF_CH5_EN": { "addr":  0x143, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # FBBUF_CH5_EN,
                "PLL2_FBDIV_MUXSEL": { "addr":  0x146, "loc":  0, "mask":   0x03, "regs": 1, "min": 0, "max":       0},  # PLL2_FBDIV_MUXSEL,
                   "PLL2_PRESCALER": { "addr":  0x146, "loc":  2, "mask":   0x3C, "regs": 1, "min": 0, "max":      15},  # PLL2_PRESCALER,
             "PLL2_NBYPASS_DIV2_FB": { "addr":  0x146, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # PLL2_NBYPASS_DIV2_FB,
            "PLL1_STATUS0_HOLDOVER": { "addr":  0x149, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # PLL1_STATUS0_HOLDOVER,
            "PLL1_STATUS1_HOLDOVER": { "addr":  0x149, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # PLL1_STATUS1_HOLDOVER,
               "PLL1_SYNC_HOLDOVER": { "addr":  0x149, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # PLL1_SYNC_HOLDOVER,
       "PLL1_CLKINSEL1_ML_HOLDOVER": { "addr":  0x149, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # PLL1_CLKINSEL1_ML_HOLDOVER,
                         "SYNC_INV": { "addr":  0x14A, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # SYNC_INV,
                "SYNC_ANALOGDLY_EN": { "addr":  0x14A, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # SYNC_ANALOGDLY_EN,
                   "SYNC_ANALOGDLY": { "addr":  0x14A, "loc":  2, "mask":   0x7C, "regs": 1, "min": 0, "max":      63},  # SYNC_ANALOGDLY,
                  "DYN_DDLY_CH6_EN": { "addr":  0x14B, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH6_EN,
                  "DYN_DDLY_CH7_EN": { "addr":  0x14B, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH7_EN,
                  "DYN_DDLY_CH8_EN": { "addr":  0x14B, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH8_EN,
                  "DYN_DDLY_CH9_EN": { "addr":  0x14B, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH9_EN,
                 "DYN_DDLY_CH10_EN": { "addr":  0x14B, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH10_EN,
                  "DYN_DDLY_CH1_EN": { "addr":  0x14C, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH1_EN,
                  "DYN_DDLY_CH2_EN": { "addr":  0x14C, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH2_EN,
                  "DYN_DDLY_CH3_EN": { "addr":  0x14C, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH3_EN,
                  "DYN_DDLY_CH4_EN": { "addr":  0x14C, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH4_EN,
                  "DYN_DDLY_CH5_EN": { "addr":  0x14C, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # DYN_DDLY_CH5_EN,
                    "SYSREF_EN_CH1": { "addr":  0x14E, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # SYSREF_EN_CH1,
                    "SYSREF_EN_CH2": { "addr":  0x14E, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # SYSREF_EN_CH2,
                  "SYSREF_EN_CH3_4": { "addr":  0x14E, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # SYSREF_EN_CH3_4,
                    "SYSREF_EN_CH5": { "addr":  0x14E, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # SYSREF_EN_CH5,
                    "SYSREF_EN_CH6": { "addr":  0x14E, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # SYSREF_EN_CH6,
                  "SYSREF_EN_CH7_8": { "addr":  0x14E, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # SYSREF_EN_CH7_8,
                    "SYSREF_EN_CH9": { "addr":  0x14E, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # SYSREF_EN_CH9,
                   "SYSREF_EN_CH10": { "addr":  0x14E, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # SYSREF_EN_CH10,
              "PLL2_PROG_PFD_RESET": { "addr":  0x150, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":       7},  # PLL2_PROG_PFD_RESET,
              "PLL2_PFD_DIS_SAMPLE": { "addr":  0x150, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # PLL2_PFD_DIS_SAMPLE,
                       "PLL2_CPROP": { "addr":  0x151, "loc":  0, "mask":   0x03, "regs": 1, "min": 0, "max":       3},  # PLL2_CPROP,
            "PLL2_CP_EN_SAMPLE_BYP": { "addr":  0x151, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # PLL2_CP_EN_SAMPLE_BYP,
                       "PLL2_RFILT": { "addr":  0x151, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # PLL2_RFILT,
                     "PLL2_CSAMPLE": { "addr":  0x152, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":       7},  # PLL2_CSAMPLE,
                   "PLL2_EN_FILTER": { "addr":  0x152, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # PLL2_EN_FILTER,
                       "PLL2_CFILT": { "addr":  0x153, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":       31}  # PLL2_CFILT,
}

    ADDRESS_INFO = []
    GPIO_PINS = []

    def __init__(self, path=None, mode=None, name="LMK04610"):
        self.__dict__ = {}
        self._name = name

        if path and mode:
            self.ADDRESS_INFO.append({'path': path, 'mode': mode})
            _logger.debug("Instantiated LMK04610 device with path: " + str(path) + " and mode: " + str(mode))
        self.from_dict_plat()

        self.LMK04610CurParams = [0] * 0x153

        #self.LMK01020CurParams[9] = 0x22A00;
        #self.LMK01020CurParams[14] = 0x40000000;

    def from_dict_plat(self):
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value

    def register_device(self, channel, address):
        self.ADDRESS_INFO.append({'path': channel, 'mode': address})
        _logger.debug("Added LMK04610 device with path: " + str(channel) + " and mode: " + str(address))

    def device_summary(self):
        report = ""
        for addr in self.ADDRESS_INFO:
            report += ('{DeviceName: <10} :: Path:{Path: >3}, Mode:{Mode: >4}(0x{Mode:02X})\n'.format(DeviceName=self._name, Path=addr['path'], Mode=addr['mode']))
        return report

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]



    def read_param(self, devNum, paramName):

        if paramName in self.REGISTERS_INFO:
            paramInfo = self.REGISTERS_INFO[paramName]
        else:
            _logger.error("{paramName} is an unknown parameter or pin name.".format(paramName=paramName))
            return -1

        if not self.ADDRESS_INFO:
            _logger.error("No Devices registered. Aborting...")
            return -1

        spi_path = self.ADDRESS_INFO[devNum]["path"]
        spi_mode = self.ADDRESS_INFO[devNum]["mode"]

        totalResponse = 0
        try:
            with SPI(spi_path, spi_mode, 1000000) as spi:
                # Dont forget to convert to big endian!
                for r in range(paramInfo['regs']):
                    valueToSend = (paramInfo['addr']+r)
                    valueToSend += 1 << 15
                    writeBuf = (valueToSend).to_bytes(2, 'big')
                    _logger.debug("About to read raw data: " + str(writeBuf))
                    response = spi.transfer(writeBuf)
                    response = int.from_bytes(response, byteorder='big', signed=False)
                    totalResponse += (response << (8 * r))
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            _logger.error(e)
            return -1

        self.LMK04610CurParams[paramInfo['addr']] = totalResponse

        return totalResponse


    def write_param(self, devNum, paramName, value):
        if not (paramName in self.REGISTERS_INFO):
            _logger.error(str(paramName) + " is an invalid parameter name")
            return -1

        if paramName in self.REGISTERS_INFO:
            paramInfo = self.REGISTERS_INFO[paramName]
        elif paramName in self.GPIO_PINS[devNum]:
            self.gpio_set(devNum=devNum, name=paramName, value=value)
            return 0
        else:
            _logger.error("{paramName} is an unknown parameter or pin name.".format(paramName=paramName))
            return -1

        if not self.ADDRESS_INFO:
            _logger.error("No Devices registered. Aborting...")
            return -1

        spi_path = self.ADDRESS_INFO[devNum]["path"]
        spi_mode = self.ADDRESS_INFO[devNum]["mode"]

        if (1 == paramInfo["min"]) and (1 == paramInfo["max"]):
            _logger.error(str(paramName) + " is a read-only parameter")
            return -1

        if (value < paramInfo["min"]) or (value > paramInfo["max"]):
            _logger.error("{value} is an invalid value for {paramName}. " +
                          "Must be between {min} and {max}".format(value=value,
                                                                   paramName=paramName,
                                                                   min=paramInfo["min"],
                                                                   max=paramInfo["max"]))
            return -1

        # Positions to appropriate bits
        value <<= paramInfo["loc"]
        # Restrain to concerned bits
        value &= paramInfo["mask"]

        value = self.register_exceptions(paramInfo, value)

        self.LMK04610CurParams[paramInfo['addr']] = (~paramInfo['mask'] & self.LMK01020CurParams[paramInfo['addr']]) | value



        try:
            with SPI(spi_path, spi_mode, 1000000) as spi:
                # Dont forget to convert to big endian!
                for r in range(paramInfo['regs']):
                    valueToSend = (paramInfo['addr']+r) << 8
                    valueToSend += ((self.LMK04610CurParams[paramInfo['addr']] >> (r * 8)) & 0xFF)
                    writeBuf = (valueToSend).to_bytes(3, 'big')
                    _logger.debug("About to write raw data: " + str(writeBuf))
                    spi.transfer(writeBuf)
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            _logger.error(e)
            return -1

        return 0


    # Here are all the formatting exceptions for registers.
    def register_exceptions(self, paramInfo, value):
        return value


    def selftest(self, devNum):
        i2c_addr = self.ADDRESS_INFO[devNum]['path']
        i2c_ch = self.ADDRESS_INFO[devNum]['mode']
        val = self.read_param(devNum, "VNDRID")

        if (val != 0x100B):
            _logger.error(
                "Self-test for device " + str(self.DEVICE_NAME) + " on channel: " + str(i2c_ch) + " at address: " + str(
                    i2c_addr) + " failed")
            _logger.error("Expecting: " + str(0x100B) + ", Received: " + str(val))
            return -1
        return 0


    def readout_all_registers(self, devNum):
        _logger.info("==== Device report ====")
        _logger.warning("lmk01020 is write-only, skipping...")
        return 0

    def gpio_set(self, devNum, name, value):
        if not self.GPIO_PINS:
            _logger.warning("No gpio pins defined. Aborting...")
            return -1

        if name in self.GPIO_PINS[devNum]:
            pin = self.GPIO_PINS[devNum][name]
            g = GPIO(pin, "out")
            g.write(value)
            g.close()
        else:
            _logger.error("Could not find pin named " + str(name) + ". Aborting...")
            return -1

        return 0


class Command():
    def __init__(self, d, name="", acc=None):
        self.__dict__ = {}
        self._name = name
        self._acc = acc

    def __call__(self, *args):
        if len(args) == 2:
            self._acc.write_param(args[0], self._name, args[1])
        else:
            _logger.warning("Incorrect number of arguments. Ignoring")


    def from_dict(self, d, name=""):
        for key, value in d.items():
            self.__dict__[key] = value

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

if __name__ == "__main__":
    import argparse

    # parser = argparse.ArgumentParser(description='LMK04610 utility program.')
    # parser.add_argument('channel', help='I2C channel')
    # parser.add_argument('address', help='I2C address')
    # parser.add_argument('param', help='Parameter name')
    # parser.add_argument('-w', default=False, action='store_true', help='Write flag')
    #
    # args = parser.parse_args()
    # print((args))
