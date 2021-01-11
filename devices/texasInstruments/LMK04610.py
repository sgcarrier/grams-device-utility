import time
import logging
from periphery import SPI, GPIO

_logger = logging.getLogger(__name__)

class LMK04610:

    DEVICE_NAME = "LMK04610"

    #All register info concerning all LMK parameters
    REGISTERS_INFO = {
        #  if min=max=0, read-only, min=max=1 Self-clearing)
               "SWRST_CPY": { "addr":  0x00, "loc":  0, "mask":   0x01, "regs": 1, "min": 1, "max":   1},  # RESET,
           "LSB_FIRST_CPY": { "addr":  0x00, "loc":  1, "mask":   0x02, "regs": 1, "min": 1, "max":   1},  # LSB_FIRST_CPY,
         "ADDR_ASCEND_CPY": { "addr":  0x00, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":   1},  #ADDR_ASCEND_CPY,
          "SDO_ACTIVE_CPY": { "addr":  0x00, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":   1},  #SDO_ACTIVE_CPY,
              "SDO_ACTIVE": { "addr":  0x00, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":   1},  #SDO_ACTIVE,
             "ADDR_ASCEND": { "addr":  0x00, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":   1},  #ADDR_ASCEND,
               "LSB_FIRST": { "addr":  0x00, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":   1},  #LSB_FIRST,
                   "SWRST": { "addr":  0x00, "loc":  7, "mask":   0x80, "regs": 1, "min": 1, "max":   1},  #SWRST,

                "CHIPTYPE": { "addr":  0x03, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":   0},  # CHIPTYPE,
                   "DEVID": { "addr":  0x03, "loc":  6, "mask":   0xC0, "regs": 1, "min": 0, "max":   0},  # DEVID,

                  "CHIPID": { "addr":  0x04, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   0},  #CHIPID,

                 "CHIPVER": { "addr":  0x06, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":   0},  # CHIPVER,

                "VENDORID": { "addr":  0x0C, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":   0},  # VENDORID,

                  "PLL1EN": { "addr":  0x10, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":   1},  # PLL1EN,
                  "PLL2EN": { "addr":  0x10, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":   1},  # PLL2EN,
                "CH1TO5EN": { "addr":  0x10, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":   1},  # CH1TO5EN,
               "CH6TO10EN": { "addr":  0x10, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":   1},  # CH6TO10EN,
      "CLKINBLK_LOSLDO_EN": { "addr":  0x10, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":   1},  # CLKINBLK_LOSLDO_EN,
              "OUTCH_MUTE": { "addr":  0x10, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":   1},  # OUTCH_MUTE,

             "DEV_STARTUP": { "addr":  0x11, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":   1},  # DEV_STARTUP,

         "PORCLKAFTERLOCK": { "addr":  0x12, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":   1},  # PORCLKAFTERLOCK,
         "PLL2_DIG_CLK_EN": { "addr":  0x12, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":   1},  # PLL2_DIG_CLK_EN,
              "DIG_CLK_EN": { "addr":  0x12, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":   1},  # DIG_CLK_EN,

     "PLL2_REF_DIGCLK_DIV": { "addr":  0x13, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":  31},  # PLL2_REF_DIGCLK_DIV,

             "GLOBAL_SYNC": { "addr":  0x14, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":   1},  # GLOBAL_SYNC,
           "SYNC_PIN_FUNC": { "addr":  0x14, "loc":  1, "mask":   0x06, "regs": 1, "min": 0, "max":   3},  # SYNC_PIN_FUNC,
 "INV_SYNC_INPUT_SYNC_CLK": { "addr":  0x14, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":   1},  # INV_SYNC_INPUT_SYNC_CLK,
           "GLOBAL_SYSREF": { "addr":  0x14, "loc":  4, "mask":   0x10, "regs": 1, "min": 1, "max":   1},  # GLOBAL_SYSREF,
      "GLOBAL_CONT_SYSREF": { "addr":  0x14, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":   1},  # GLOBAL_CONT_SYSREF,
        "EN_SYNC_PIN_FUNC": { "addr":  0x14, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":   1},  # EN_SYNC_PIN_FUNC,

           "CLKINSEL1_INV": { "addr":  0x15, "loc":  0, "mask":    0x01, "regs": 1, "min": 0, "max":       1},  # CLKINSEL1_INV,
             "CLKIN_SWRST": { "addr":  0x15, "loc":  2, "mask":    0x04, "regs": 1, "min": 1, "max":       1},  # CLKIN_SWRST,
        "CLKIN_STAGGER_EN": { "addr":  0x15, "loc":  3, "mask":    0x08, "regs": 1, "min": 0, "max":       1},  # CLKIN_STAGGER_EN,

 "CLKINBLK_EN_BUF_BYP_PLL": { "addr":  0x16, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # CLKINBLK_EN_BUF_BYP_PLL,
 "CLKINBLK_EN_BUF_CLK_PLL": { "addr":  0x16, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # CLKINBLK_EN_BUF_CLK_PLL,
          "CLKINSEL1_MODE": { "addr":  0x16, "loc":  5, "mask":   0x60, "regs": 1, "min": 0, "max":       2},  # CLKINSEL1_MODE,
         "CLKINBLK_ALL_EN": { "addr":  0x16, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # CLKINBLK_ALL_EN,

             "CLKIN0_PRIO": { "addr":  0x19, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":       4},  # CLKIN0_PRIO,
          "CLKIN0_SE_MODE": { "addr":  0x19, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # CLKIN0_SE_MODE,
               "CLKIN0_EN": { "addr":  0x19, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # CLKIN0_EN,
   "CLKIN0_LOS_FRQ_DBL_EN": { "addr":  0x19, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # CLKIN0_LOS_FRQ_DBL_EN,
         "CLKIN0_PLL1_INV": { "addr":  0x19, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # CLKIN0_PLL1_INV,

             "CLKIN1_PRIO": { "addr":  0x1A, "loc":  0, "mask":   0x07, "regs": 1, "min": 0, "max":       4},  # CLKIN1_PRIO,
          "CLKIN1_SE_MODE": { "addr":  0x1A, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # CLKIN1_SE_MODE,
               "CLKIN1_EN": { "addr":  0x1A, "loc":  4, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # CLKIN1_EN,
   "CLKIN1_LOS_FRQ_DBL_EN": { "addr":  0x1A, "loc":  5, "mask":   0x20, "regs": 1, "min": 0, "max":       1},  # CLKIN1_LOS_FRQ_DBL_EN,
         "CLKIN1_PLL1_INV": { "addr":  0x1A, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # CLKIN1_PLL1_INV,

        "CLKIN0_PLL1_RDIV": { "addr":  0x1F, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # CLKIN0_PLL1_RDIV,

        "CLKIN1_PLL1_RDIV": { "addr":  0x21, "loc":  0, "mask": 0xFFFF, "regs": 2, "min": 0, "max":   65535},  # CLKIN1_PLL1_RDIV,

      "CLKIN0_LOS_REC_CNT": { "addr":  0x27, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CLKIN0_LOS_REC_CNT,

      "CLKIN0_LOS_LAT_SEL": { "addr":  0x28, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CLKIN0_LOS_LAT_SEL,

      "CLKIN1_LOS_REC_CNT": { "addr":  0x29, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CLKIN1_LOS_REC_CNT,

      "CLKIN1_LOS_LAT_SEL": { "addr":  0x2A, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # CLKIN1_LOS_LAT_SEL,

           "SW_CLKLOS_TMR": { "addr":  0x2B, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":      31},  # SW_CLKLOS_TMR,

           "SW_LOS_CH_SEL": { "addr":  0x2C, "loc":  0, "mask":   0x0F, "regs": 1, "min": 0, "max":      15},  # RISE_VALID_PRI,
             "SW_REFINSEL": { "addr":  0x2C, "loc":  4, "mask":   0xF0, "regs": 1, "min": 0, "max":      15},  # FALL_VALID_PRI,

        "SW_ALLREFSON_TMR": { "addr":  0x2D, "loc":  0, "mask":   0x1F, "regs": 1, "min": 0, "max":      31},  # SW_ALLREFSON_TMR,

        "OSCIN_BUF_LOS_EN": { "addr":  0x2E, "loc":  0, "mask":   0x10, "regs": 1, "min": 0, "max":       1},  # OSCIN_BUF_LOS_EN,
        "OSCIN_BUF_REF_EN": { "addr":  0x2E, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # OSCIN_BUF_REF_EN,
     "OSCIN_OSCINSTAGE_EN": { "addr":  0x2E, "loc":  2, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OSCIN_OSCINSTAGE_EN,
  "OSCIN_BUF_TO_OSCOUT_EN": { "addr":  0x2E, "loc":  3, "mask":   0xC0, "regs": 1, "min": 0, "max":       1},  # OSCIN_BUF_TO_OSCOUT_EN,
           "OSCIN_SE_MODE": { "addr":  0x2E, "loc":  4, "mask":   0x30, "regs": 1, "min": 0, "max":       1},  # OSCIN_SE_MODE,
            "OSCIN_PD_LDO": { "addr":  0x2E, "loc":  5, "mask":   0x0C, "regs": 1, "min": 0, "max":       1},  # OSCIN_PD_LDO,

          "OSCOUT_SEL_SRC": { "addr":  0x2F, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OSCOUT_SEL_SRC,
            "OSCOUT_SWRST": { "addr":  0x2F, "loc":  1, "mask":   0x02, "regs": 1, "min": 1, "max":       1},  # OSCOUT_SWRST,
        "OSCOUT_DIV_CLKEN": { "addr":  0x2F, "loc":  2, "mask":   0x04, "regs": 1, "min": 0, "max":       1},  # OSCOUT_DIV_CLKEN,
          "OSCOUT_SEL_VBG": { "addr":  0x2F, "loc":  3, "mask":   0x08, "regs": 1, "min": 0, "max":       1},  # OSCOUT_SEL_VBG,
       "OSCOUT_PINSEL_DIV": { "addr":  0x2F, "loc":  4, "mask":   0x30, "regs": 1, "min": 0, "max":       0},  # OSCOUT_PINSEL_DIV,
   "OSCOUT_DIV_REGCONTROL": { "addr":  0x2F, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OSCOUT_DIV_REGCONTROL,
"OSCOUT_LVCMOS_WEAK_DRIVE": { "addr":  0x2F, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OSCOUT_LVCMOS_WEAK_DRIVE,

              "OSCOUT_DIV": { "addr":  0x30, "loc":  0, "mask":   0xFF, "regs": 1, "min": 0, "max":     255},  # OSCOUT_DIV,

         "OSCOUT_DRV_MODE": { "addr":  0x31, "loc":  0, "mask":   0x3F, "regs": 1, "min": 0, "max":      63},  # OSCOUT_DRV_MODE,
         "OSCOUT_DRV_MUTE": { "addr":  0x31, "loc":  6, "mask":   0xC0, "regs": 1, "min": 0, "max":       3},  # OSCOUT_DRV_MUTE,

               "CH1_SWRST": { "addr":  0x32, "loc":  0, "mask":   0x01, "regs": 1, "min": 1, "max":       1},  # CH1_SWRST,
               "CH2_SWRST": { "addr":  0x32, "loc":  1, "mask":   0x02, "regs": 1, "min": 1, "max":       1},  # CH2_SWRST,
              "CH34_SWRST": { "addr":  0x32, "loc":  2, "mask":   0x04, "regs": 1, "min": 1, "max":       1},  # CH34_SWRST,
               "CH5_SWRST": { "addr":  0x32, "loc":  3, "mask":   0x08, "regs": 1, "min": 1, "max":       1},  # CH5_SWRST,
               "CH6_SWRST": { "addr":  0x32, "loc":  4, "mask":   0x10, "regs": 1, "min": 1, "max":       1},  # CH6_SWRST,
              "CH78_SWRST": { "addr":  0x32, "loc":  5, "mask":   0x20, "regs": 1, "min": 1, "max":       1},  # CH78_SWRST,
               "CH9_SWRST": { "addr":  0x32, "loc":  6, "mask":   0x40, "regs": 1, "min": 1, "max":       1},  # CH9_SWRST,
              "CH10_SWRST": { "addr":  0x32, "loc":  7, "mask":   0x80, "regs": 1, "min": 1, "max":       1},  # CH10_SWRST,

         "OUTCH1_LDO_MASK": { "addr":  0x33, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH1_LDO_MASK,
     "OUTCH1_LDO_BYP_MODE": { "addr":  0x33, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH1_LDO_BYP_MODE,

        "OUTCH1_DIV_CLKEN": { "addr":  0x34, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH1_DIV_CLKEN,
          "DIV_DCC_EN_CH1": { "addr":  0x34, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH1,
        "OUTCH1_DRIV_MODE": { "addr":  0x34, "loc":  2, "mask":   0xFC, "regs": 1, "min": 0, "max":      63},  # OUTCH1_DRIV_MODE,

        "OUTCH2_DRIV_MODE": { "addr":  0x35, "loc":  0, "mask":   0x2F, "regs": 1, "min": 0, "max":      63},  # OUTCH2_DRIV_MODE,
         "OUTCH2_LDO_MASK": { "addr":  0x35, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH2_LDO_MASK,
     "OUTCH2_LDO_BYP_MODE": { "addr":  0x35, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH2_LDO_BYP_MODE,

        "OUTCH2_DIV_CLKEN": { "addr":  0x36, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH2_DIV_CLKEN,
          "DIV_DCC_EN_CH2": { "addr":  0x36, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH2,

       "OUTCH34_DRIV_MODE": { "addr":  0x37, "loc":  0, "mask":   0x2F, "regs": 1, "min": 0, "max":      63},  # OUTCH34_DRIV_MODE,
        "OUTCH34_LDO_MASK": { "addr":  0x37, "loc":  6, "mask":   0x40, "regs": 1, "min": 0, "max":       1},  # OUTCH34_LDO_MASK,
    "OUTCH34_LDO_BYP_MODE": { "addr":  0x37, "loc":  7, "mask":   0x80, "regs": 1, "min": 0, "max":       1},  # OUTCH34_LDO_BYP_MODE,

       "OUTCH34_DIV_CLKEN": { "addr":  0x38, "loc":  0, "mask":   0x01, "regs": 1, "min": 0, "max":       1},  # OUTCH34_DIV_CLKEN,
        "DIV_DCC_EN_CH3_4": { "addr":  0x38, "loc":  1, "mask":   0x02, "regs": 1, "min": 0, "max":       1},  # DIV_DCC_EN_CH3_4,
        "OUTCH4_DRIV_MODE": { "addr":  0x38, "loc":  2, "mask":   0xFC, "regs": 1, "min": 0, "max":      63},  # OUTCH4_DRIV_MODE,

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







                  "TERM2GND_PRI": { "addr":  29, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       1},  # TERM2GND_PRI,
                  "DIFFTERM_SEC": { "addr":  29, "loc": 3, "mask":     0x08, "regs": 1, "min": 0, "max":       1},  # DIFFTERM_SEC,
                  "DIFFTERM_PRI": { "addr":  29, "loc": 2, "mask":     0x04, "regs": 1, "min": 0, "max":       1},  # DIFFTERM_PRI,
                   "AC_MODE_SEC": { "addr":  29, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # AC_MODE_SEC,
                   "AC_MODE_PRI": { "addr":  29, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # AC_MODE_PRI,
                    "CMOSCHPWDN": { "addr":  30, "loc": 6, "mask":     0x40, "regs": 1, "min": 0, "max":       1},  # CMOSCHPWDN,
                       "CH7PWDN": { "addr":  30, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       1},  # CH7PWDN,
                       "CH6PWDN": { "addr":  30, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       1},  # CH6PWDN,
                       "CH5PWDN": { "addr":  30, "loc": 3, "mask":     0x08, "regs": 1, "min": 0, "max":       1},  # CH5PWDN,
                      "CH23PWDN": { "addr":  30, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # CH23PWDN,
                      "CH01PWDN": { "addr":  30, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # CH01PWDN,
}

    ADDRESS_INFO = []
    GPIO_PINS = []

    def __init__(self, path=None, mode=None, name="LMK04610"):
        self._name = name
        self.__dict__ = {}

        if path and mode:
            self.ADDRESS_INFO.append({'path': path, 'mode': mode})
        self.from_dict_plat()

        self.LMK04610CurParams = [0] * 14

        #self.LMK01020CurParams[9] = 0x22A00;
        #self.LMK01020CurParams[14] = 0x40000000;

    def from_dict_plat(self):
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value

    def register_device(self, channel, address):
        self.ADDRESS_INFO.append({'path': channel, 'mode': address})

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


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

        with SPI(spi_path, spi_mode, 1000000) as spi:
            writeBuf = self.LMK04610CurParams[paramInfo['addr']].to_bytes(4, 'big')
            spi.transfer(writeBuf)

        return 0


    # Here are all the formatting exceptions for registers.
    def register_exceptions(self, paramInfo, value):
        return value


    def selftest(self, devNum):
        # lmk01020 is write-only, skip self-test
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
        try:
            if len(args) == 2:
                self._acc.write_param(args[0], self._name, args[1])
            else:
                _logger.warning("Incorrect number of arguments. Ignoring")
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            raise e


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
