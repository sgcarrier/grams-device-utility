import time
import smbus
import logging
from periphery import GPIO

_logger = logging.getLogger(__name__)

class LMK03318:
    """
        Class for the LMK03318, a Ultra-Low-Noise Jitter Clock Generator
        The LMK03318 is a read-write device that communicates via I2C

        User Notes:
        - BEFORE talking to it on i2c line, toggle the PDN pin. (see setup() function). If you don't the I2C might be
          unusable
        - Toggle the SYNC pin after programming. leave a sleep() in between
        - Make sure the Fvco is within its range (4.8-5.4 GHz), if it's not locked, it won't output anything
        - Toggling the register PLL_PDN 1->0 is important to lock the VCO do it right before the sync
    """

    DEVICE_NAME = "LMK03318"

    ''' All register info concerning all LMK parameters '''
    REGISTERS_INFO = {
        #  if min=max=0, read-only, min=max=1 Self-clearing)
                        "VNDRID": { "addr":   0, "loc": 0, "mask":   0xFFFF, "regs": 2, "min": 0, "max":       0},  # VNDRID = 0x0,
                        "PRODID": { "addr":   2, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":       0},  # PRODID,
                         "REVID": { "addr":   3, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":       0},  # REVID,
                         "PRTID": { "addr":   4, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":       0},  # PRTID,
               "HW_SW_CTRL_MODE": { "addr":   8, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       0},  # HW_SW_CTRL_MODE,
                "GPIO32_SW_MODE": { "addr":   8, "loc": 4, "mask":     0x70, "regs": 1, "min": 0, "max":       0},  # GPIO32_SW_MODE,
                  "GPIO_HW_MODE": { "addr":   9, "loc": 2, "mask":     0xFC, "regs": 1, "min": 0, "max":       0},  # GPIO_HW_MODE,
              "SLAVEADR_GPIO_SW": { "addr":  10, "loc": 1, "mask":     0xFE, "regs": 1, "min": 0, "max":       0},  # SLAVEADR_GPIO_SW,
                         "EEREV": { "addr":  11, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":       0},  # EEREV,
                     "RESETN_SW": { "addr":  12, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       1},  # RESETN_SW,
                      "SYNCN_SW": { "addr":  12, "loc": 6, "mask":     0x40, "regs": 1, "min": 0, "max":       1},  # SYNCN_SW,
                     "SYNC_AUTO": { "addr":  12, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       1},  # SYNC_AUTO,
                     "SYNC_MUTE": { "addr":  12, "loc": 3, "mask":      0x8, "regs": 1, "min": 0, "max":       1},  # SYNC_MUTE,
                  "AONAFTERLOCK": { "addr":  12, "loc": 2, "mask":      0x4, "regs": 1, "min": 0, "max":       1},  # AONAFTERLOCK,
                      "AUTOSTRT": { "addr":  12, "loc": 0, "mask":      0x1, "regs": 1, "min": 0, "max":       1},  # AUTOSTRT,
                           "LOL": { "addr":  13, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       0},  # LOL,
                           "LOS": { "addr":  13, "loc": 6, "mask":     0x40, "regs": 1, "min": 0, "max":       0},  # LOS,
                           "CAL": { "addr":  13, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       0},  # CAL,
                      "SECTOPRI": { "addr":  13, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       0},  # SECTOPRI,
                      "LOL_MASK": { "addr":  14, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       1},  # LOL_MASK,
                      "LOS_MASK": { "addr":  14, "loc": 6, "mask":     0x40, "regs": 1, "min": 0, "max":       1},  # LOS_MASK,
                      "CAL_MASK": { "addr":  14, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       1},  # CAL_MASK,
                 "SECTOPRI_MASK": { "addr":  14, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # SECTOPRI_MASK,
                       "LOL_POL": { "addr":  15, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       1},  # LOL_POL,
                       "LOS_POL": { "addr":  15, "loc": 6, "mask":     0x40, "regs": 1, "min": 0, "max":       1},  # LOS_POL,
                       "CAL_POL": { "addr":  15, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       1},  # CAL_POL,
                  "SECTOPRI_POL": { "addr":  15, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # SECTOPRI_POL,
                      "LOL_INTR": { "addr":  16, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       0},  # LOL_INTR,
                      "LOS_INTR": { "addr":  16, "loc": 6, "mask":     0x40, "regs": 1, "min": 0, "max":       0},  # LOS_INTR,
                      "CAL_INTR": { "addr":  16, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       0},  # CAL_INTR,
                 "SECTOPRI_INTR": { "addr":  16, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       0},  # SECTOPRI_INTR,
                    "INT_AND_OR": { "addr":  17, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # INT_AND_OR,
                        "INT_EN": { "addr":  17, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # INT_EN,
                "RISE_VALID_SEC": { "addr":  18, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       0},  # RISE_VALID_SEC,
                "FALL_VALID_SEC": { "addr":  18, "loc": 6, "mask":     0x40, "regs": 1, "min": 0, "max":       0},  # FALL_VALID_SEC,
                "RISE_VALID_PRI": { "addr":  18, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       0},  # RISE_VALID_PRI,
                "FALL_VALID_PRI": { "addr":  18, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       0},  # FALL_VALID_PRI,
        "STAT1_SHOOT_THRU_LIMIT": { "addr":  19, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       1},  # STAT1_SHOOT_THRU_LIMIT,
        "STAT0_SHOOT_THRU_LIMIT": { "addr":  19, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       1},  # STAT0_SHOOT_THRU_LIMIT,
                   "STAT1_OPEND": { "addr":  19, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # STAT1_OPEND,
                   "STAT0_OPEND": { "addr":  19, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # STAT0_OPEND,
                  "CH3_MUTE_LVL": { "addr":  20, "loc": 6, "mask":     0xC0, "regs": 1, "min": 0, "max":       3},  # CH3_MUTE_LVL,
                  "CH2_MUTE_LVL": { "addr":  20, "loc": 4, "mask":     0x30, "regs": 1, "min": 0, "max":       3},  # CH2_MUTE_LVL,
                  "CH1_MUTE_LVL": { "addr":  20, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # CH1_MUTE_LVL,
                  "CH0_MUTE_LVL": { "addr":  20, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # CH0_MUTE_LVL,
                  "CH7_MUTE_LVL": { "addr":  21, "loc": 6, "mask":     0xC0, "regs": 1, "min": 0, "max":       3},  # CH7_MUTE_LVL,
                  "CH6_MUTE_LVL": { "addr":  21, "loc": 4, "mask":     0x30, "regs": 1, "min": 0, "max":       3},  # CH6_MUTE_LVL,
                  "CH5_MUTE_LVL": { "addr":  21, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # CH5_MUTE_LVL,
                  "CH4_MUTE_LVL": { "addr":  21, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # CH4_MUTE_LVL,
                     "CH_7_MUTE": { "addr":  22, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       1},  # CH_7_MUTE,
                     "CH_6_MUTE": { "addr":  22, "loc": 6, "mask":     0x40, "regs": 1, "min": 0, "max":       1},  # CH_6_MUTE,
                     "CH_5_MUTE": { "addr":  22, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       1},  # CH_5_MUTE,
                     "CH_4_MUTE": { "addr":  22, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       1},  # CH_4_MUTE,
                     "CH_3_MUTE": { "addr":  22, "loc": 3, "mask":     0x08, "regs": 1, "min": 0, "max":       1},  # CH_3_MUTE,
                     "CH_2_MUTE": { "addr":  22, "loc": 2, "mask":     0x04, "regs": 1, "min": 0, "max":       1},  # CH_2_MUTE,
                     "CH_1_MUTE": { "addr":  22, "loc": 1, "mask":     0x20, "regs": 1, "min": 0, "max":       1},  # CH_1_MUTE,
                     "CH_0_MUTE": { "addr":  22, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # CH_0_MUTE,
                  "STATUS1_MUTE": { "addr":  23, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # STATUS1_MUTE,
                  "STATUS0_MUTE": { "addr":  23, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # STATUS0_MUTE,
                 "DIV_7_DYN_DLY": { "addr":  24, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       1},  # DIV_7_DYN_DLY,
                 "DIV_6_DYN_DLY": { "addr":  24, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       1},  # DIV_6_DYN_DLY,
                 "DIV_5_DYN_DLY": { "addr":  24, "loc": 3, "mask":     0x08, "regs": 1, "min": 0, "max":       1},  # DIV_5_DYN_DLY,
                 "DIV_4_DYN_DLY": { "addr":  24, "loc": 2, "mask":     0x04, "regs": 1, "min": 0, "max":       1},  # DIV_4_DYN_DLY,
                "DIV_23_DYN_DLY": { "addr":  24, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # DIV_23_DYN_DLY,
                "DIV_01_DYN_DLY": { "addr":  24, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # DIV_01_DYN_DLY,
               "DETECT_MODE_SEC": { "addr":  25, "loc": 6, "mask":     0xC0, "regs": 1, "min": 0, "max":       3},  # DETECT_MODE_SEC,
               "DETECT_MODE_PRI": { "addr":  25, "loc": 4, "mask":     0x30, "regs": 1, "min": 0, "max":       3},  # DETECT_MODE_PRI,
                   "LVL_SEL_SEC": { "addr":  25, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # LVL_SEL_SEC,
                   "LVL_SEL_PRI": { "addr":  25, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # LVL_SEL_PRI,
                     "STAT0_SEL": { "addr":  27, "loc": 4, "mask":     0xF0, "regs": 1, "min": 0, "max":      15},  # STAT0_SEL,
                     "STAT0_POL": { "addr":  27, "loc": 3, "mask":     0x08, "regs": 1, "min": 0, "max":       1},  # STAT0_POL,
                     "STAT1_SEL": { "addr":  28, "loc": 4, "mask":     0xF0, "regs": 1, "min": 0, "max":      15},  # STAT1_SEL,
                     "STAT1_POL": { "addr":  28, "loc": 3, "mask":     0x08, "regs": 1, "min": 0, "max":       1},  # STAT1_POL,
                    "DETECT_BYP": { "addr":  29, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       1},  # DETECT_BYP,
                  "TERM2GND_SEC": { "addr":  29, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       1},  # TERM2GND_SEC,
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
                     "OUT_0_SEL": { "addr":  31, "loc": 5, "mask":     0x60, "regs": 1, "min": 0, "max":       3},  # OUT_0_SEL,
                   "OUT_0_MODE1": { "addr":  31, "loc": 3, "mask":     0x18, "regs": 1, "min": 0, "max":       3},  # OUT_0_MODE1,
                   "OUT_0_MODE2": { "addr":  31, "loc": 1, "mask":     0x06, "regs": 1, "min": 0, "max":       3},  # OUT_0_MODE2,
                     "OUT_1_SEL": { "addr":  32, "loc": 5, "mask":     0x60, "regs": 1, "min": 0, "max":       3},  # OUT_1_SEL,
                   "OUT_1_MODE1": { "addr":  32, "loc": 3, "mask":     0x18, "regs": 1, "min": 0, "max":       3},  # OUT_1_MODE1,
                   "OUT_1_MODE2": { "addr":  32, "loc": 1, "mask":     0x06, "regs": 1, "min": 0, "max":       3},  # OUT_1_MODE2,
                   "OUT_0_1_DIV": { "addr":  33, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":     255},  # OUT_0_1_DIV,
                     "OUT_2_SEL": { "addr":  34, "loc": 5, "mask":     0x60, "regs": 1, "min": 0, "max":       3},  # OUT_2_SEL,
                   "OUT_2_MODE1": { "addr":  34, "loc": 3, "mask":     0x18, "regs": 1, "min": 0, "max":       3},  # OUT_2_MODE1,
                   "OUT_2_MODE2": { "addr":  34, "loc": 1, "mask":     0x06, "regs": 1, "min": 0, "max":       3},  # OUT_2_MODE2,
                     "OUT_3_SEL": { "addr":  35, "loc": 5, "mask":     0x60, "regs": 1, "min": 0, "max":       3},  # OUT_3_SEL,
                   "OUT_3_MODE1": { "addr":  35, "loc": 3, "mask":     0x18, "regs": 1, "min": 0, "max":       3},  # OUT_3_MODE1,
                   "OUT_3_MODE2": { "addr":  35, "loc": 1, "mask":     0x06, "regs": 1, "min": 0, "max":       3},  # OUT_3_MODE2,
                   "OUT_2_3_DIV": { "addr":  36, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":     255},  # OUT_2_3_DIV,
                      "CH_4_MUX": { "addr":  37, "loc": 6, "mask":     0xC0, "regs": 1, "min": 0, "max":       3},  # CH_4_MUX,
                     "OUT_4_SEL": { "addr":  37, "loc": 4, "mask":     0x30, "regs": 1, "min": 0, "max":       3},  # OUT_4_SEL,
                   "OUT_4_MODE1": { "addr":  37, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # OUT_4_MODE1,
                   "OUT_4_MODE2": { "addr":  37, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # OUT_4_MODE2,
                     "OUT_4_DIV": { "addr":  38, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":     255},  # OUT_4_DIV,
                      "CH_5_MUX": { "addr":  39, "loc": 6, "mask":     0xC0, "regs": 1, "min": 0, "max":       3},  # CH_5_MUX,
                     "OUT_5_SEL": { "addr":  39, "loc": 4, "mask":     0x30, "regs": 1, "min": 0, "max":       3},  # OUT_5_SEL,
                   "OUT_5_MODE1": { "addr":  39, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # OUT_5_MODE1,
                   "OUT_5_MODE2": { "addr":  39, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # OUT_5_MODE2,
                     "OUT_5_DIV": { "addr":  40, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":     255},  # OUT_5_DIV,
                      "CH_6_MUX": { "addr":  41, "loc": 6, "mask":     0xC0, "regs": 1, "min": 0, "max":       3},  # CH_6_MUX,
                     "OUT_6_SEL": { "addr":  41, "loc": 4, "mask":     0x30, "regs": 1, "min": 0, "max":       3},  # OUT_6_SEL,
                   "OUT_6_MODE1": { "addr":  41, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # OUT_6_MODE1,
                   "OUT_6_MODE2": { "addr":  41, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # OUT_6_MODE2,
                     "OUT_6_DIV": { "addr":  42, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":     255},  # OUT_6_DIV,
                      "CH_7_MUX": { "addr":  43, "loc": 6, "mask":     0xC0, "regs": 1, "min": 0, "max":       3},  # CH_7_MUX,
                     "OUT_7_SEL": { "addr":  43, "loc": 4, "mask":     0x30, "regs": 1, "min": 0, "max":       3},  # OUT_7_SEL,
                   "OUT_7_MODE1": { "addr":  43, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # OUT_7_MODE1,
                   "OUT_7_MODE2": { "addr":  43, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # OUT_7_MODE2,
                     "OUT_7_DIV": { "addr":  44, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":     255},  # OUT_7_DIV,
                 "PLLCMOSPREDIV": { "addr":  45, "loc": 4, "mask":     0x30, "regs": 1, "min": 0, "max":       2},  # PLLCMOSPREDIV,
                    "STATUS1MUX": { "addr":  45, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # STATUS1MUX,
                    "STATUS0MUX": { "addr":  45, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # STATUS0MUX,
                      "CMOSDIV0": { "addr":  46, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":     255},  # CMOSDIV0,
                   "STATUS1SLEW": { "addr":  49, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       2},  # STATUS1SLEW,
                   "STATUS0SLEW": { "addr":  49, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       2},  # STATUS0SLEW,
                     "SECBUFSEL": { "addr":  50, "loc": 6, "mask":     0xC0, "regs": 1, "min": 0, "max":       3},  # SECBUFSEL,
                     "PRIBUFSEL": { "addr":  50, "loc": 4, "mask":     0x30, "regs": 1, "min": 0, "max":       3},  # PRIBUFSEL,
                     "INSEL_PLL": { "addr":  50, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # INSEL_PLL,
                 "CLKMUX_BYPASS": { "addr":  51, "loc": 7, "mask":     0x80, "regs": 1, "min": 0, "max":       1},  # CLKMUX_BYPASS,
                   "SECONSWITCH": { "addr":  51, "loc": 2, "mask":     0x04, "regs": 1, "min": 0, "max":       1},  # SECONSWITCH,
                    "SECBUFGAIN": { "addr":  51, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # SECBUFGAIN,
                    "PRIBUFGAIN": { "addr":  51, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # PRIBUFGAIN,
                       "PLLRDIV": { "addr":  52, "loc": 0, "mask":     0x07, "regs": 1, "min": 0, "max":       7},  # PLLRDIV,
                       "PLLMDIV": { "addr":  53, "loc": 0, "mask":     0x1F, "regs": 1, "min": 0, "max":      31},  # PLLMDIV,
                         "PLL_P": { "addr":  56, "loc": 2, "mask":     0x1C, "regs": 1, "min": 0, "max":       7},  # PLL_P,
                   "PLL_SYNC_EN": { "addr":  56, "loc": 1, "mask":     0x02, "regs": 1, "min": 0, "max":       1},  # PLL_SYNC_EN,
                       "PLL_PDN": { "addr":  56, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # PLL_PDN,
                         "PRI_D": { "addr":  57, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       1},  # PRI_D,
                        "PLL_CP": { "addr":  57, "loc": 0, "mask":     0x0F, "regs": 1, "min": 1, "max":       8},  # PLL_CP,
                      "PLL_NDIV": { "addr":  58, "loc": 0, "mask":   0x0FFF, "regs": 2, "min": 0, "max":    4095},  # PLL_NDIV,
                       "PLL_NUM": { "addr":  60, "loc": 0, "mask": 0x3FFFFF, "regs": 3, "min": 0, "max": 4194303},  # PLL_NUM,
                       "PLL_DEN": { "addr":  63, "loc": 0, "mask": 0x3FFFFF, "regs": 3, "min": 0, "max": 4194303},  # PLL_DEN,
                  "PLL_DTHRMODE": { "addr":  66, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # PLL_DTHRMODE,
                     "PLL_ORDER": { "addr":  66, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # PLL_ORDER,
                     "PLL_LF_R2": { "addr":  67, "loc": 0, "mask":     0x3F, "regs": 1, "min": 0, "max":      48},  # PLL_LF_R2,
                     "PLL_LF_C1": { "addr":  68, "loc": 0, "mask":     0x07, "regs": 1, "min": 0, "max":       7},  # PLL_LF_C1,
                     "PLL_LF_R3": { "addr":  69, "loc": 1, "mask":     0x7E, "regs": 1, "min": 0, "max":      63},  # PLL_LF_R3,
               "PLL_LF_INT_FRAC": { "addr":  69, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # PLL_LF_INT_FRAC,
                     "PLL_LF_C3": { "addr":  70, "loc": 0, "mask":     0x07, "regs": 1, "min": 0, "max":       7},  # PLL_LF_C3,
                         "SEC_D": { "addr":  72, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       1},  # SEC_D,
               "MARGIN_DIG_STEP": { "addr":  86, "loc": 4, "mask":     0x70, "regs": 1, "min": 0, "max":       7},  # MARGIN_DIG_STEP,
                 "MARGIN_OPTION": { "addr":  86, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # MARGIN_OPTION,
                "XOOFFSET_STEP1": { "addr":  88, "loc": 0, "mask":   0x03FF, "regs": 2, "min": 0, "max":    1023},  # XOOFFSET_STEP1,
                "XOOFFSET_STEP2": { "addr":  90, "loc": 0, "mask":   0x03FF, "regs": 2, "min": 0, "max":    1023},  # XOOFFSET_STEP2,
                "XOOFFSET_STEP3": { "addr":  92, "loc": 0, "mask":   0x03FF, "regs": 2, "min": 0, "max":    1023},  # XOOFFSET_STEP3,
                "XOOFFSET_STEP4": { "addr":  94, "loc": 0, "mask":   0x03FF, "regs": 2, "min": 0, "max":    1023},  # XOOFFSET_STEP4,
                "XOOFFSET_STEP5": { "addr":  96, "loc": 0, "mask":   0x03FF, "regs": 2, "min": 0, "max":    1023},  # XOOFFSET_STEP5,
                "XOOFFSET_STEP6": { "addr":  98, "loc": 0, "mask":   0x03FF, "regs": 2, "min": 0, "max":    1023},  # XOOFFSET_STEP6,
                "XOOFFSET_STEP7": { "addr": 100, "loc": 0, "mask":   0x03FF, "regs": 2, "min": 0, "max":    1023},  # XOOFFSET_STEP7,
                "XOOFFSET_STEP8": { "addr": 102, "loc": 0, "mask":   0x03FF, "regs": 2, "min": 0, "max":    1023},  # XOOFFSET_STEP8,
                   "XOOFFSET_SW": { "addr": 104, "loc": 0, "mask":   0x03FF, "regs": 2, "min": 0, "max":    1023},  # XOOFFSET_SW,
                   "PLL_STRETCH": { "addr": 117, "loc": 0, "mask":     0x80, "regs": 1, "min": 0, "max":       1},  # PLL_STRETCH,
               "PLL_DISABLE_4TH": { "addr": 118, "loc": 0, "mask":     0x07, "regs": 1, "min": 0, "max":       7},  # PLL_DISABLE_4TH,
                  "PLL_CLSDWAIT": { "addr": 119, "loc": 2, "mask":     0x0C, "regs": 1, "min": 0, "max":       3},  # PLL_CLSDWAIT,
                   "PLL_VCOWAIT": { "addr": 119, "loc": 0, "mask":     0x03, "regs": 1, "min": 0, "max":       3},  # PLL_VCOWAIT,
                    "PLL_LOOPBW": { "addr": 120, "loc": 0, "mask":     0x01, "regs": 1, "min": 0, "max":       1},  # PLL_LOOPBW,
                        "NVMCNT": { "addr": 136, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":       0},  # NVMCNT,
                     "REGCOMMIT": { "addr": 137, "loc": 6, "mask":     0x40, "regs": 1, "min": 1, "max":       1},  # REGCOMMIT,
                     "NVMCRCERR": { "addr": 137, "loc": 5, "mask":     0x20, "regs": 1, "min": 0, "max":       0},  # NVMCRCERR,
                    "NVMAUTOCRC": { "addr": 137, "loc": 4, "mask":     0x10, "regs": 1, "min": 0, "max":       1},  # NVMAUTOCRC,
                     "NVMCOMMIT": { "addr": 137, "loc": 3, "mask":     0x08, "regs": 1, "min": 1, "max":       1},  # NVMCOMMIT,
                       "NVMBUSY": { "addr": 137, "loc": 2, "mask":     0x04, "regs": 1, "min": 0, "max":       0},  # NVMBUSY,
                       "NVMPROG": { "addr": 137, "loc": 0, "mask":     0x01, "regs": 1, "min": 1, "max":       1},  # NVMPROG,
                       "NVMLCRC": { "addr": 138, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":       0},  # NVMLCRC,
                        "MEMADR": { "addr": 139, "loc": 0, "mask":   0x0FFF, "regs": 2, "min": 0, "max":    4095},  # MEMADR,
                        "NVMDAT": { "addr": 141, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":       0},  # NVMDAT,
                        "RAMDAT": { "addr": 142, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":     255},  # RAMDAT,
                        "ROMDAT": { "addr": 143, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":       0},  # ROMDAT,
                       "NVMUNLK": { "addr": 144, "loc": 0, "mask":     0xFF, "regs": 1, "min": 0, "max":     255},  # NVMUNLK,
                  "REGCOMMIT_PG": { "addr": 145, "loc": 0, "mask":     0x0F, "regs": 1, "min": 0, "max":       5},  # REGCOMMIT_PG,
                   "XO_CAP_CTRL": { "addr": 199, "loc": 0, "mask":    0x3FF, "regs": 1, "min": 0, "max":       0}   # XO_CAP_CTRL,
}

    ADDRESS_INFO = []
    GPIO_PINS = []

    def __init__(self, i2c_ch=None, i2c_addr=None, name="LMK03318", cmdClass=None):
        self.__dict__ = {}
        self._name = name
        if i2c_ch and i2c_addr:
            self.ADDRESS_INFO.append({'ch': i2c_ch, 'addr': i2c_addr})
            _logger.debug("Instantiated LMK03318 device with ch: " + str(i2c_ch) + " and addr: " + str(i2c_addr))

        if cmdClass == None:
            cmdClass = Command

        ''' Populate add all the registers as attributes '''
        for key, value in self.REGISTERS_INFO.items():
            value = cmdClass(value, str(key), self)
            self.__dict__[key] = value

        '''Extra commands'''
        self.__dict__["GPIO"] = cmdClass(self.GPIO_PINS, "GPIO", self)

    def setup(self):
        """
        The functions that must be run before anything is done on the line.
        In this case: Must toggle PDN before sending data or else the I2C line will lock up...
        :return: None
        """
        for i in range(len(self.GPIO_PINS)):
            self.GPIO(i, "CFGSEL0", False)
            self.GPIO(i, "CFGSEL1", False)
            time.sleep(0.5)
            self.GPIO(i, "CFGSEL0", True)
            self.GPIO(i, "CFGSEL1", True)
            time.sleep(0.5)
            self.GPIO(i, "PDN", False)
            time.sleep(0.5)
            self.GPIO(i, "PDN", True)

    def register_device(self, channel, address):
        """
        Register a new LMK03318 device.
        :param channel: I2C Channel number
        :param address: I2C address
        :return: None
        """
        self.ADDRESS_INFO.append({'ch': channel, 'addr': address})
        _logger.debug("Added LMK03318 device with ch: " + str(channel) + " and addr: " + str(address))

    def device_summary(self):
        """
        Returns a summary of all the LMK03318 devices.
        :return: String report
        """
        report = ""
        for addr in self.ADDRESS_INFO:
            report += ('{DeviceName: <10} :: Channel:{Channel: >3}, Address:{Address: >4}(0x{Address:02X})\n'.format(DeviceName=self._name, Channel=addr['ch'], Address=addr['addr']))
        return report

    def read_param(self, devNum, paramName):
        if not (paramName in self.REGISTERS_INFO):
            _logger.error(str(paramName) + " is an invalid parameter name")
            return -1

        if paramName in self.REGISTERS_INFO:
            paramInfo = self.REGISTERS_INFO[paramName]
        else:
            _logger.error("{paramName} is an unknown parameter.".format(paramName=paramName))
            return -1

        if not self.ADDRESS_INFO:
            _logger.error("No Devices registered. Aborting...")
            return -1

        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']

        try:
            bus = smbus.SMBus(i2c_ch)
            retVal = bus.read_i2c_block_data(i2c_addr, paramInfo["addr"], paramInfo["regs"])
            bus.close()
        except FileNotFoundError as e:
            _logger.error(e)
            _logger.error("Could not find i2c bus at channel: " + str(i2c_ch) + ", address: " + str(i2c_addr) + ". Check your connection....")
            return -1
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            _logger.error(e)
            return -1

        val = int.from_bytes(retVal, byteorder='big', signed=False)

        ''' Data formating from the register '''
        val &= paramInfo['mask']
        val >>= paramInfo['loc']
        val = self._register_exceptions(paramInfo, val)

        time.sleep(0.01)
        return val

    def write_param(self, devNum, paramName, value):
        if not (paramName in self.REGISTERS_INFO):
            _logger.error(str(paramName) + " is an invalid parameter name")
            return -1

        if paramName in self.REGISTERS_INFO:
            paramInfo = self.REGISTERS_INFO[paramName]
        else:
            _logger.error("{paramName} is an unknown parameter or pin name.".format(paramName=paramName))
            return -1

        if not self.ADDRESS_INFO:
            _logger.error("No Devices registered. Aborting...")
            return -1

        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']

        if (0 == paramInfo["min"]) and (0 == paramInfo["max"]):
            _logger.error(str(paramName) + " is a read-only parameter")
            return -1

        if (value < paramInfo["min"]) or (value > paramInfo["max"]):
            _logger.error("{value} is an invalid value for {paramName}. " +
                          "Must be between {min} and {max}".format(value=value,
                                                                   paramName=paramName,
                                                                   min=paramInfo["min"],
                                                                   max=paramInfo["max"]))
            return -1

        ''' Data formating to put into the register '''
        value <<= paramInfo["loc"]
        value &= paramInfo["mask"]
        value = self._register_exceptions(paramInfo, value)

        try:
            bus = smbus.SMBus(i2c_ch)

            ''' Retrieve value in register '''
            currVal = bus.read_i2c_block_data(i2c_addr, paramInfo["addr"], paramInfo["regs"])
            _logger.debug("In register " + str(paramName) + " = " + str([hex(no) for no in currVal]))
            currVal = int.from_bytes(currVal, byteorder='big')
            ''' Clear all bits concerned with our parameter and keep the others we dont want to affect
                Note this might cause problems if your python is not 64-bits and registers are >32bits '''
            currVal_cleared = currVal & (~paramInfo["mask"])
            ''' Write new value for the parameter '''
            newVal = value + currVal_cleared
            ''' Package as a byte-list '''
            writeBuf = self.int_to_short_list(newVal, fixed_length=paramInfo["regs"])

            _logger.debug("To register " + str(paramName) + " = " + str([hex(no) for no in writeBuf]))
            bus.write_i2c_block_data(i2c_addr, paramInfo["addr"], writeBuf)
            bus.close()
        except FileNotFoundError as e:
            _logger.error(e)
            _logger.error("Could not find i2c bus at channel: " + str(i2c_ch) + ", address: " + str(i2c_addr) + ". Check your connection....")
            return -1
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            _logger.error(e)
            return -1

        time.sleep(0.01)
        return 0


    def int_to_short_list(self, data, fixed_length=None, invert=False):
        """
        Converts an integer to a list of byte-size shorts.
        Ex:    idx          0     1     2
            0x123456 --> [0x12, 0x34, 0x56] (invert=False) (BIG_ENDIAN)
            0x123456 --> [0x56, 0x34, 0x12] (invert=True)  (LITTLE ENDIAN)
        :param data: integer to convert
        :param fixed_length: Force the final length in bytes
        :param invert: Little (False) or big (True) endian
        :return: List of bytes
        """
        retList = []
        if fixed_length:
            for i in range(fixed_length):
                retList.append(data & 0xFF)
                data = data >> 8
        else:
            while(data != 0):
                retList.append(data & 0xFF)
                data = data >> 8
        if invert:
            return retList
        else:
            return retList[::-1]


    def _register_exceptions(self, paramInfo, value):
        """
        Applies formatting exceptions for registers. There are none for the LMK03318, this is here for compatibility.
        :param paramInfo: The info dictionary about the parameter
        :param value: The new to be written to the register or read from the register
        :return: modified value if an exception applies
        """
        return value


    def selftest(self, devNum):
        """
        Run a simple selftest to see if the device responds.
        :param devNum: Device number to test
        :return: <0 on failure, 0 on success
        """
        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']
        val = self.read_param(devNum, "VNDRID")

        if (val != 0x100B):
            _logger.error("Self-test for device " + str(self.DEVICE_NAME) + " on channel: " + str(i2c_ch) + " at address: " + str(i2c_addr) + " failed")
            _logger.error("Expecting: " + str(0x100B) + ", Received: " + str(val))
            return -1
        return 0

    def readout_all_registers(self, devNum):
        """
        Display on the logger the contents of the all the registers of the device.
        :param devNum: Device number
        :return: None
        """
        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']
        _logger.info("==== Device report ====")
        _logger.info("Device Name: " + str(self.DEVICE_NAME))
        _logger.info("I2C channel: " + str(i2c_ch) + " I2C address: " + str(i2c_addr))
        for key in self.REGISTERS_INFO:
            val = self.read_param(i2c_ch, i2c_addr, key)
            _logger.info('Param Name: {ParamName: <20}, Param Value: {Value: <16}'.format(ParamName=key, Value=val))

    def gpio_set(self, devNum, name, value):
        """
        Set the GPIO pin associated to the device.
        :param devNum: Device number
        :param name: Name string of the pin
        :param value: Value to set (True/False)
        :return: <0 on failure, 0 on success
        """
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



    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


class Command:
    """
    This class allows us to use all registers as attributes. Calling the registers with different number of arguments calls
    a read or write operation, depending on what is available.
    For example:
       > d = Device()
       > d.register_name(0)  # read operation of the device number 0
       > d.register_name(0, 1) # writing 1 to the device 0
    """
    def __init__(self, d, name="", acc=None):
        self.__dict__ = {}
        self._name = name
        self._acc = acc

    def __call__(self, *args):
        if len(args) == 2:
            self._acc.write_param(args[0], self._name, args[1])
        elif len(args) == 1:
            return self._acc.read_param(args[0], self._name)
        else:
            _logger.warning("Incorrect number of arguments. Ignoring")

        time.sleep(0.01)

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]



'''
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='LMK03318 utility program.')
    parser.add_argument('channel', help='I2C channel')
    parser.add_argument('address', help='I2C address')
    parser.add_argument('param', help='Parameter name')
    parser.add_argument('-w', default=False, action='store_true', help='Write flag')
    parser.add_argument('-r', default=False, action='store_true', help='Read flag')
    parser.add_argument('-s', default=False, action='store_true', help='Selftest flag')

    args = parser.parse_args()
    print((args))
'''

'''
    def set_frequency(self, devNum, freq):

        """
                F_VCO = (F_REF / R) × D × [(INT + NUM / DEN) / M]
                F_OUT = F_VCO / (P × OUTDIV)
         """
        FVCO = 5000000000
        self.PLL_P(devNum, 7)
        self.CH_0_MUTE(devNum, 0)
        self.CH_3_MUTE(devNum, 0)
        self.INSEL_PLL(devNum, 2)
        self.OUT_3_MODE1(devNum, 0)
        self.OUT_3_SEL(devNum, 1)

        ## Config de base pour le output
        self.PRIBUFSEL(devNum, 1)
        self.AC_MODE_PRI(devNum, 0)
        self.DIFFTERM_PRI(devNum, 1)
        self.TERM2GND_PRI(devNum, 0)
        self.SECBUFSEL(devNum, 3)

        self.OUT_0_SEL(devNum, 1)
        self.OUT_0_MODE1(devNum, 0)
        self.OUT_3_SEL(devNum, 1)
        self.OUT_3_MODE1(devNum, 0)
        self.PLL_NDIV(devNum, 40)
        self.PLLRDIV(devNum, 0)
        self.PLLMDIV(devNum, 1)
        self.OUT_0_1_DIV(devNum, 100)
        self.OUT_2_3_DIV(devNum, 100)
        self.PRI_D(devNum, 0)
        self.PLL_P(devNum, 7)

        self.PLL_PDN(devNum, 1)
        self.PLL_PDN(devNum, 0)

        self.gpio_set(devNum, "SYNC", 0)
        self.gpio_set(devNum, "SYNC", 1)
'''
