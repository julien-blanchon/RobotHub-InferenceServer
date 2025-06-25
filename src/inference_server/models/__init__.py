#!/usr/bin/env python

# Copyright 2024 The LeRobot Team and contributors.
# Licensed under the Apache License, Version 2.0

"""
RobotHub Inference Server - Model inference engines for various policy types.

This module provides unified inference engines for different policy architectures
including ACT, Pi0, SmolVLA, and Diffusion policies.
"""

import logging

from .act_inference import ACTInferenceEngine
from .base_inference import BaseInferenceEngine
from .diffusion_inference import DiffusionInferenceEngine
from .joint_config import JointConfig
from .pi0_inference import Pi0InferenceEngine
from .pi0fast_inference import Pi0FastInferenceEngine
from .smolvla_inference import SmolVLAInferenceEngine

logger = logging.getLogger(__name__)

# Core exports that are always available
__all__ = [
    "ACTInferenceEngine",
    "BaseInferenceEngine",
    "DiffusionInferenceEngine",
    "JointConfig",
    "Pi0FastInferenceEngine",
    "Pi0InferenceEngine",
    "SmolVLAInferenceEngine",
    "get_inference_engine",
]


POLICY_ENGINES = {
    "act": ACTInferenceEngine,
    "pi0": Pi0InferenceEngine,
    "pi0fast": Pi0FastInferenceEngine,
    "smolvla": SmolVLAInferenceEngine,
    "diffusion": DiffusionInferenceEngine,
}


def get_inference_engine(policy_type: str, **kwargs) -> BaseInferenceEngine:
    """
    Get an inference engine instance for the specified policy type.

    Args:
        policy_type: Type of policy ('act', 'pi0', 'pi0fast', 'smolvla', 'diffusion')
        **kwargs: Additional arguments passed to the engine constructor

    Returns:
        BaseInferenceEngine: Configured inference engine instance

    Raises:
        ValueError: If policy_type is not supported or not available

    """
    if policy_type not in POLICY_ENGINES:
        available = list(POLICY_ENGINES.keys())
        if not available:
            msg = "No policy engines are available. Check your LeRobot installation."
        else:
            msg = f"Unsupported policy type: {policy_type}. Available: {available}"
        raise ValueError(msg)

    engine_class = POLICY_ENGINES[policy_type]
    return engine_class(**kwargs)
