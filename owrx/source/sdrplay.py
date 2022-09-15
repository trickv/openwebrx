from owrx.source.soapy import SoapyConnectorSource, SoapyConnectorDeviceDescription
from owrx.form.input import Input, CheckboxInput, DropdownInput, NumberInput, DropdownEnum
from owrx.form.input.validator import RangeValidator
from owrx.form.input.device import BiasTeeInput
from typing import List


class SdrplaySource(SoapyConnectorSource):
    def getSoapySettingsMappings(self):
        mappings = super().getSoapySettingsMappings()
        mappings.update(
            {
                "bias_tee": "biasT_ctrl",
                "rf_notch": "rfnotch_ctrl",
                "dab_notch": "dabnotch_ctrl",
                "if_mode": "if_mode",
                "external_reference": "extref_ctrl",
                "gain_model": "gain_ctrl_model",
                "agc_setpoint": "agc_setpoint",
                "rfgain_sel": "rfgain_sel"
            }
        )
        return mappings

    def getDriver(self):
        return "sdrplay"


class IfModeOptions(DropdownEnum):
    IFMODE_ZERO_IF = "Zero-IF"
    IFMODE_450 = "450kHz"
    IFMODE_1620 = "1620kHz"
    IFMODE_2048 = "2048kHz"

    def __str__(self):
        return self.value


class GainModelOptions(DropdownEnum):
    GMODEL_LEGACY = "LEGACY"
    GMODEL_DB = "DB"
    GMODEL_RFATT = "RFATT"
    GMODEL_STEPS = "STEPS"

    def __str__(self):
        return self.value


class SdrplayDeviceDescription(SoapyConnectorDeviceDescription):
    def getName(self):
        return "SDRPlay device (RSP1, RSP2, RSPDuo, RSPDx)"

    def getGainStages(self):
        return ["RFGR", "IFGR"]

    def getInputs(self) -> List[Input]:
        return super().getInputs() + [
            BiasTeeInput(),
            CheckboxInput(
                "rf_notch",
                "Enable RF Notch Filter",
            ),
            CheckboxInput(
                "dab_notch",
                "Enable DAB Notch Filter",
            ),
            DropdownInput(
                "if_mode",
                "IF Mode",
                IfModeOptions,
            ),
            DropdownInput(
                "gain_model",
                "Gain Control Model",
                GainModelOptions,
            ),
            NumberInput(
                "agc_setpoint",
                "AGC Setpoint",
                append="dBFS",
                validator=RangeValidator(-60, 0),
            ),
            NumberInput(
                "rfgain_sel",
                "RF Gain Reduction",
                validator=RangeValidator(0, 32),
            ),
        ]

    def getDeviceOptionalKeys(self):
        return super().getDeviceOptionalKeys() + ["bias_tee", "rf_notch", "dab_notch", "if_mode", "gain_model", "agc_setpoint", "rfgain_sel"]

    def getProfileOptionalKeys(self):
        return super().getProfileOptionalKeys() + ["bias_tee", "rf_notch", "dab_notch", "if_mode", "gain_model", "agc_setpoint", "rfgain_sel"]
