Using launch settings from /Users/boudewijnvangroos/zero/zero-sail-systems-mqtt-adapter/SailSystemMqttAdapter/Properties/launchSettings.json...
Project Name: 3094_SailPLC
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$defs": {
    "EF": {
      "type": "object",
      "properties": {
        "i_FPKIsoDC": {
          "type": "integer"
        },
        "i_HYPIsoDC": {
          "type": "integer"
        },
        "i_LAZIsoDC": {
          "type": "integer"
        },
        "i_MAINIsoDC": {
          "type": "integer"
        },
        "x_FPKIsoDC": {
          "type": "boolean"
        },
        "x_HYPIsoDC": {
          "type": "boolean"
        },
        "x_LAZIsoDC": {
          "type": "boolean"
        },
        "x_MAINIsoDC": {
          "type": "boolean"
        }
      }
    },
    "F0401_MzznHdFrlr": {
      "type": "object",
      "properties": {
        "ix_SnsrHdslLck": {
          "type": "boolean"
        },
        "ix_SnsrHdslLckOvrhst": {
          "type": "boolean"
        }
      }
    },
    "FE207_MnHlyrd": {
      "type": "object",
      "properties": {
        "ix_SnsrBmRfLck1": {
          "type": "boolean"
        },
        "ix_SnsrBmRfLck2": {
          "type": "boolean"
        },
        "ix_SnsrBmRfLck3": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck1": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck1Ovrhst": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck2": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck2Ovrhst": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck3": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck3Ovrhst": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLckFh": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLckFhOvrhst": {
          "type": "boolean"
        }
      }
    },
    "FE404_MzznHlyrd": {
      "type": "object",
      "properties": {
        "ix_SnsrBmRfLck1": {
          "type": "boolean"
        },
        "ix_SnsrBmRfLck2": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck1": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck1Ovrhst": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck2": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLck2Ovrhst": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLckFh": {
          "type": "boolean"
        },
        "ix_SnsrHlyrdLckFhOvrhst": {
          "type": "boolean"
        }
      }
    },
    "ist_LoadBottom": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_LoadAt4rmA": {
          "type": "integer"
        },
        "i_LoadChangePermA": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "r_RawSensor": {
          "type": "number"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    },
    "ist_LoadRod": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_LoadAt4rmA": {
          "type": "integer"
        },
        "i_LoadChangePermA": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "r_RawSensor": {
          "type": "number"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    },
    "ist_SnsrKeelPos1": {
      "type": "object",
      "properties": {
        "i_CylinderLength": {
          "type": "integer"
        },
        "i_MaxPosition": {
          "type": "integer"
        },
        "i_MinPosition": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_Position_permille": {
          "type": "integer"
        },
        "i_PositionChangemA": {
          "type": "integer"
        },
        "i_PositionStart": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        },
        "x_MinLimitReached": {
          "type": "boolean"
        }
      }
    },
    "ist_SnsrKeelPos2": {
      "type": "object",
      "properties": {
        "i_CylinderLength": {
          "type": "integer"
        },
        "i_MaxPosition": {
          "type": "integer"
        },
        "i_MinPosition": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_Position_permille": {
          "type": "integer"
        },
        "i_PositionChangemA": {
          "type": "integer"
        },
        "i_PositionStart": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        },
        "x_MinLimitReached": {
          "type": "boolean"
        }
      }
    },
    "sDrive": {
      "type": "object",
      "properties": {
        "duiRunningTime": {
          "type": "integer"
        },
        "iActualSpeed": {
          "type": "integer"
        },
        "iSpeedDemand": {
          "type": "integer"
        },
        "ow_Alarmcode": {
          "type": "integer"
        },
        "rActualTorque": {
          "type": "number"
        },
        "rDcLinkVoltage": {
          "type": "number"
        },
        "rHeatsinkTemp": {
          "type": "number"
        },
        "rTorqueDemand": {
          "type": "number"
        },
        "wCanState": {
          "type": "integer"
        },
        "x_CanAlive": {
          "type": "boolean"
        },
        "xBrake": {
          "type": "boolean"
        },
        "xFault": {
          "type": "boolean"
        },
        "xReady": {
          "type": "boolean"
        },
        "xRun": {
          "type": "boolean"
        },
        "xRunning": {
          "type": "boolean"
        }
      }
    },
    "sDriveA": {
      "type": "object",
      "properties": {
        "duiRunningTime": {
          "type": "integer"
        },
        "iActualSpeed": {
          "type": "integer"
        },
        "iSpeedDemand": {
          "type": "integer"
        },
        "rActualTorque": {
          "type": "number"
        },
        "rDcLinkVoltage": {
          "type": "number"
        },
        "rHeatsinkTemp": {
          "type": "number"
        },
        "rTorqueDemand": {
          "type": "number"
        },
        "wActiveFault": {
          "type": "integer"
        },
        "x_CanAlive": {
          "type": "boolean"
        },
        "xBrake": {
          "type": "boolean"
        },
        "xFault": {
          "type": "boolean"
        },
        "xReady": {
          "type": "boolean"
        },
        "xRun": {
          "type": "boolean"
        },
        "xRunning": {
          "type": "boolean"
        }
      }
    },
    "sDriveB": {
      "type": "object",
      "properties": {
        "duiRunningTime": {
          "type": "integer"
        },
        "iActualSpeed": {
          "type": "integer"
        },
        "iSpeedDemand": {
          "type": "integer"
        },
        "rActualTorque": {
          "type": "number"
        },
        "rDcLinkVoltage": {
          "type": "number"
        },
        "rHeatsinkTemp": {
          "type": "number"
        },
        "rTorqueDemand": {
          "type": "number"
        },
        "wActiveFault": {
          "type": "integer"
        },
        "x_CanAlive": {
          "type": "boolean"
        },
        "xBrake": {
          "type": "boolean"
        },
        "xFault": {
          "type": "boolean"
        },
        "xReady": {
          "type": "boolean"
        },
        "xRun": {
          "type": "boolean"
        },
        "xRunning": {
          "type": "boolean"
        }
      }
    },
    "sDriveBw": {
      "type": "object",
      "properties": {
        "duiRunningTime": {
          "type": "integer"
        },
        "iActualSpeed": {
          "type": "integer"
        },
        "iSpeedDemand": {
          "type": "integer"
        },
        "ow_Alarmcode": {
          "type": "integer"
        },
        "rActualTorque": {
          "type": "number"
        },
        "rDcLinkVoltage": {
          "type": "number"
        },
        "rHeatsinkTemp": {
          "type": "number"
        },
        "rTorqueDemand": {
          "type": "number"
        },
        "wCanState": {
          "type": "integer"
        },
        "x_CanAlive": {
          "type": "boolean"
        },
        "xBrake": {
          "type": "boolean"
        },
        "xFault": {
          "type": "boolean"
        },
        "xReady": {
          "type": "boolean"
        },
        "xRun": {
          "type": "boolean"
        },
        "xRunning": {
          "type": "boolean"
        }
      }
    },
    "sFrpk": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "i_Temperature": {
          "type": "integer"
        },
        "iMaxTemperature": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_NoFeedbackAlarm": {
          "type": "boolean"
        },
        "x_NoFlowAlarm": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_TempAlarm": {
          "type": "boolean"
        }
      }
    },
    "sHlmPs": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "ix_0202_JstckOOCMnBmVng": {
          "type": "boolean"
        },
        "ix_0203_BtnMnChckstyDflctrEase": {
          "type": "boolean"
        },
        "ix_0203_BtnMnChckstyDflctrPull": {
          "type": "boolean"
        },
        "ix_0204_JstckOOCMnBmPrvntr": {
          "type": "boolean"
        },
        "ix_0301_BtnKeelLftDwn": {
          "type": "boolean"
        },
        "ix_0301_BtnKeelLftUp": {
          "type": "boolean"
        },
        "ix_0502_JstckOOCMzznBmVng": {
          "type": "boolean"
        },
        "ix_0503_BtnMzznChckstyDflctrEase": {
          "type": "boolean"
        },
        "ix_0503_BtnMzznChckstyDflctrPull": {
          "type": "boolean"
        },
        "ix_0506_JstckOOCMzznBmPrvntr": {
          "type": "boolean"
        },
        "ix_BtnActvtRnnrFnct": {
          "type": "boolean"
        },
        "ix_BtnActvtSlFnctPs": {
          "type": "boolean"
        },
        "ix_E205_JstckOOCMnSht": {
          "type": "boolean"
        },
        "ix_E401_BtnMnRnnrPsEase": {
          "type": "boolean"
        },
        "ix_E401_BtnMnRnnrPsPull": {
          "type": "boolean"
        },
        "ix_E402_BtnMzznRnnrPsEase": {
          "type": "boolean"
        },
        "ix_E402_BtnMzznRnnrPsPull": {
          "type": "boolean"
        },
        "ix_E405_JstckOOCMnTrvllr": {
          "type": "boolean"
        },
        "ix_E501_BtnMnRnnrSbEase": {
          "type": "boolean"
        },
        "ix_E501_BtnMnRnnrSbPull": {
          "type": "boolean"
        },
        "ix_E502_BtnMzznRnnrSbEase": {
          "type": "boolean"
        },
        "ix_E502_BtnMzznRnnrSbPull": {
          "type": "boolean"
        },
        "ix_E504_JstckOOCMzznSht": {
          "type": "boolean"
        },
        "s0202_JstckMnBmVng/iSetpoint": {
          "type": "integer"
        },
        "s0202_JstckMnBmVng/x_Enabled": {
          "type": "boolean"
        },
        "s0202_JstckMnBmVng/x_onOff": {
          "type": "boolean"
        },
        "s0202_JstckMnBmVng/x_Ooc": {
          "type": "boolean"
        },
        "s0204_JstckMnBmPrvntr/iSetpoint": {
          "type": "integer"
        },
        "s0204_JstckMnBmPrvntr/x_Enabled": {
          "type": "boolean"
        },
        "s0204_JstckMnBmPrvntr/x_onOff": {
          "type": "boolean"
        },
        "s0204_JstckMnBmPrvntr/x_Ooc": {
          "type": "boolean"
        },
        "s0502_JstckMzznBmVng/iSetpoint": {
          "type": "integer"
        },
        "s0502_JstckMzznBmVng/x_Enabled": {
          "type": "boolean"
        },
        "s0502_JstckMzznBmVng/x_onOff": {
          "type": "boolean"
        },
        "s0502_JstckMzznBmVng/x_Ooc": {
          "type": "boolean"
        },
        "s0506_JstckMzznBmPrvntr/iSetpoint": {
          "type": "integer"
        },
        "s0506_JstckMzznBmPrvntr/x_Enabled": {
          "type": "boolean"
        },
        "s0506_JstckMzznBmPrvntr/x_onOff": {
          "type": "boolean"
        },
        "s0506_JstckMzznBmPrvntr/x_Ooc": {
          "type": "boolean"
        },
        "sE205_JstckMnSht/iSetpoint": {
          "type": "integer"
        },
        "sE205_JstckMnSht/x_Enabled": {
          "type": "boolean"
        },
        "sE205_JstckMnSht/x_onOff": {
          "type": "boolean"
        },
        "sE205_JstckMnSht/x_Ooc": {
          "type": "boolean"
        },
        "sE405_JstckMnTrvllr/iSetpoint": {
          "type": "integer"
        },
        "sE405_JstckMnTrvllr/x_Enabled": {
          "type": "boolean"
        },
        "sE405_JstckMnTrvllr/x_onOff": {
          "type": "boolean"
        },
        "sE405_JstckMnTrvllr/x_Ooc": {
          "type": "boolean"
        },
        "sE504_JstckMzznSht/iSetpoint": {
          "type": "integer"
        },
        "sE504_JstckMzznSht/x_Enabled": {
          "type": "boolean"
        },
        "sE504_JstckMzznSht/x_onOff": {
          "type": "boolean"
        },
        "sE504_JstckMzznSht/x_Ooc": {
          "type": "boolean"
        }
      }
    },
    "sHlmSb": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "ix_0202_JstckOOCMnBmVng": {
          "type": "boolean"
        },
        "ix_0204_JstckOOCMnBmPrvntr": {
          "type": "boolean"
        },
        "ix_0301_BtnKeelLftDwn": {
          "type": "boolean"
        },
        "ix_0301_BtnKeelLftUp": {
          "type": "boolean"
        },
        "ix_0502_JstckOOCMzznBmVng": {
          "type": "boolean"
        },
        "ix_0506_JstckOOCMzznBmPrvntr": {
          "type": "boolean"
        },
        "ix_BtnActvtSlFnctSb": {
          "type": "boolean"
        },
        "ix_E205_JstckOOCMnSht": {
          "type": "boolean"
        },
        "ix_E405_JstckOOCMnTrvllr": {
          "type": "boolean"
        },
        "ix_E504_JstckOOCMzznSht": {
          "type": "boolean"
        },
        "s0202_JstckMnBmVng/iSetpoint": {
          "type": "integer"
        },
        "s0202_JstckMnBmVng/x_Enabled": {
          "type": "boolean"
        },
        "s0202_JstckMnBmVng/x_onOff": {
          "type": "boolean"
        },
        "s0202_JstckMnBmVng/x_Ooc": {
          "type": "boolean"
        },
        "s0204_JstckMnBmPrvntr/iSetpoint": {
          "type": "integer"
        },
        "s0204_JstckMnBmPrvntr/x_Enabled": {
          "type": "boolean"
        },
        "s0204_JstckMnBmPrvntr/x_onOff": {
          "type": "boolean"
        },
        "s0204_JstckMnBmPrvntr/x_Ooc": {
          "type": "boolean"
        },
        "s0502_JstckMzznBmVng/iSetpoint": {
          "type": "integer"
        },
        "s0502_JstckMzznBmVng/x_Enabled": {
          "type": "boolean"
        },
        "s0502_JstckMzznBmVng/x_onOff": {
          "type": "boolean"
        },
        "s0502_JstckMzznBmVng/x_Ooc": {
          "type": "boolean"
        },
        "s0506_JstckMzznBmPrvntr/iSetpoint": {
          "type": "integer"
        },
        "s0506_JstckMzznBmPrvntr/x_Enabled": {
          "type": "boolean"
        },
        "s0506_JstckMzznBmPrvntr/x_onOff": {
          "type": "boolean"
        },
        "s0506_JstckMzznBmPrvntr/x_Ooc": {
          "type": "boolean"
        },
        "sE205_JstckMnSht/iSetpoint": {
          "type": "integer"
        },
        "sE205_JstckMnSht/x_Enabled": {
          "type": "boolean"
        },
        "sE205_JstckMnSht/x_onOff": {
          "type": "boolean"
        },
        "sE205_JstckMnSht/x_Ooc": {
          "type": "boolean"
        },
        "sE405_JstckMnTrvllr/iSetpoint": {
          "type": "integer"
        },
        "sE405_JstckMnTrvllr/x_Enabled": {
          "type": "boolean"
        },
        "sE405_JstckMnTrvllr/x_onOff": {
          "type": "boolean"
        },
        "sE405_JstckMnTrvllr/x_Ooc": {
          "type": "boolean"
        },
        "sE504_JstckMzznSht/iSetpoint": {
          "type": "integer"
        },
        "sE504_JstckMzznSht/x_Enabled": {
          "type": "boolean"
        },
        "sE504_JstckMzznSht/x_onOff": {
          "type": "boolean"
        },
        "sE504_JstckMzznSht/x_Ooc": {
          "type": "boolean"
        }
      }
    },
    "sHlyrdpt": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "i_Temperature": {
          "type": "integer"
        },
        "iMaxTemperature": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_NoFeedbackAlarm": {
          "type": "boolean"
        },
        "x_NoFlowAlarm": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_TempAlarm": {
          "type": "boolean"
        }
      }
    },
    "sLoad": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_LoadAt4rmA": {
          "type": "integer"
        },
        "i_LoadChangePermA": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "r_RawSensor": {
          "type": "number"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    },
    "sLzrtt": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "i_Temperature": {
          "type": "integer"
        },
        "iMaxTemperature": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_NoFeedbackAlarm": {
          "type": "boolean"
        },
        "x_NoFlowAlarm": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_TempAlarm": {
          "type": "boolean"
        }
      }
    },
    "sRaceCp": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "ix_0202_JstckOOCMnBmVng": {
          "type": "boolean"
        },
        "ix_0204_JstckOOCMnBmPrvntr": {
          "type": "boolean"
        },
        "ix_0206_JstckOOCBldTwkrPs": {
          "type": "boolean"
        },
        "ix_E101_JstckOOCCdZrFrlr": {
          "type": "boolean"
        },
        "ix_E102_JstckOOCBldFrlr": {
          "type": "boolean"
        },
        "ix_E103_JstckOOCStyslFrlr": {
          "type": "boolean"
        },
        "ix_E201_JstckOOCBldShtPs": {
          "type": "boolean"
        },
        "ix_E203_JstckOOCStyslShtPs": {
          "type": "boolean"
        },
        "ix_E205_JstckOOCMnSht": {
          "type": "boolean"
        },
        "ix_E301_JstckOOCBldShtSb": {
          "type": "boolean"
        },
        "ix_E303_JstckOOCStyslShtSb": {
          "type": "boolean"
        },
        "ix_E405_JstckOOCMnTrvllr": {
          "type": "boolean"
        },
        "s0202_JstckMnBmVng/iSetpoint": {
          "type": "integer"
        },
        "s0202_JstckMnBmVng/x_Enabled": {
          "type": "boolean"
        },
        "s0202_JstckMnBmVng/x_onOff": {
          "type": "boolean"
        },
        "s0202_JstckMnBmVng/x_Ooc": {
          "type": "boolean"
        },
        "s0204_JstckMnBmPrvntr/iSetpoint": {
          "type": "integer"
        },
        "s0204_JstckMnBmPrvntr/x_Enabled": {
          "type": "boolean"
        },
        "s0204_JstckMnBmPrvntr/x_onOff": {
          "type": "boolean"
        },
        "s0204_JstckMnBmPrvntr/x_Ooc": {
          "type": "boolean"
        },
        "s0206_JstckBldTwkrPs/iSetpoint": {
          "type": "integer"
        },
        "s0206_JstckBldTwkrPs/x_Enabled": {
          "type": "boolean"
        },
        "s0206_JstckBldTwkrPs/x_onOff": {
          "type": "boolean"
        },
        "s0206_JstckBldTwkrPs/x_Ooc": {
          "type": "boolean"
        },
        "sE101_JstckCdZrFrlr/iSetpoint": {
          "type": "integer"
        },
        "sE101_JstckCdZrFrlr/x_Enabled": {
          "type": "boolean"
        },
        "sE101_JstckCdZrFrlr/x_onOff": {
          "type": "boolean"
        },
        "sE101_JstckCdZrFrlr/x_Ooc": {
          "type": "boolean"
        },
        "sE102_JstckBldFrlr/iSetpoint": {
          "type": "integer"
        },
        "sE102_JstckBldFrlr/x_Enabled": {
          "type": "boolean"
        },
        "sE102_JstckBldFrlr/x_onOff": {
          "type": "boolean"
        },
        "sE102_JstckBldFrlr/x_Ooc": {
          "type": "boolean"
        },
        "sE103_JstckStyslFrlr/iSetpoint": {
          "type": "integer"
        },
        "sE103_JstckStyslFrlr/x_Enabled": {
          "type": "boolean"
        },
        "sE103_JstckStyslFrlr/x_onOff": {
          "type": "boolean"
        },
        "sE103_JstckStyslFrlr/x_Ooc": {
          "type": "boolean"
        },
        "sE201_JstckBldShtPs/iSetpoint": {
          "type": "integer"
        },
        "sE201_JstckBldShtPs/x_Enabled": {
          "type": "boolean"
        },
        "sE201_JstckBldShtPs/x_onOff": {
          "type": "boolean"
        },
        "sE201_JstckBldShtPs/x_Ooc": {
          "type": "boolean"
        },
        "sE203_JstckStyslShtPs/iSetpoint": {
          "type": "integer"
        },
        "sE203_JstckStyslShtPs/x_Enabled": {
          "type": "boolean"
        },
        "sE203_JstckStyslShtPs/x_onOff": {
          "type": "boolean"
        },
        "sE203_JstckStyslShtPs/x_Ooc": {
          "type": "boolean"
        },
        "sE205_JstckMnSht/iSetpoint": {
          "type": "integer"
        },
        "sE205_JstckMnSht/x_Enabled": {
          "type": "boolean"
        },
        "sE205_JstckMnSht/x_onOff": {
          "type": "boolean"
        },
        "sE205_JstckMnSht/x_Ooc": {
          "type": "boolean"
        },
        "sE301_JstckBldShtSb/iSetpoint": {
          "type": "integer"
        },
        "sE301_JstckBldShtSb/x_Enabled": {
          "type": "boolean"
        },
        "sE301_JstckBldShtSb/x_onOff": {
          "type": "boolean"
        },
        "sE301_JstckBldShtSb/x_Ooc": {
          "type": "boolean"
        },
        "sE303_JstckStyslShtSb/iSetpoint": {
          "type": "integer"
        },
        "sE303_JstckStyslShtSb/x_Enabled": {
          "type": "boolean"
        },
        "sE303_JstckStyslShtSb/x_onOff": {
          "type": "boolean"
        },
        "sE303_JstckStyslShtSb/x_Ooc": {
          "type": "boolean"
        },
        "sE405_JstckMnTrvllr/iSetpoint": {
          "type": "integer"
        },
        "sE405_JstckMnTrvllr/x_Enabled": {
          "type": "boolean"
        },
        "sE405_JstckMnTrvllr/x_onOff": {
          "type": "boolean"
        },
        "sE405_JstckMnTrvllr/x_Ooc": {
          "type": "boolean"
        }
      }
    },
    "sRcAnchr": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "x_Aux1": {
          "type": "boolean"
        },
        "x_Aux2": {
          "type": "boolean"
        },
        "x_Aux3": {
          "type": "boolean"
        },
        "x_Aux4": {
          "type": "boolean"
        },
        "x_Aux5": {
          "type": "boolean"
        },
        "x_Aux6": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_fifiPumpOff": {
          "type": "boolean"
        },
        "x_fifiPumpOn": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_PsRcInHigh": {
          "type": "boolean"
        },
        "x_PsRcInLow": {
          "type": "boolean"
        },
        "x_PsRcOutHigh": {
          "type": "boolean"
        },
        "x_PsRcOutLow": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_SbRcInHigh": {
          "type": "boolean"
        },
        "x_SbRcInLow": {
          "type": "boolean"
        },
        "x_SbRcOutHigh": {
          "type": "boolean"
        },
        "x_SbRcOutLow": {
          "type": "boolean"
        },
        "x_Start1": {
          "type": "boolean"
        },
        "x_Start2": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        }
      }
    },
    "sRcCrwsNst": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "x_Down": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_Start": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        },
        "x_Up": {
          "type": "boolean"
        }
      }
    },
    "sRcDrum": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "sCode/iSetpoint": {
          "type": "integer"
        },
        "sCode/x_Enabled": {
          "type": "boolean"
        },
        "sCode/x_onOff": {
          "type": "boolean"
        },
        "sCode/x_Ooc": {
          "type": "boolean"
        },
        "sSailDrum/iSetpoint": {
          "type": "integer"
        },
        "sSailDrum/x_Enabled": {
          "type": "boolean"
        },
        "sSailDrum/x_onOff": {
          "type": "boolean"
        },
        "sSailDrum/x_Ooc": {
          "type": "boolean"
        },
        "sStaysail/iSetpoint": {
          "type": "integer"
        },
        "sStaysail/x_Enabled": {
          "type": "boolean"
        },
        "sStaysail/x_onOff": {
          "type": "boolean"
        },
        "sStaysail/x_Ooc": {
          "type": "boolean"
        },
        "sStaysailTack/iSetpoint": {
          "type": "integer"
        },
        "sStaysailTack/x_Enabled": {
          "type": "boolean"
        },
        "sStaysailTack/x_onOff": {
          "type": "boolean"
        },
        "sStaysailTack/x_Ooc": {
          "type": "boolean"
        },
        "x_Aux1": {
          "type": "boolean"
        },
        "x_Aux2": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_Start": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        }
      }
    },
    "sRcHead": {
      "type": "object",
      "properties": {
        "b_errorMessage": {
          "type": "string"
        },
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "sBladePs/iSetpoint": {
          "type": "integer"
        },
        "sBladePs/x_Enabled": {
          "type": "boolean"
        },
        "sBladePs/x_onOff": {
          "type": "boolean"
        },
        "sBladePs/x_Ooc": {
          "type": "boolean"
        },
        "sBladeSb/iSetpoint": {
          "type": "integer"
        },
        "sBladeSb/x_Enabled": {
          "type": "boolean"
        },
        "sBladeSb/x_onOff": {
          "type": "boolean"
        },
        "sBladeSb/x_Ooc": {
          "type": "boolean"
        },
        "sStaysailPs/iSetpoint": {
          "type": "integer"
        },
        "sStaysailPs/x_Enabled": {
          "type": "boolean"
        },
        "sStaysailPs/x_onOff": {
          "type": "boolean"
        },
        "sStaysailPs/x_Ooc": {
          "type": "boolean"
        },
        "sStaysailSb/iSetpoint": {
          "type": "integer"
        },
        "sStaysailSb/x_Enabled": {
          "type": "boolean"
        },
        "sStaysailSb/x_onOff": {
          "type": "boolean"
        },
        "sStaysailSb/x_Ooc": {
          "type": "boolean"
        },
        "x_Aux1": {
          "type": "boolean"
        },
        "x_Aux2": {
          "type": "boolean"
        },
        "x_BladeLeadDown": {
          "type": "boolean"
        },
        "x_BladeLeadUp": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_FurlBladeEase": {
          "type": "boolean"
        },
        "x_FurlBladePull": {
          "type": "boolean"
        },
        "x_FurlCodeDown": {
          "type": "boolean"
        },
        "x_FurlCodeUp": {
          "type": "boolean"
        },
        "x_FurlStayslEase": {
          "type": "boolean"
        },
        "x_FurlStayslPull": {
          "type": "boolean"
        },
        "x_htouch500": {
          "type": "boolean"
        },
        "x_htouch501": {
          "type": "boolean"
        },
        "x_htouch502": {
          "type": "boolean"
        },
        "x_htouch503": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_LowBattery": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_Start": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TackBladeEase": {
          "type": "boolean"
        },
        "x_TackBladePull": {
          "type": "boolean"
        },
        "x_TackCodeDown": {
          "type": "boolean"
        },
        "x_TackCodeUp": {
          "type": "boolean"
        },
        "x_TackStayslEase": {
          "type": "boolean"
        },
        "x_TackStayslPull": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        }
      }
    },
    "sRcMain": {
      "type": "object",
      "properties": {
        "b_errorMessage": {
          "type": "string"
        },
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "sHalyard/iSetpoint": {
          "type": "integer"
        },
        "sHalyard/x_Enabled": {
          "type": "boolean"
        },
        "sHalyard/x_onOff": {
          "type": "boolean"
        },
        "sHalyard/x_Ooc": {
          "type": "boolean"
        },
        "sRunnersPs/iSetpoint": {
          "type": "integer"
        },
        "sRunnersPs/x_Enabled": {
          "type": "boolean"
        },
        "sRunnersPs/x_onOff": {
          "type": "boolean"
        },
        "sRunnersPs/x_Ooc": {
          "type": "boolean"
        },
        "sRunnersSb/iSetpoint": {
          "type": "integer"
        },
        "sRunnersSb/x_Enabled": {
          "type": "boolean"
        },
        "sRunnersSb/x_onOff": {
          "type": "boolean"
        },
        "sRunnersSb/x_Ooc": {
          "type": "boolean"
        },
        "sSheet/iSetpoint": {
          "type": "integer"
        },
        "sSheet/x_Enabled": {
          "type": "boolean"
        },
        "sSheet/x_onOff": {
          "type": "boolean"
        },
        "sSheet/x_Ooc": {
          "type": "boolean"
        },
        "x_Aux1": {
          "type": "boolean"
        },
        "x_Aux2": {
          "type": "boolean"
        },
        "x_CunninghamEase": {
          "type": "boolean"
        },
        "x_CunninghamPull": {
          "type": "boolean"
        },
        "x_DeflectorEase": {
          "type": "boolean"
        },
        "x_DeflectorPull": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_htouch500": {
          "type": "boolean"
        },
        "x_htouch501": {
          "type": "boolean"
        },
        "x_htouch502": {
          "type": "boolean"
        },
        "x_htouch503": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_LowBattery": {
          "type": "boolean"
        },
        "x_OuthaulEase": {
          "type": "boolean"
        },
        "x_OuthaulPull": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_PreventerEase": {
          "type": "boolean"
        },
        "x_PreventerPull": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_Start": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        },
        "x_TravelerLeft": {
          "type": "boolean"
        },
        "x_TravelerRight": {
          "type": "boolean"
        },
        "x_VangDown": {
          "type": "boolean"
        },
        "x_VangUp": {
          "type": "boolean"
        }
      }
    },
    "sRcMntnc": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_FuncIn_1st": {
          "type": "boolean"
        },
        "ix_FuncIn_2nd": {
          "type": "boolean"
        },
        "ix_FuncOut_1st": {
          "type": "boolean"
        },
        "ix_FuncOut_2nd": {
          "type": "boolean"
        },
        "ix_MainIn_1st": {
          "type": "boolean"
        },
        "ix_MainIn_2nd": {
          "type": "boolean"
        },
        "ix_MainOut_1st": {
          "type": "boolean"
        },
        "ix_MainOut_2nd": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "ix_SecIn_1st": {
          "type": "boolean"
        },
        "ix_SecIn_2nd": {
          "type": "boolean"
        },
        "ix_SecOut_1st": {
          "type": "boolean"
        },
        "ix_SecOut_2nd": {
          "type": "boolean"
        },
        "x_Active": {
          "type": "boolean"
        },
        "x_Aux1": {
          "type": "boolean"
        },
        "x_Aux2": {
          "type": "boolean"
        },
        "x_Aux3": {
          "type": "boolean"
        },
        "x_Aux4": {
          "type": "boolean"
        },
        "x_Aux5": {
          "type": "boolean"
        },
        "x_Aux6": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        },
        "xStart1": {
          "type": "boolean"
        },
        "xStart2": {
          "type": "boolean"
        }
      }
    },
    "sRcMzzn": {
      "type": "object",
      "properties": {
        "b_errorMessage": {
          "type": "string"
        },
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "sHalyard/iSetpoint": {
          "type": "integer"
        },
        "sHalyard/x_Enabled": {
          "type": "boolean"
        },
        "sHalyard/x_onOff": {
          "type": "boolean"
        },
        "sHalyard/x_Ooc": {
          "type": "boolean"
        },
        "sRunnersPs/iSetpoint": {
          "type": "integer"
        },
        "sRunnersPs/x_Enabled": {
          "type": "boolean"
        },
        "sRunnersPs/x_onOff": {
          "type": "boolean"
        },
        "sRunnersPs/x_Ooc": {
          "type": "boolean"
        },
        "sRunnersSb/iSetpoint": {
          "type": "integer"
        },
        "sRunnersSb/x_Enabled": {
          "type": "boolean"
        },
        "sRunnersSb/x_onOff": {
          "type": "boolean"
        },
        "sRunnersSb/x_Ooc": {
          "type": "boolean"
        },
        "sSheet/iSetpoint": {
          "type": "integer"
        },
        "sSheet/x_Enabled": {
          "type": "boolean"
        },
        "sSheet/x_onOff": {
          "type": "boolean"
        },
        "sSheet/x_Ooc": {
          "type": "boolean"
        },
        "x_Aux1": {
          "type": "boolean"
        },
        "x_Aux2": {
          "type": "boolean"
        },
        "x_CunninghamEase": {
          "type": "boolean"
        },
        "x_CunninghamPull": {
          "type": "boolean"
        },
        "x_DeflectorEase": {
          "type": "boolean"
        },
        "x_DeflectorPull": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_htouch500": {
          "type": "boolean"
        },
        "x_htouch501": {
          "type": "boolean"
        },
        "x_htouch502": {
          "type": "boolean"
        },
        "x_htouch503": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_LowBattery": {
          "type": "boolean"
        },
        "x_MzJibFurlIn": {
          "type": "boolean"
        },
        "x_MzJibFurlOut": {
          "type": "boolean"
        },
        "x_MzJibTackDown": {
          "type": "boolean"
        },
        "x_MzJibTackUp": {
          "type": "boolean"
        },
        "x_OuthaulEase": {
          "type": "boolean"
        },
        "x_OuthaulPull": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_PreventerEase": {
          "type": "boolean"
        },
        "x_PreventerPull": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_Start": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        },
        "x_VangDown": {
          "type": "boolean"
        },
        "x_VangUp": {
          "type": "boolean"
        }
      }
    },
    "sRcSpare1": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "sJoystick1/iSetpoint": {
          "type": "integer"
        },
        "sJoystick1/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick1/x_onOff": {
          "type": "boolean"
        },
        "sJoystick1/x_Ooc": {
          "type": "boolean"
        },
        "sJoystick2/iSetpoint": {
          "type": "integer"
        },
        "sJoystick2/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick2/x_onOff": {
          "type": "boolean"
        },
        "sJoystick2/x_Ooc": {
          "type": "boolean"
        },
        "sJoystick3/iSetpoint": {
          "type": "integer"
        },
        "sJoystick3/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick3/x_onOff": {
          "type": "boolean"
        },
        "sJoystick3/x_Ooc": {
          "type": "boolean"
        },
        "sJoystick4/iSetpoint": {
          "type": "integer"
        },
        "sJoystick4/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick4/x_onOff": {
          "type": "boolean"
        },
        "sJoystick4/x_Ooc": {
          "type": "boolean"
        },
        "x_Aux1": {
          "type": "boolean"
        },
        "x_Aux2": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_Start": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        }
      }
    },
    "sRcSpare2": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "sJoystick1/iSetpoint": {
          "type": "integer"
        },
        "sJoystick1/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick1/x_onOff": {
          "type": "boolean"
        },
        "sJoystick1/x_Ooc": {
          "type": "boolean"
        },
        "sJoystick2/iSetpoint": {
          "type": "integer"
        },
        "sJoystick2/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick2/x_onOff": {
          "type": "boolean"
        },
        "sJoystick2/x_Ooc": {
          "type": "boolean"
        },
        "sJoystick3/iSetpoint": {
          "type": "integer"
        },
        "sJoystick3/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick3/x_onOff": {
          "type": "boolean"
        },
        "sJoystick3/x_Ooc": {
          "type": "boolean"
        },
        "sJoystick4/iSetpoint": {
          "type": "integer"
        },
        "sJoystick4/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick4/x_onOff": {
          "type": "boolean"
        },
        "sJoystick4/x_Ooc": {
          "type": "boolean"
        },
        "x_Aux1": {
          "type": "boolean"
        },
        "x_Aux2": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_Start": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        }
      }
    },
    "sRcSpare3": {
      "type": "object",
      "properties": {
        "Enable/x_Enabled": {
          "type": "boolean"
        },
        "Enable/x_ExtOnOff": {
          "type": "boolean"
        },
        "Enable/x_OnOff": {
          "type": "boolean"
        },
        "i_rssi": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_Running": {
          "type": "boolean"
        },
        "sJoystick1/iSetpoint": {
          "type": "integer"
        },
        "sJoystick1/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick1/x_onOff": {
          "type": "boolean"
        },
        "sJoystick1/x_Ooc": {
          "type": "boolean"
        },
        "sJoystick2/iSetpoint": {
          "type": "integer"
        },
        "sJoystick2/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick2/x_onOff": {
          "type": "boolean"
        },
        "sJoystick2/x_Ooc": {
          "type": "boolean"
        },
        "sJoystick3/iSetpoint": {
          "type": "integer"
        },
        "sJoystick3/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick3/x_onOff": {
          "type": "boolean"
        },
        "sJoystick3/x_Ooc": {
          "type": "boolean"
        },
        "sJoystick4/iSetpoint": {
          "type": "integer"
        },
        "sJoystick4/x_Enabled": {
          "type": "boolean"
        },
        "sJoystick4/x_onOff": {
          "type": "boolean"
        },
        "sJoystick4/x_Ooc": {
          "type": "boolean"
        },
        "x_Aux1": {
          "type": "boolean"
        },
        "x_Aux2": {
          "type": "boolean"
        },
        "x_Estop": {
          "type": "boolean"
        },
        "x_Linked": {
          "type": "boolean"
        },
        "x_OutOfRange": {
          "type": "boolean"
        },
        "x_RangeWarning": {
          "type": "boolean"
        },
        "x_Start": {
          "type": "boolean"
        },
        "x_Started": {
          "type": "boolean"
        },
        "x_stopActive": {
          "type": "boolean"
        },
        "x_stopInactive": {
          "type": "boolean"
        },
        "x_TcpConnected": {
          "type": "boolean"
        }
      }
    },
    "sSettings": {
      "type": "object",
      "properties": {
        "i_EaseBtnSpeed": {
          "type": "integer"
        },
        "i_EaseMaxSpeed": {
          "type": "integer"
        },
        "i_LineTensionDelay": {
          "type": "integer"
        },
        "i_MaxPosition": {
          "type": "integer"
        },
        "i_MinPosition": {
          "type": "integer"
        },
        "i_PullBtnSpeed": {
          "type": "integer"
        },
        "i_PullMaxSpeed": {
          "type": "integer"
        }
      }
    },
    "st_AnchorWinches": {
      "type": "object",
      "properties": {
        "x_Enabled": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        }
      }
    },
    "st_BoardingEquipment": {
      "type": "object",
      "properties": {
        "x_Enabled": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        }
      }
    },
    "st_cylinder": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "st_DeckWinches": {
      "type": "object",
      "properties": {
        "x_Enabled": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        }
      }
    },
    "st_encoder": {
      "type": "object",
      "properties": {
        "i_CylinderLength": {
          "type": "integer"
        },
        "i_MaxPosition": {
          "type": "integer"
        },
        "i_MinPosition": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_Position_permille": {
          "type": "integer"
        },
        "i_Speed": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        },
        "x_MinLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_F0404LockCylinder": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "st_load": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_LoadAt4rmA": {
          "type": "integer"
        },
        "i_LoadChangePermA": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "r_RawSensor": {
          "type": "number"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_Load": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_loadBottom": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_LoadAt4rmA": {
          "type": "integer"
        },
        "i_LoadChangePermA": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "r_RawSensor": {
          "type": "number"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_loadPs": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_loadRod": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_LoadAt4rmA": {
          "type": "integer"
        },
        "i_LoadChangePermA": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "r_RawSensor": {
          "type": "number"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_loadSb": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_MainEnable": {
      "type": "object",
      "properties": {
        "x_Enabled": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        }
      }
    },
    "st_position": {
      "type": "object",
      "properties": {
        "i_CylinderLength": {
          "type": "integer"
        },
        "i_MaxPosition": {
          "type": "integer"
        },
        "i_MinPosition": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_Position_permille": {
          "type": "integer"
        },
        "i_PositionChangemA": {
          "type": "integer"
        },
        "i_PositionStart": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        },
        "x_MinLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_positionPs": {
      "type": "object",
      "properties": {
        "i_CylinderLength": {
          "type": "integer"
        },
        "i_MaxPosition": {
          "type": "integer"
        },
        "i_MinPosition": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_Position_permille": {
          "type": "integer"
        },
        "i_Speed": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        },
        "x_MinLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_positionSb": {
      "type": "object",
      "properties": {
        "i_CylinderLength": {
          "type": "integer"
        },
        "i_MaxPosition": {
          "type": "integer"
        },
        "i_MinPosition": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_Position_permille": {
          "type": "integer"
        },
        "i_Speed": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        },
        "x_MinLimitReached": {
          "type": "boolean"
        }
      }
    },
    "st_powerEnable": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "st_SailFunction": {
      "type": "object",
      "properties": {
        "x_Enabled": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        }
      }
    },
    "st_settings": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_speedDownSetting": {
          "type": "integer"
        },
        "i_speedUpSetting": {
          "type": "integer"
        },
        "ist_LoadBottom/i_LoadAt4rmA": {
          "type": "integer"
        },
        "ist_LoadBottom/i_LoadChangePermA": {
          "type": "integer"
        },
        "ist_LoadBottom/i_MaxLoad": {
          "type": "integer"
        },
        "ist_LoadRod/i_LoadAt4rmA": {
          "type": "integer"
        },
        "ist_LoadRod/i_LoadChangePermA": {
          "type": "integer"
        },
        "ist_LoadRod/i_MaxLoad": {
          "type": "integer"
        },
        "ist_SnsrKeelPos1/i_MaxPosition": {
          "type": "integer"
        },
        "ist_SnsrKeelPos1/i_MinPosition": {
          "type": "integer"
        },
        "ist_SnsrKeelPos1/i_PositionChangemA": {
          "type": "integer"
        },
        "ist_SnsrKeelPos1/i_PositionStart": {
          "type": "integer"
        },
        "ist_SnsrKeelPos2/i_MaxPosition": {
          "type": "integer"
        },
        "ist_SnsrKeelPos2/i_MinPosition": {
          "type": "integer"
        },
        "ist_SnsrKeelPos2/i_PositionChangemA": {
          "type": "integer"
        },
        "ist_SnsrKeelPos2/i_PositionStart": {
          "type": "integer"
        }
      }
    },
    "sTchSpc": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "i_Temperature": {
          "type": "integer"
        },
        "iMaxTemperature": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_NoFeedbackAlarm": {
          "type": "boolean"
        },
        "x_NoFlowAlarm": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_TempAlarm": {
          "type": "boolean"
        }
      }
    },
    "StormSailFurlerLoad": {
      "type": "object",
      "properties": {
        "i_Load": {
          "type": "integer"
        },
        "i_MaxLoadSetting": {
          "type": "integer"
        },
        "x_Failure": {
          "type": "boolean"
        },
        "x_MaxLimitReached": {
          "type": "boolean"
        }
      }
    }
  },
  "topics": {
    "sail-system/cooling-pumps": {
      "type": "object",
      "properties": {
        "iDelayTime": {
          "type": "integer"
        },
        "sFrpk": {
          "$ref": "#/$defs/sFrpk"
        },
        "sHlyrdpt": {
          "$ref": "#/$defs/sHlyrdpt"
        },
        "sLzrtt": {
          "$ref": "#/$defs/sLzrtt"
        },
        "sTchSpc": {
          "$ref": "#/$defs/sTchSpc"
        }
      }
    },
    "sail-system/e-stop": {
      "type": "object",
      "properties": {
        "ix_0000_BtnHydrEnblHlmPs": {
          "type": "boolean"
        },
        "ix_0000_BtnHydrStopHlmPs": {
          "type": "boolean"
        },
        "ix_0000_BtnHydrStopHlmSb": {
          "type": "boolean"
        },
        "ix_0000_BtnHydrStopHlyrdPt": {
          "type": "boolean"
        },
        "ix_0000_BtnHydrStopMnMst": {
          "type": "boolean"
        },
        "ix_0000_BtnHydrStopMzznMst": {
          "type": "boolean"
        },
        "ix_0000_BtnHydrStopRcCckpt": {
          "type": "boolean"
        },
        "ix_0000_BtnHydrStopSlStrgLckr": {
          "type": "boolean"
        },
        "ix_0000_BtnHydrStopTechRm": {
          "type": "boolean"
        },
        "ix_0000_EStopRelay": {
          "type": "boolean"
        },
        "ix_0000_HydrFireStop": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f001-filter-pump": {
      "type": "object",
      "properties": {
        "i_OffDelayTime": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "st_powerEnable": {
          "$ref": "#/$defs/st_powerEnable"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_ExtSetModeAuto": {
          "type": "boolean"
        },
        "x_ExtSetModeOff": {
          "type": "boolean"
        },
        "x_ExtSetModeOn": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_ModeAuto": {
          "type": "boolean"
        },
        "x_ModeOff": {
          "type": "boolean"
        },
        "x_ModeOn": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SetModeAuto": {
          "type": "boolean"
        },
        "x_SetModeOff": {
          "type": "boolean"
        },
        "x_SetModeOn": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0101-blade-cunningham": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_positionPs": {
          "$ref": "#/$defs/st_positionPs"
        },
        "st_positionSb": {
          "$ref": "#/$defs/st_positionSb"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0102-code-sail-tack": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_positionPs": {
          "$ref": "#/$defs/st_positionPs"
        },
        "st_positionSb": {
          "$ref": "#/$defs/st_positionSb"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0103-blade-adjuster": {
      "type": "object",
      "properties": {
        "i_ActualLoad": {
          "type": "integer"
        },
        "i_ActualLoad2": {
          "type": "integer"
        },
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_LoadcellCalibration": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "r_ActualPressure": {
          "type": "number"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0104-staysail-stay-adjuster": {
      "type": "object",
      "properties": {
        "i_ActualLoad": {
          "type": "integer"
        },
        "i_ActualLoad2": {
          "type": "integer"
        },
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_LoadcellCalibration": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "r_ActualPressure": {
          "type": "number"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0201-main-outhaul": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0202-main-vang": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_load": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ii_EPrssrRlfAB_Current": {
          "type": "integer"
        },
        "oi_EPrssrRlfAB_Cmd": {
          "type": "integer"
        },
        "ox_CVangPark": {
          "type": "boolean"
        },
        "ox_DVangFloat": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_loadBottom": {
          "$ref": "#/$defs/st_loadBottom"
        },
        "st_loadRod": {
          "$ref": "#/$defs/st_loadRod"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        },
        "xEnableFloat": {
          "type": "boolean"
        },
        "xLocalEase": {
          "type": "boolean"
        },
        "xLocalPull": {
          "type": "boolean"
        },
        "xRcEase": {
          "type": "boolean"
        },
        "xRcPull": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0203-main-checkstay-deflector": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_Load": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_loadPs": {
          "$ref": "#/$defs/st_loadPs"
        },
        "st_loadSb": {
          "$ref": "#/$defs/st_loadSb"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0204-main-boom-preventer": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_cylinder": {
          "$ref": "#/$defs/st_cylinder"
        },
        "st_encoder": {
          "$ref": "#/$defs/st_encoder"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_loadBottom": {
          "$ref": "#/$defs/st_loadBottom"
        },
        "st_loadRod": {
          "$ref": "#/$defs/st_loadRod"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        },
        "xCvlve": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0205-main-cunningham": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        },
        "xCvlve": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0206-blade-tweaker-ps": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0207-blade-tweaker-sb": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0301-keel-lift-cylinders": {
      "type": "object",
      "properties": {
        "i_keelPosition": {
          "type": "integer"
        },
        "i_liftSeq": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_KeelLiftA_Current": {
          "type": "number"
        },
        "ir_KeelLiftB_Current": {
          "type": "number"
        },
        "ist_LoadBottom": {
          "$ref": "#/$defs/ist_LoadBottom"
        },
        "ist_LoadRod": {
          "$ref": "#/$defs/ist_LoadRod"
        },
        "ist_SnsrKeelPos1": {
          "$ref": "#/$defs/ist_SnsrKeelPos1"
        },
        "ist_SnsrKeelPos2": {
          "$ref": "#/$defs/ist_SnsrKeelPos2"
        },
        "ix_BtnExtDown": {
          "type": "boolean"
        },
        "ix_BtnExtUp": {
          "type": "boolean"
        },
        "ix_BtnPsDown": {
          "type": "boolean"
        },
        "ix_BtnPsUp": {
          "type": "boolean"
        },
        "ix_BtnSbDown": {
          "type": "boolean"
        },
        "ix_BtnSbUp": {
          "type": "boolean"
        },
        "ix_EnergyRecoveryMode": {
          "type": "boolean"
        },
        "ix_Locked": {
          "type": "boolean"
        },
        "ix_PosDown": {
          "type": "boolean"
        },
        "ix_PosUp": {
          "type": "boolean"
        },
        "ix_SnsrHtchOpen": {
          "type": "boolean"
        },
        "ix_SnsrKeelup100": {
          "type": "boolean"
        },
        "ix_SnsrKeelup80": {
          "type": "boolean"
        },
        "ix_unlocked": {
          "type": "boolean"
        },
        "oi_KeelLiftA": {
          "type": "integer"
        },
        "oi_KeelLiftB": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_KeelLiftC": {
          "type": "boolean"
        },
        "ox_KeelLiftD": {
          "type": "boolean"
        },
        "r_keelPosition": {
          "type": "number"
        },
        "st_settings": {
          "$ref": "#/$defs/st_settings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_hatchNotOpen": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_lockTimeout": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_notLocked": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_postionDeviation": {
          "type": "boolean"
        },
        "x_postionFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_timeoutDownSequence": {
          "type": "boolean"
        },
        "x_timeoutUpSequence": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0302-keel-lock-cylinders": {
      "type": "object",
      "properties": {
        "i_keelPosition": {
          "type": "integer"
        },
        "i_liftSeq": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_KeelLiftA_Current": {
          "type": "number"
        },
        "ir_KeelLiftB_Current": {
          "type": "number"
        },
        "ist_LoadBottom": {
          "$ref": "#/$defs/ist_LoadBottom"
        },
        "ist_LoadRod": {
          "$ref": "#/$defs/ist_LoadRod"
        },
        "ist_SnsrKeelPos1": {
          "$ref": "#/$defs/ist_SnsrKeelPos1"
        },
        "ist_SnsrKeelPos2": {
          "$ref": "#/$defs/ist_SnsrKeelPos2"
        },
        "ix_BtnExtDown": {
          "type": "boolean"
        },
        "ix_BtnExtUp": {
          "type": "boolean"
        },
        "ix_BtnPsDown": {
          "type": "boolean"
        },
        "ix_BtnPsUp": {
          "type": "boolean"
        },
        "ix_BtnSbDown": {
          "type": "boolean"
        },
        "ix_BtnSbUp": {
          "type": "boolean"
        },
        "ix_EnergyRecoveryMode": {
          "type": "boolean"
        },
        "ix_Locked": {
          "type": "boolean"
        },
        "ix_PosDown": {
          "type": "boolean"
        },
        "ix_PosUp": {
          "type": "boolean"
        },
        "ix_SnsrHtchOpen": {
          "type": "boolean"
        },
        "ix_SnsrKeelup100": {
          "type": "boolean"
        },
        "ix_SnsrKeelup80": {
          "type": "boolean"
        },
        "ix_unlocked": {
          "type": "boolean"
        },
        "oi_KeelLiftA": {
          "type": "integer"
        },
        "oi_KeelLiftB": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_KeelLiftC": {
          "type": "boolean"
        },
        "ox_KeelLiftD": {
          "type": "boolean"
        },
        "r_keelPosition": {
          "type": "number"
        },
        "st_settings": {
          "$ref": "#/$defs/st_settings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_hatchNotOpen": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_lockTimeout": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_notLocked": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_postionDeviation": {
          "type": "boolean"
        },
        "x_postionFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_timeoutDownSequence": {
          "type": "boolean"
        },
        "x_timeoutUpSequence": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0303-keel-spare": {
      "type": "object",
      "properties": {
        "i_keelPosition": {
          "type": "integer"
        },
        "i_liftSeq": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_KeelLiftA_Current": {
          "type": "number"
        },
        "ir_KeelLiftB_Current": {
          "type": "number"
        },
        "ist_LoadBottom": {
          "$ref": "#/$defs/ist_LoadBottom"
        },
        "ist_LoadRod": {
          "$ref": "#/$defs/ist_LoadRod"
        },
        "ist_SnsrKeelPos1": {
          "$ref": "#/$defs/ist_SnsrKeelPos1"
        },
        "ist_SnsrKeelPos2": {
          "$ref": "#/$defs/ist_SnsrKeelPos2"
        },
        "ix_BtnExtDown": {
          "type": "boolean"
        },
        "ix_BtnExtUp": {
          "type": "boolean"
        },
        "ix_BtnPsDown": {
          "type": "boolean"
        },
        "ix_BtnPsUp": {
          "type": "boolean"
        },
        "ix_BtnSbDown": {
          "type": "boolean"
        },
        "ix_BtnSbUp": {
          "type": "boolean"
        },
        "ix_EnergyRecoveryMode": {
          "type": "boolean"
        },
        "ix_Locked": {
          "type": "boolean"
        },
        "ix_PosDown": {
          "type": "boolean"
        },
        "ix_PosUp": {
          "type": "boolean"
        },
        "ix_SnsrHtchOpen": {
          "type": "boolean"
        },
        "ix_SnsrKeelup100": {
          "type": "boolean"
        },
        "ix_SnsrKeelup80": {
          "type": "boolean"
        },
        "ix_unlocked": {
          "type": "boolean"
        },
        "oi_KeelLiftA": {
          "type": "integer"
        },
        "oi_KeelLiftB": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_KeelLiftC": {
          "type": "boolean"
        },
        "ox_KeelLiftD": {
          "type": "boolean"
        },
        "r_keelPosition": {
          "type": "number"
        },
        "st_settings": {
          "$ref": "#/$defs/st_settings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_hatchNotOpen": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_lockTimeout": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_notLocked": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_postionDeviation": {
          "type": "boolean"
        },
        "x_postionFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_timeoutDownSequence": {
          "type": "boolean"
        },
        "x_timeoutUpSequence": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0401-mizzen-headsail-furler": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "iFeedForwardPressure": {
          "type": "integer"
        },
        "iFurlSpeedSetting": {
          "type": "integer"
        },
        "ii_FrlrA_Current": {
          "type": "integer"
        },
        "ii_FrlrB_Current": {
          "type": "integer"
        },
        "iUnfurlSpeedSetting": {
          "type": "integer"
        },
        "ix_BtnFrl": {
          "type": "boolean"
        },
        "ix_BtnUnfrl": {
          "type": "boolean"
        },
        "ix_RcFurl": {
          "type": "boolean"
        },
        "ix_RcUnfurl": {
          "type": "boolean"
        },
        "oi_FrlrA": {
          "type": "integer"
        },
        "oi_FrlrB": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0402-mizzen-headsail-tack-adjuster": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0403-crew-boarding-platform-ps": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_SnsrLock1": {
          "type": "boolean"
        },
        "ix_SnsrLock2": {
          "type": "boolean"
        },
        "ix_SnsrUnlock1": {
          "type": "boolean"
        },
        "ix_SnsrUnlock2": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "st_F0404LockCylinder": {
          "$ref": "#/$defs/st_F0404LockCylinder"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CloseButton": {
          "type": "boolean"
        },
        "x_CloseExt": {
          "type": "boolean"
        },
        "x_CloseTimeout": {
          "type": "boolean"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Locked": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OpenButton": {
          "type": "boolean"
        },
        "x_Opened": {
          "type": "boolean"
        },
        "x_OpenExt": {
          "type": "boolean"
        },
        "x_OpenTimeout": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensorFailure": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0405-oil-supply-guest-boarding-system-sb": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_HtchClsdLckd": {
          "type": "boolean"
        },
        "ix_OilRqst": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_OilsplyB": {
          "type": "boolean"
        },
        "ox_SystmEnbl": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0501-mizzen-outhaul": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0502-mizzen-vang": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_load": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ii_EPrssrRlfAB_Current": {
          "type": "integer"
        },
        "oi_EPrssrRlfAB_Cmd": {
          "type": "integer"
        },
        "ox_CVangPark": {
          "type": "boolean"
        },
        "ox_DVangFloat": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_loadBottom": {
          "$ref": "#/$defs/st_loadBottom"
        },
        "st_loadRod": {
          "$ref": "#/$defs/st_loadRod"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        },
        "xEnableFloat": {
          "type": "boolean"
        },
        "xLocalEase": {
          "type": "boolean"
        },
        "xLocalPull": {
          "type": "boolean"
        },
        "xRcEase": {
          "type": "boolean"
        },
        "xRcPull": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0503-mizzen-checkstay-deflector": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_Load": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_loadPs": {
          "$ref": "#/$defs/st_loadPs"
        },
        "st_loadSb": {
          "$ref": "#/$defs/st_loadSb"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0504-mizzen-cunningham": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        },
        "xCvlve": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0505-oil-supply-passarelle": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_HtchClsdLckd": {
          "type": "boolean"
        },
        "ix_OilRqst": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_OilsplyB": {
          "type": "boolean"
        },
        "ox_SystmEnbl": {
          "type": "boolean"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0506-mizzen-boom-preventer": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressureSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "st_cylinder": {
          "$ref": "#/$defs/st_cylinder"
        },
        "st_encoder": {
          "$ref": "#/$defs/st_encoder"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "st_loadBottom": {
          "$ref": "#/$defs/st_loadBottom"
        },
        "st_loadRod": {
          "$ref": "#/$defs/st_loadRod"
        },
        "st_position": {
          "$ref": "#/$defs/st_position"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_CylA": {
          "type": "boolean"
        },
        "x_CylB": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_In": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_Out": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SensrIn": {
          "type": "boolean"
        },
        "x_SensrOut": {
          "type": "boolean"
        },
        "xCvlve": {
          "type": "boolean"
        }
      }
    },
    "sail-system/f0600-tender-crane": {
      "type": "object",
      "properties": {
        "i_FeedForwardPressure": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_Estop": {
          "type": "boolean"
        },
        "ix_OilRqst": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_HpuRnnng": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "ox_PwrEnablePP": {
          "type": "boolean"
        },
        "ox_Sailsystm": {
          "type": "boolean"
        },
        "ox_SystmEnbl": {
          "type": "boolean"
        },
        "rFlowDemand": {
          "type": "integer"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_UsePowerPack": {
          "type": "boolean"
        },
        "x_UseSailSystem": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe101-code-furler": {
      "type": "object",
      "properties": {
        "i_FurlSpeedSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "i_UnfurlSpeedSetting": {
          "type": "integer"
        },
        "ix_LocalFurl": {
          "type": "boolean"
        },
        "ix_LocalUnfurl": {
          "type": "boolean"
        },
        "ix_RcFurl": {
          "type": "boolean"
        },
        "ix_RcUnfurl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_Furl": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "ox_Unfurl": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe102-blade-furler": {
      "type": "object",
      "properties": {
        "i_FurlSpeedSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "i_UnfurlSpeedSetting": {
          "type": "integer"
        },
        "ix_LocalFurl": {
          "type": "boolean"
        },
        "ix_LocalUnfurl": {
          "type": "boolean"
        },
        "ix_RcFurl": {
          "type": "boolean"
        },
        "ix_RcUnfurl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_Furl": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "ox_Unfurl": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe103-staysail-furler": {
      "type": "object",
      "properties": {
        "i_FurlSpeedSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "i_UnfurlSpeedSetting": {
          "type": "integer"
        },
        "ix_LocalFurl": {
          "type": "boolean"
        },
        "ix_LocalUnfurl": {
          "type": "boolean"
        },
        "ix_RcFurl": {
          "type": "boolean"
        },
        "ix_RcUnfurl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_Furl": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "ox_Unfurl": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe104-bow-deck-winch-ps": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe105-bow-deck-winch-sb": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe106-anchor-windlass-ps": {
      "type": "object",
      "properties": {
        "i_ChainLength": {
          "type": "integer"
        },
        "i_HighspeedDelay": {
          "type": "integer"
        },
        "i_HighSpeedInSetting": {
          "type": "integer"
        },
        "i_HighSpeedOutSetting": {
          "type": "integer"
        },
        "i_LowSpeedInSetting": {
          "type": "integer"
        },
        "i_LowSpeedOutSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_BtnInLoc": {
          "type": "boolean"
        },
        "ix_BtnOutLoc": {
          "type": "boolean"
        },
        "ix_CCPulse": {
          "type": "boolean"
        },
        "ix_RcInHigh": {
          "type": "boolean"
        },
        "ix_RcInLow": {
          "type": "boolean"
        },
        "ix_RcOutHigh": {
          "type": "boolean"
        },
        "ix_RcOutLow": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_Brk": {
          "type": "boolean"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_HighSpeed": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_ResetChainLength": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe107-anchor-windlass-sb": {
      "type": "object",
      "properties": {
        "i_ChainLength": {
          "type": "integer"
        },
        "i_HighspeedDelay": {
          "type": "integer"
        },
        "i_HighSpeedInSetting": {
          "type": "integer"
        },
        "i_HighSpeedOutSetting": {
          "type": "integer"
        },
        "i_LowSpeedInSetting": {
          "type": "integer"
        },
        "i_LowSpeedOutSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_BtnInLoc": {
          "type": "boolean"
        },
        "ix_BtnOutLoc": {
          "type": "boolean"
        },
        "ix_CCPulse": {
          "type": "boolean"
        },
        "ix_RcInHigh": {
          "type": "boolean"
        },
        "ix_RcInLow": {
          "type": "boolean"
        },
        "ix_RcOutHigh": {
          "type": "boolean"
        },
        "ix_RcOutLow": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_Brk": {
          "type": "boolean"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_HighSpeed": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_ResetChainLength": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe108-sail-drum": {
      "type": "object",
      "properties": {
        "i_FurlSpeedSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "i_UnfurlSpeedSetting": {
          "type": "integer"
        },
        "ir_RcSetpoint": {
          "type": "number"
        },
        "ix_LocalFurl": {
          "type": "boolean"
        },
        "ix_LocalUnfurl": {
          "type": "boolean"
        },
        "ix_RcOoc": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_WrkSwtch": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "ox_Furl": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "ox_Unfurl": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe201-blade-sheet-captive-winch-ps": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe202-blade-sheet-ps-feeder": {
      "type": "object",
      "properties": {
        "i_MaxSpeedStp": {
          "type": "integer"
        },
        "i_MaxTorqueStp": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "xSpeedDeviationAlarm": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe203-staysail-sheet-captive-winch-ps": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe204-staysail-sheet-ps-feeder": {
      "type": "object",
      "properties": {
        "i_MaxSpeedStp": {
          "type": "integer"
        },
        "i_MaxTorqueStp": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "xSpeedDeviationAlarm": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe205-main-sheet-captive-winch": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "st_Load": {
          "$ref": "#/$defs/st_Load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe206-main-sheet-feeder": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "rEaseTorqueSetting": {
          "type": "number"
        },
        "rPullTorqueSetting": {
          "type": "number"
        },
        "sDriveA": {
          "$ref": "#/$defs/sDriveA"
        },
        "sDriveB": {
          "$ref": "#/$defs/sDriveB"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "wActiveFault": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "xDriveNotRunningAlarm": {
          "type": "boolean"
        },
        "xEase": {
          "type": "boolean"
        },
        "xPull": {
          "type": "boolean"
        },
        "xRunningCCW": {
          "type": "boolean"
        },
        "xRunningCW": {
          "type": "boolean"
        },
        "xSpeedDeviationAlarm": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe207-main-halyard-captive-winch": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_BtnEase": {
          "type": "boolean"
        },
        "ix_BtnPull": {
          "type": "boolean"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sLoad": {
          "$ref": "#/$defs/sLoad"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe208-crows-nest-captive": {
      "type": "object",
      "properties": {
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_BtnDwn": {
          "type": "boolean"
        },
        "ix_BtnUp": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLti": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "st_settings": {
          "$ref": "#/$defs/st_settings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe209-main-mast-deck-winch-ps-fwd": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe210-main-mast-deck-winch-ps-aft": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe211-main-runner-retriever-captive-winch-ps": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe212-primary-deck-winch-ps": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp1Bw": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_Btn3": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sDriveBw": {
          "$ref": "#/$defs/sDriveBw"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe301-blade-sheet-captive-winch-sb": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe302-blade-sheet-sb-feeder": {
      "type": "object",
      "properties": {
        "i_MaxSpeedStp": {
          "type": "integer"
        },
        "i_MaxTorqueStp": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "xSpeedDeviationAlarm": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe303-staysail-sheet-captive-winch-sb": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe304-staysail-sheet-sb-feeder": {
      "type": "object",
      "properties": {
        "i_MaxSpeedStp": {
          "type": "integer"
        },
        "i_MaxTorqueStp": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "xSpeedDeviationAlarm": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe305-main-mast-deck-winch-sb-fwd": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe306-main-mast-deck-winch-sb-aft": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe307-main-runner-retriever-captive-winch-sb": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe308-primary-deck-winch-sb": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp1Bw": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_Btn3": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sDriveBw": {
          "$ref": "#/$defs/sDriveBw"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe401-main-runner-captive-winch-ps": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_BtnEase": {
          "type": "boolean"
        },
        "ix_BtnPull": {
          "type": "boolean"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "st_Load": {
          "$ref": "#/$defs/st_Load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe402-mizzen-runner-captive-winch-ps": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_BtnEase": {
          "type": "boolean"
        },
        "ix_BtnPull": {
          "type": "boolean"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "st_Load": {
          "$ref": "#/$defs/st_Load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe403-mizzen-runner-retriever-captive-winch-ps": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe404-mizzen-halyard-captive-winch": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_BtnEase": {
          "type": "boolean"
        },
        "ix_BtnPull": {
          "type": "boolean"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sLoad": {
          "$ref": "#/$defs/sLoad"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe405-main-sheet-traveller-winch": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_BtnEase": {
          "type": "boolean"
        },
        "ix_BtnPull": {
          "type": "boolean"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sLoad": {
          "$ref": "#/$defs/sLoad"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe406-popup-capstan-ps": {
      "type": "object",
      "properties": {
        "i_EaseSpeedSetting": {
          "type": "integer"
        },
        "i_PullSpeedSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_BtnEase": {
          "type": "boolean"
        },
        "ix_BtnPull": {
          "type": "boolean"
        },
        "ix_LmtdSpdSnsr": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe407-mizzen-mast-deck-winch-ps": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe408-aft-deck-deck-winch-ps": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe501-main-runner-captive-winch-sb": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_BtnEase": {
          "type": "boolean"
        },
        "ix_BtnPull": {
          "type": "boolean"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "st_Load": {
          "$ref": "#/$defs/st_Load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe502-mizzen-runner-captive-winch-sb": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_BtnEase": {
          "type": "boolean"
        },
        "ix_BtnPull": {
          "type": "boolean"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "st_Load": {
          "$ref": "#/$defs/st_Load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe503-mizzen-runner-retriever-captive-winch-sb": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe504-mizzen-sheet-captive-winch": {
      "type": "object",
      "properties": {
        "i_ActualLineLength": {
          "type": "integer"
        },
        "i_Position_mm": {
          "type": "integer"
        },
        "i_PositionPermille": {
          "type": "integer"
        },
        "i_SetActualLineLength": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ir_setpoint": {
          "type": "number"
        },
        "ir_SnsrPos": {
          "type": "number"
        },
        "ix_MnlCtrl": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrDti": {
          "type": "boolean"
        },
        "ix_SnsrIn": {
          "type": "boolean"
        },
        "ix_SnsrLine": {
          "type": "boolean"
        },
        "ix_SnsrOut": {
          "type": "boolean"
        },
        "or_Spd": {
          "type": "number"
        },
        "or_Trq": {
          "type": "number"
        },
        "ox_Ease": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_Pull": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "sSettings": {
          "$ref": "#/$defs/sSettings"
        },
        "st_Load": {
          "$ref": "#/$defs/st_Load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ActivateLineLengthSetting": {
          "type": "boolean"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_OoC": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SnsrDtiAlarm": {
          "type": "boolean"
        },
        "xInnerLimit": {
          "type": "boolean"
        },
        "xOuterLimit": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe505-mizzen-sheet-feeder": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "rEaseTorqueSetting": {
          "type": "number"
        },
        "rPullTorqueSetting": {
          "type": "number"
        },
        "sDriveA": {
          "$ref": "#/$defs/sDriveA"
        },
        "sDriveB": {
          "$ref": "#/$defs/sDriveB"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "wActiveFault": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "xDriveNotRunningAlarm": {
          "type": "boolean"
        },
        "xEase": {
          "type": "boolean"
        },
        "xPull": {
          "type": "boolean"
        },
        "xRunningCCW": {
          "type": "boolean"
        },
        "xRunningCW": {
          "type": "boolean"
        },
        "xSpeedDeviationAlarm": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe506-popup-capstan-sb": {
      "type": "object",
      "properties": {
        "i_EaseSpeedSetting": {
          "type": "integer"
        },
        "i_PullSpeedSetting": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_BtnEase": {
          "type": "boolean"
        },
        "ix_BtnPull": {
          "type": "boolean"
        },
        "ix_LmtdSpdSnsr": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe507-mizzen-mast-deck-winch-sb": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fe508-aft-deck-deck-winch-sb": {
      "type": "object",
      "properties": {
        "i_State": {
          "type": "integer"
        },
        "io_SpdStp1": {
          "type": "integer"
        },
        "io_SpdStp2": {
          "type": "integer"
        },
        "io_SpdStp3": {
          "type": "integer"
        },
        "ix_Btn1": {
          "type": "boolean"
        },
        "ix_Btn2": {
          "type": "boolean"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "ix_SnsrSpd": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_LoadAlarm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "st_load": {
          "$ref": "#/$defs/st_load"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fpp1-powerpack1": {
      "type": "object",
      "properties": {
        "i_Flow": {
          "type": "integer"
        },
        "i_LoadSenseOffset": {
          "type": "integer"
        },
        "i_OffDelaySettings": {
          "type": "integer"
        },
        "i_Pressure": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "or_SpdStp": {
          "type": "number"
        },
        "or_TrqStp": {
          "type": "number"
        },
        "ox_FcuEnbl": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "tOnDelay": {
          "type": "string",
          "format": "duration"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_ExtSetModeAuto": {
          "type": "boolean"
        },
        "x_ExtSetModeOff": {
          "type": "boolean"
        },
        "x_ExtSetModeOn": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_ModeAuto": {
          "type": "boolean"
        },
        "x_ModeOff": {
          "type": "boolean"
        },
        "x_ModeOn": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SetModeAuto": {
          "type": "boolean"
        },
        "x_SetModeOff": {
          "type": "boolean"
        },
        "x_SetModeOn": {
          "type": "boolean"
        }
      }
    },
    "sail-system/fpp2-powerpack2": {
      "type": "object",
      "properties": {
        "i_Flow": {
          "type": "integer"
        },
        "i_LoadSenseOffset": {
          "type": "integer"
        },
        "i_OffDelaySettings": {
          "type": "integer"
        },
        "i_Pressure": {
          "type": "integer"
        },
        "i_State": {
          "type": "integer"
        },
        "ix_RelayStatus": {
          "type": "boolean"
        },
        "or_SpdStp": {
          "type": "number"
        },
        "or_TrqStp": {
          "type": "number"
        },
        "ox_FcuEnbl": {
          "type": "boolean"
        },
        "ox_GnrlAlrm": {
          "type": "boolean"
        },
        "ox_PwrEnable": {
          "type": "boolean"
        },
        "sDrive": {
          "$ref": "#/$defs/sDrive"
        },
        "tOnDelay": {
          "type": "string",
          "format": "duration"
        },
        "ui_RunningHours": {
          "type": "integer"
        },
        "x_ExtOnOff": {
          "type": "boolean"
        },
        "x_ExtSetModeAuto": {
          "type": "boolean"
        },
        "x_ExtSetModeOff": {
          "type": "boolean"
        },
        "x_ExtSetModeOn": {
          "type": "boolean"
        },
        "x_FunctionEnabled": {
          "type": "boolean"
        },
        "x_GroupEnabled": {
          "type": "boolean"
        },
        "x_LocalControl": {
          "type": "boolean"
        },
        "x_Maintenance": {
          "type": "boolean"
        },
        "x_ModeAuto": {
          "type": "boolean"
        },
        "x_ModeOff": {
          "type": "boolean"
        },
        "x_ModeOn": {
          "type": "boolean"
        },
        "x_OnOff": {
          "type": "boolean"
        },
        "x_PowerFailure": {
          "type": "boolean"
        },
        "x_RcControl": {
          "type": "boolean"
        },
        "x_Running": {
          "type": "boolean"
        },
        "x_SetModeAuto": {
          "type": "boolean"
        },
        "x_SetModeOff": {
          "type": "boolean"
        },
        "x_SetModeOn": {
          "type": "boolean"
        }
      }
    },
    "sail-system/group-releases": {
      "type": "object",
      "properties": {
        "st_AnchorWinches": {
          "$ref": "#/$defs/st_AnchorWinches"
        },
        "st_BoardingEquipment": {
          "$ref": "#/$defs/st_BoardingEquipment"
        },
        "st_DeckWinches": {
          "$ref": "#/$defs/st_DeckWinches"
        },
        "st_MainEnable": {
          "$ref": "#/$defs/st_MainEnable"
        },
        "st_SailFunction": {
          "$ref": "#/$defs/st_SailFunction"
        }
      }
    },
    "sail-system/hydraulic-system": {
      "type": "object",
      "properties": {
        "i_OilTankLevel": {
          "type": "integer"
        },
        "i_OilTankTemperature": {
          "type": "integer"
        },
        "i_SnsrPrssrAftSystm": {
          "type": "integer"
        },
        "i_SnsrPrssrFwdSystm": {
          "type": "integer"
        },
        "i_SnsrPrssrRtr": {
          "type": "integer"
        },
        "i_SnsrPrssrVB01": {
          "type": "integer"
        },
        "i_SnsrPrssrVB02": {
          "type": "integer"
        },
        "i_SnsrPrssrVB03": {
          "type": "integer"
        },
        "i_SnsrPrssrVB04": {
          "type": "integer"
        },
        "i_SnsrPrssrVB05": {
          "type": "integer"
        },
        "i_SnsrPrssrVB06": {
          "type": "integer"
        },
        "ix_requestEcoMode": {
          "type": "boolean"
        },
        "ix_requestxPerformacnceMode": {
          "type": "boolean"
        },
        "ix_SnsrLwLwOilLevel": {
          "type": "boolean"
        },
        "ix_SnsrLwOilLevel": {
          "type": "boolean"
        },
        "ix_SnsrShtdwnOilLevel": {
          "type": "boolean"
        },
        "ix_SnsrSuctionVlv1Open": {
          "type": "boolean"
        },
        "ix_SnsrSuctionVlv2Open": {
          "type": "boolean"
        },
        "oi_LoadLimitAft_Cmd": {
          "type": "integer"
        },
        "oi_LoadLimitAft_Current": {
          "type": "integer"
        },
        "oi_LoadLimitFore_Cmd": {
          "type": "integer"
        },
        "oi_LoadLimitFore_Current": {
          "type": "integer"
        },
        "x_CombinedSystem": {
          "type": "boolean"
        },
        "x_EcoMode": {
          "type": "boolean"
        },
        "x_ExtEnablePulse": {
          "type": "boolean"
        },
        "x_KeelRegeneration": {
          "type": "boolean"
        },
        "x_LoadSensePressureControl": {
          "type": "boolean"
        },
        "x_noPumpAvailable": {
          "type": "boolean"
        },
        "x_oiltankLow": {
          "type": "boolean"
        },
        "x_oiltankLowLow": {
          "type": "boolean"
        },
        "x_oiltankTempHigh": {
          "type": "boolean"
        },
        "x_PerformacnceMode": {
          "type": "boolean"
        },
        "x_SnsrShtdwnOilLevel": {
          "type": "boolean"
        },
        "x_SplitSystem": {
          "type": "boolean"
        },
        "x_SystemEnabled": {
          "type": "boolean"
        },
        "x_VolumeControl": {
          "type": "boolean"
        }
      }
    },
    "sail-system/mast": {
      "type": "object",
      "properties": {
        "F0401_MzznHdFrlr": {
          "$ref": "#/$defs/F0401_MzznHdFrlr"
        },
        "FE207_MnHlyrd": {
          "$ref": "#/$defs/FE207_MnHlyrd"
        },
        "FE404_MzznHlyrd": {
          "$ref": "#/$defs/FE404_MzznHlyrd"
        },
        "ix_SnsrA2Lck": {
          "type": "boolean"
        },
        "ix_SnsrA2LckOvrhst": {
          "type": "boolean"
        },
        "ix_SnsrA3C0Lck": {
          "type": "boolean"
        },
        "ix_SnsrA3C0LckOvrhst": {
          "type": "boolean"
        },
        "ix_SnsrSrmJpLck": {
          "type": "boolean"
        },
        "ix_SnsrSrmJpLckOvrhst": {
          "type": "boolean"
        },
        "ix_SnsrStyslLck": {
          "type": "boolean"
        },
        "ix_SnsrStyslLckOvrhst": {
          "type": "boolean"
        },
        "StormSailFurlerLoad": {
          "$ref": "#/$defs/StormSailFurlerLoad"
        }
      }
    },
    "sail-system/remotes": {
      "type": "object",
      "properties": {
        "sHlmPs": {
          "$ref": "#/$defs/sHlmPs"
        },
        "sHlmSb": {
          "$ref": "#/$defs/sHlmSb"
        },
        "sRaceCp": {
          "$ref": "#/$defs/sRaceCp"
        },
        "sRcAnchr": {
          "$ref": "#/$defs/sRcAnchr"
        },
        "sRcCrwsNst": {
          "$ref": "#/$defs/sRcCrwsNst"
        },
        "sRcDrum": {
          "$ref": "#/$defs/sRcDrum"
        },
        "sRcHead": {
          "$ref": "#/$defs/sRcHead"
        },
        "sRcMain": {
          "$ref": "#/$defs/sRcMain"
        },
        "sRcMntnc": {
          "$ref": "#/$defs/sRcMntnc"
        },
        "sRcMzzn": {
          "$ref": "#/$defs/sRcMzzn"
        },
        "sRcSpare1": {
          "$ref": "#/$defs/sRcSpare1"
        },
        "sRcSpare2": {
          "$ref": "#/$defs/sRcSpare2"
        },
        "sRcSpare3": {
          "$ref": "#/$defs/sRcSpare3"
        }
      }
    },
    "sail-system/s-maintenance-function": {
      "type": "object",
      "properties": {}
    },
    "sail-system/system": {
      "type": "object",
      "properties": {
        "e_CanHdc02": {
          "type": "integer"
        },
        "e_CanHdc03": {
          "type": "integer"
        },
        "e_CanHdc04": {
          "type": "integer"
        },
        "e_CanHdc05": {
          "type": "integer"
        },
        "e_CanHdc06": {
          "type": "integer"
        },
        "e_CanMainMst": {
          "type": "integer"
        },
        "e_CanMzznMst": {
          "type": "integer"
        },
        "e_CanTech": {
          "type": "integer"
        },
        "EF": {
          "$ref": "#/$defs/EF"
        },
        "i_CanHdc02Load": {
          "type": "integer"
        },
        "i_CanHdc03Load": {
          "type": "integer"
        },
        "i_CanHdc04Load": {
          "type": "integer"
        },
        "i_CanHdc05Load": {
          "type": "integer"
        },
        "i_CanHdc06Load": {
          "type": "integer"
        },
        "i_CanMainMstLoad": {
          "type": "integer"
        },
        "i_CanMzznMstLoad": {
          "type": "integer"
        },
        "i_CanTechLoad": {
          "type": "integer"
        },
        "x_RioFpkConnected": {
          "type": "boolean"
        },
        "x_RioHlmPsConnected": {
          "type": "boolean"
        },
        "x_RioHlmSbConnected": {
          "type": "boolean"
        },
        "x_RioHypConnected": {
          "type": "boolean"
        },
        "x_RioKeelConnected": {
          "type": "boolean"
        },
        "x_RioLazConnected": {
          "type": "boolean"
        },
        "x_RioMstConnected": {
          "type": "boolean"
        }
      }
    },
    "sail-system/x-acknowledge-alarm": {
      "type": "object",
      "properties": {}
    }
  }
}
