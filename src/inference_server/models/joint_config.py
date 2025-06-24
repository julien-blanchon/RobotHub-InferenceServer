from typing import ClassVar

import numpy as np


class JointConfig:
    # Standard joint names used in LeRobot training data
    LEROBOT_JOINT_NAMES: ClassVar = [
        "shoulder_pan_joint",
        "shoulder_lift_joint",
        "elbow_joint",
        "wrist_1_joint",
        "wrist_2_joint",
        "wrist_3_joint",
    ]

    # Our custom joint names (more intuitive for users)
    CUSTOM_JOINT_NAMES: ClassVar = [
        "base_rotation",
        "shoulder_tilt",
        "elbow_bend",
        "wrist_rotate",
        "wrist_tilt",
        "wrist_twist",
    ]

    # Mapping from our custom names to LeRobot standard names
    CUSTOM_TO_LEROBOT_NAMES: ClassVar = {
        "base_rotation": "shoulder_pan_joint",
        "shoulder_tilt": "shoulder_lift_joint",
        "elbow_bend": "elbow_joint",
        "wrist_rotate": "wrist_1_joint",
        "wrist_tilt": "wrist_2_joint",
        "wrist_twist": "wrist_3_joint",
    }

    # Reverse mapping for convenience
    LEROBOT_TO_CUSTOM_NAMES: ClassVar = {
        v: k for k, v in CUSTOM_TO_LEROBOT_NAMES.items()
    }

    # Joint limits in normalized values (-100 to +100 for most joints, 0 to 100 for gripper)
    JOINT_LIMITS: ClassVar = {
        "base_rotation": (-100.0, 100.0),
        "shoulder_tilt": (-100.0, 100.0),
        "elbow_bend": (-100.0, 100.0),
        "wrist_rotate": (-100.0, 100.0),
        "wrist_tilt": (-100.0, 100.0),
        "wrist_twist": (-100.0, 100.0),
    }

    @classmethod
    def get_joint_index(cls, joint_name: str) -> int | None:
        """
        Get the index of a joint in the standard joint order.

        Args:
            joint_name: Name of the joint (can be custom or LeRobot name)

        Returns:
            Index of the joint, or None if not found

        """
        # Try custom names first
        if joint_name in cls.CUSTOM_JOINT_NAMES:
            return cls.CUSTOM_JOINT_NAMES.index(joint_name)

        # Try LeRobot names
        if joint_name in cls.LEROBOT_JOINT_NAMES:
            return cls.LEROBOT_JOINT_NAMES.index(joint_name)

        # Try case-insensitive matching
        joint_name_lower = joint_name.lower()
        for i, name in enumerate(cls.CUSTOM_JOINT_NAMES):
            if name.lower() == joint_name_lower:
                return i

        for i, name in enumerate(cls.LEROBOT_JOINT_NAMES):
            if name.lower() == joint_name_lower:
                return i

        return None

    @classmethod
    def parse_joint_data(cls, joints_data, policy_type: str = "act") -> list[float]:
        """
        Parse joint data from Arena message into standard order.

        Expected format: dict with joint names as keys and normalized values.
        All values are already normalized from the training data pipeline.

        Args:
            joints_data: Joint data from Arena message
            policy_type: Type of policy (for logging purposes)

        Returns:
            List of 6 normalized joint values in LeRobot standard order

        """
        try:
            # Handle different possible data formats
            if hasattr(joints_data, "data"):
                joint_dict = joints_data.data
            else:
                joint_dict = joints_data

            if not isinstance(joint_dict, dict):
                return [0.0] * 6

            # Extract joint values in LeRobot standard order
            joint_values = []
            for lerobot_name in cls.LEROBOT_JOINT_NAMES:
                value = None

                # Try LeRobot name directly
                if lerobot_name in joint_dict:
                    value = float(joint_dict[lerobot_name])
                else:
                    # Try custom name
                    custom_name = cls.LEROBOT_TO_CUSTOM_NAMES.get(lerobot_name)
                    if custom_name and custom_name in joint_dict:
                        value = float(joint_dict[custom_name])
                    else:
                        # Try various common formats
                        for key in [
                            lerobot_name,
                            f"joint_{lerobot_name}",
                            lerobot_name.upper(),
                            custom_name,
                            f"joint_{custom_name}" if custom_name else None,
                        ]:
                            if key and key in joint_dict:
                                value = float(joint_dict[key])
                                break

                joint_values.append(value if value is not None else 0.0)

            return joint_values

        except Exception:
            # Return zeros if parsing fails
            return [0.0] * 6

    @classmethod
    def create_joint_commands(cls, action_values: np.ndarray) -> list[dict]:
        """
        Create joint command dictionaries from action values.

        Args:
            action_values: Array of 6 joint values in LeRobot standard order

        Returns:
            List of joint command dictionaries with custom names

        """
        commands = []
        for i, custom_name in enumerate(cls.CUSTOM_JOINT_NAMES):
            if i < len(action_values):
                commands.append({"name": custom_name, "value": float(action_values[i])})
        return commands

    @classmethod
    def validate_joint_values(cls, joint_values: np.ndarray) -> np.ndarray:
        """
        Validate and clamp joint values to their limits.

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

        # Clamp to limits
        for i, custom_name in enumerate(cls.CUSTOM_JOINT_NAMES):
            min_val, max_val = cls.JOINT_LIMITS[custom_name]
            joint_values[i] = np.clip(joint_values[i], min_val, max_val)

        return joint_values
