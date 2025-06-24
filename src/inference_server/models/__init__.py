#!/usr/bin/env python

# Copyright 2024 The LeRobot Team and contributors.
# Licensed under the Apache License, Version 2.0

"""
Inference Server Models Module.

This module provides various inference engines for different robotic policy types,
including ACT, Pi0, SmolVLA, and Diffusion Policy models.
"""

import logging

from .joint_config import JointConfig

logger = logging.getLogger(__name__)

# Import engines with optional dependencies
_available_engines = {}
_available_policies = []

# Try to import ACT (should always work)
try:
    from .act_inference import ACTInferenceEngine

    _available_engines["act"] = ACTInferenceEngine
    _available_policies.append("act")
except ImportError as e:
    logger.warning(f"ACT policy not available: {e}")

# Try to import Pi0 (optional)
try:
    from .pi0_inference import Pi0InferenceEngine

    _available_engines["pi0"] = Pi0InferenceEngine
    _available_policies.append("pi0")
except ImportError as e:
    logger.warning(f"Pi0 policy not available: {e}")

# Try to import Pi0Fast (optional)
try:
    from .pi0fast_inference import Pi0FastInferenceEngine

    _available_engines["pi0fast"] = Pi0FastInferenceEngine
    _available_policies.append("pi0fast")
except ImportError as e:
    logger.warning(f"Pi0Fast policy not available: {e}")

# Try to import SmolVLA (optional)
try:
    from .smolvla_inference import SmolVLAInferenceEngine

    _available_engines["smolvla"] = SmolVLAInferenceEngine
    _available_policies.append("smolvla")
except ImportError as e:
    logger.warning(f"SmolVLA policy not available: {e}")

# Try to import Diffusion (optional - known to have dependency issues)
try:
    from .diffusion_inference import DiffusionInferenceEngine

    _available_engines["diffusion"] = DiffusionInferenceEngine
    _available_policies.append("diffusion")
except ImportError as e:
    logger.warning(f"Diffusion policy not available: {e}")

# Export what's available
__all__ = [
    # Shared configuration
    "JointConfig",
    # Factory functions
    "get_inference_engine",
    "list_supported_policies",
]

# Add available engines to exports
for policy_type in _available_policies:
    if policy_type == "act":
        __all__.append("ACTInferenceEngine")
    elif policy_type == "pi0":
        __all__.append("Pi0InferenceEngine")
    elif policy_type == "pi0fast":
        __all__.append("Pi0FastInferenceEngine")
    elif policy_type == "smolvla":
        __all__.append("SmolVLAInferenceEngine")
    elif policy_type == "diffusion":
        __all__.append("DiffusionInferenceEngine")


def list_supported_policies() -> list[str]:
    """Return a list of supported policy types based on available dependencies."""
    return _available_policies.copy()


def get_inference_engine(policy_type: str, **kwargs):
    """
    Factory function to create an inference engine based on policy type.

    Args:
        policy_type: Type of policy (act, pi0, pi0fast, smolvla, diffusion)
        **kwargs: Arguments to pass to the inference engine constructor

    Returns:
        Appropriate inference engine instance

    Raises:
        ValueError: If policy type is not supported or not available

    """
    policy_type = policy_type.lower()

    if policy_type not in _available_engines:
        available = list_supported_policies()
        msg = f"Policy type '{policy_type}' is not available. Available policies: {available}"
        raise ValueError(msg)

    engine_class = _available_engines[policy_type]
    return engine_class(**kwargs)
