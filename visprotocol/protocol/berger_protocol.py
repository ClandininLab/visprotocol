#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from visprotocol.protocol.clandinin_protocol import BaseProtocol


class FullFieldDCRamp(BaseProtocol):
    """Full field linear luminance ramp"""

    STIM_LENGTH = 30.0
    MAX_BRIGHTNESS = 1

    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters["center"])

        # current_intensity = self.selectParametersFromLists(
        #     self.protocol_parameters["intensity"],
        #     randomize_order=self.protocol_parameters["randomize_order"],
        # )

        color_traj = {
            "name": "tv_pairs",
            "tv_pairs": [(0, 0), (self.STIM_LENGTH, self.MAX_BRIGHTNESS)],
            "kind": "linear",
        }

        self.epoch_parameters = {
            "name": "MovingPatch",
            "width": self.protocol_parameters["width"],
            "height": self.protocol_parameters["height"],
            "sphere_radius": 1,
            "color": color_traj,
            "theta": adj_center[0],
            "phi": adj_center[1],
            "angle": 0,
        }
        # self.convenience_parameters = {"current_intensity": current_intensity}

    def getParameterDefaults(self):
        self.protocol_parameters = {
            "height": 120.0,
            "width": 120.0,
            "center": [0, 0],
            "intensity": [1.0, 0.0],
            "randomize_order": True,
        }

    def getRunParameterDefaults(self):
        self.run_parameters = {
            "protocol_ID": "FullFieldDCRamp",
            "num_epochs": 10,
            "pre_time": 5.0,
            "stim_time": self.STIM_LENGTH,
            "tail_time": 1.0,
            "idle_color": 0.5,
        }


class UniformFlash(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters["center"])

        current_intensity = self.selectParametersFromLists(
            self.protocol_parameters["intensity"],
            randomize_order=self.protocol_parameters["randomize_order"],
        )

        self.epoch_parameters = {
            "name": "MovingPatch",
            "width": self.protocol_parameters["width"],
            "height": self.protocol_parameters["height"],
            "sphere_radius": 1,
            "color": current_intensity,
            "theta": adj_center[0],
            "phi": adj_center[1],
            "angle": 0,
        }
        self.convenience_parameters = {"current_intensity": current_intensity}

    def getParameterDefaults(self):
        self.protocol_parameters = {
            "height": 120.0,
            "width": 120.0,
            "center": [0, 0],
            "intensity": [1.0, 0.0],
            "randomize_order": True,
        }

    def getRunParameterDefaults(self):
        self.run_parameters = {
            "protocol_ID": "UniformFlash",
            "num_epochs": 10,
            "pre_time": 1.0,
            "stim_time": 0.5,
            "tail_time": 1.0,
            "idle_color": 0.5,
        }


class LoomingSpot(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stim_time = self.run_parameters["stim_time"]
        start_size = self.protocol_parameters["start_size"]
        end_size = self.protocol_parameters["end_size"]

        # adjust center to screen center
        adj_center = self.adjustCenter(self.protocol_parameters["center"])

        rv_ratio = self.protocol_parameters["rv_ratio"]  # msec
        current_rv_ratio, current_intensity = self.selectParametersFromLists(
            (rv_ratio, self.protocol_parameters["intensity"]),
            randomize_order=self.protocol_parameters["randomize_order"],
        )

        current_rv_ratio = current_rv_ratio / 1e3  # msec -> sec
        r_traj = {
            "name": "Loom2",
            "rv_ratio": current_rv_ratio,
            "start_size": start_size,
            "end_size": end_size,
        }

        self.epoch_parameters = {
            "name": "MovingSpot",
            "radius": r_traj,
            "sphere_radius": 1,
            "color": current_intensity,
            "theta": adj_center[0],
            "phi": adj_center[1],
        }

        self.convenience_parameters = {
            "current_rv_ratio": current_rv_ratio,
            "current_intensity": current_intensity,
        }

    def getParameterDefaults(self):
        self.protocol_parameters = {
            "intensity": [0.0, 1.0],
            "center": [0, 0],
            "start_size": 2.5,
            "end_size": 80.0,
            "rv_ratio": [5.0, 10.0, 20.0, 40.0, 80.0],
            "randomize_order": True,
        }

    def getRunParameterDefaults(self):
        self.run_parameters = {
            "protocol_ID": "LoomingSpot",
            "num_epochs": 75,
            "pre_time": 0.5,
            "stim_time": 1.0,
            "tail_time": 1.0,
            "idle_color": 0.5,
        }


class FlickeringPatch(BaseProtocol):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        adj_center = self.adjustCenter(self.protocol_parameters["center"])

        current_temporal_frequency = self.selectParametersFromLists(
            self.protocol_parameters["temporal_frequency"],
            randomize_order=self.protocol_parameters["randomize_order"],
        )

        # make color trajectory
        color_traj = {
            "name": "Sinusoid"
            if self.protocol_parameters["sinusoidal"]
            else "SquareWave",
            "temporal_frequency": current_temporal_frequency,
            "amplitude": self.protocol_parameters["mean"]
            * self.protocol_parameters["contrast"],
            "offset": self.protocol_parameters["mean"],
        }

        self.epoch_parameters = {
            "name": "MovingPatch",
            "width": self.protocol_parameters["width"],
            "height": self.protocol_parameters["height"],
            "sphere_radius": 1,
            "color": color_traj,
            "theta": adj_center[0],
            "phi": adj_center[1],
            "angle": 0,
        }

        self.convenience_parameters = {
            "current_temporal_frequency": current_temporal_frequency
        }

    def getParameterDefaults(self):
        self.protocol_parameters = {
            "height": 10.0,
            "width": 10.0,
            "center": [0, 0],
            "contrast": 1.0,
            "mean": 0.5,
            "temporal_frequency": [0.5, 1.0, 2.0, 4.0, 8.0, 16.0],
            "sinusoidal": False,
            "randomize_order": True,
        }

    def getRunParameterDefaults(self):
        self.run_parameters = {
            "protocol_ID": "FlickeringPatch",
            "num_epochs": 30,
            "pre_time": 1.0,
            "stim_time": 4.0,
            "tail_time": 1.0,
            "idle_color": 0.5,
        }
