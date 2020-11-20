import time
import smbus
from periphery import GPIO

class LMK03318:

    DEVICE_NAME = "LMK03318"

    #All register info concerning all LMK parameters
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

    # Read temperature registers and calculate Celsius
    def read_param(self, i2c_ch, i2c_addr, paramName):
        if not (paramName in self.REGISTERS_INFO):
            print("ERROR :: LMK03318 :: " + str(paramName) + " is an invalid parameter name")
            return -1

        paramInfo = self.REGISTERS_INFO[paramName]

        with smbus.SMBus(i2c_ch) as bus:
            retVal = bus.read_i2c_block_data(i2c_addr, paramInfo["addr"], paramInfo["regs"])

        val = int.from_bytes(retVal, byteorder='big', signed=False)

        # Restrain to concerned bits
        val &= paramInfo['mask']
        # Positions to appropriate bits
        val >>= paramInfo['loc']

        val = self.register_exceptions(paramInfo, val)

        return val

    def write_param(self, i2c_ch, i2c_addr, paramName, value):
        if not (paramName in self.REGISTERS_INFO):
            print("ERROR :: LMK03318 :: " + str(paramName) + " is an invalid parameter name")
            return -1

        paramInfo = self.REGISTERS_INFO[paramName]

        if (1 == paramInfo["min"]) and (1 == paramInfo["max"]):
            print("ERROR :: LMK03318 :: " + str(paramName) + " is a read-only parameter")
            return -1

        if (value < paramInfo["min"]) or (value > paramInfo["max"]):
            print("ERROR :: LMK03318 :: " + str(value) + " is an invalid value")
            return -1

        # Positions to appropriate bits
        value <<= paramInfo["loc"]
        # Restrain to concerned bits
        value &= paramInfo["mask"]

        value = self.register_exceptions(paramInfo, value)

        with smbus.SMBus(i2c_ch) as bus:
            currVal = bus.read_i2c_block_data(i2c_addr, paramInfo["addr"], paramInfo["regs"])
            writeBuf = (value).to_bytes(paramInfo["regs"], 'big')
            for i in paramInfo["regs"]:
                writeBuf[i] |= (currVal[i] & (~paramInfo["mask"] >> 8 * i))

            bus.write_i2c_block_data(i2c_addr, paramInfo["addr"], writeBuf)

        return 0


    # Here are all the formatting exceptions for registers.
    def register_exceptions(self, paramInfo, value):
        return value


    def selftest(self, i2c_ch, i2c_addr):
        val = self.read_param(i2c_ch, i2c_addr, "VNDRID")

        if (val != 0x100B):
            print("ERROR :: LMK03318 :: Self-test for device on channel: " + str(i2c_ch) + " at address: " + str(i2c_addr) + " failed")
            return -1

        return 0

    def readout_all_registers(self, i2c_ch, i2c_addr,):
        print("==== Device report ====")
        print("Device Name: " + str(self.DEVICE_NAME))
        print("I2C channel: " + str(i2c_ch) + " I2C address: " + str(i2c_addr))
        for key in self.REGISTERS_INFO:
            val = self.read_param(i2c_ch, i2c_addr, key)
            print('Param Name: {ParamName: <20}, Param Value: {Value: <16}'.format(ParamName=key, Value=val))


    def gpio_set(self, path, pin, val, dir="out"):
        with GPIO(path, pin, dir) as gpio_out:
            gpio_out.write(val)


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
