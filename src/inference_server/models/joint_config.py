"""
Joint configuration and mapping utilities for RobotHub Inference Server.

This module handles joint data parsing and normalization between different
robot configurations and the standardized training data format.
"""

from typing import ClassVar

import numpy as np


class JointConfig:
    """Joint configuration and mapping utilities."""

    # Joint name mapping from AI server names to standard names
    AI_TO_STANDARD_NAMES: ClassVar = {
        "Rotation": "shoulder_pan",
        "Pitch": "shoulder_lift",
        "Elbow": "elbow_flex",
        "Wrist_Pitch": "wrist_flex",
        "Wrist_Roll": "wrist_roll",
        "Jaw": "gripper",
    }

    # Standard joint names in order
    STANDARD_JOINT_NAMES: ClassVar = [
        "shoulder_pan",
        "shoulder_lift",
        "elbow_flex",
        "wrist_flex",
        "wrist_roll",
        "gripper",
    ]

    # AI server joint names in order
    AI_JOINT_NAMES: ClassVar = [
        "Rotation",
        "Pitch",
        "Elbow",
        "Wrist_Pitch",
        "Wrist_Roll",
        "Jaw",
    ]

    # Normalization ranges for robot joints
    # Most joints: [-100, 100], Gripper: [0, 100]
    ROBOT_NORMALIZATION_RANGES: ClassVar = {
        "shoulder_pan": (-100, 100),
        "shoulder_lift": (-100, 100),
        "elbow_flex": (-100, 100),
        "wrist_flex": (-100, 100),
        "wrist_roll": (-100, 100),
        "gripper": (0, 100),
    }

    @classmethod
    def parse_joint_data(cls, joints_data, policy_type: str = "act") -> list[float]:
        """
        Parse joint data from Transport Server message into standard order.

        Args:
            joints_data: Joint data from Transport Server message
            policy_type: Type of policy (for logging purposes)

        Returns:
            List of 6 normalized joint values in standard order

        """
        # Handle different possible data formats
        joint_dict = joints_data.data if hasattr(joints_data, "data") else joints_data

        if not isinstance(joint_dict, dict):
            return [0.0] * 6

        # Extract joint values in standard order
        joint_values = []
        for standard_name in cls.STANDARD_JOINT_NAMES:
            value = 0.0  # Default value

            # Try standard name first
            if standard_name in joint_dict:
                value = float(joint_dict[standard_name])
            else:
                # Try AI name
                for ai_name, std_name in cls.AI_TO_STANDARD_NAMES.items():
                    if std_name == standard_name and ai_name in joint_dict:
                        value = float(joint_dict[ai_name])
                        break

            joint_values.append(value)

        return joint_values

    @classmethod
    def create_joint_commands(cls, action_values: np.ndarray | list) -> list[dict]:
        """
        Create joint command messages from action values.

        Args:
            action_values: Array of 6 joint values in standard order

        Returns:
            List of joint command dictionaries with AI server names

        """
        if len(action_values) != 6:
            msg = f"Expected 6 joint values, got {len(action_values)}"
            raise ValueError(msg)

        commands = []
        for i, ai_name in enumerate(cls.AI_JOINT_NAMES):
            commands.append({
                "name": ai_name,
                "value": float(action_values[i]),
                "index": i,
            })
        return commands

    @classmethod
    def validate_joint_values(cls, joint_values: np.ndarray) -> np.ndarray:
        """
        Validate and clamp joint values to their normalized limits.

        Args:
            joint_values: Array of joint values

        Returns:
            Clamped joint values

        """
        if len(joint_values) != 6:
            # Pad or truncate to 6 values
            padded = np.zeros(6, dtype=np.float32)
            n = min(len(joint_values), 6)
            padded[:n] = joint_values[:n]
            joint_values = padded

        # Clamp to normalized limits
        for i, standard_name in enumerate(cls.STANDARD_JOINT_NAMES):
            min_val, max_val = cls.ROBOT_NORMALIZATION_RANGES[standard_name]
            joint_values[i] = np.clip(joint_values[i], min_val, max_val)

        return joint_values
