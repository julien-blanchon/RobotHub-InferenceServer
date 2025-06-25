import asyncio
import logging
from abc import ABC, abstractmethod

import numpy as np
import torch
from PIL import Image

from .joint_config import JointConfig

logger = logging.getLogger(__name__)


class BaseInferenceEngine(ABC):
    """
    Base class for all inference engines.

    This class provides common functionality for:
    - Image preprocessing and normalization
    - Joint data handling and validation
    - Model loading and management
    - Action prediction interface
    """

    def __init__(
        self,
        policy_path: str,
        camera_names: list[str],
        device: str | None = None,
    ):
        self.policy_path = policy_path
        self.camera_names = camera_names

        # Device selection
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        logger.info(f"Using device: {self.device}")

        # Model and preprocessing
        self.policy = None
        self.image_transforms = {}  # {camera_name: transform}
        self.stats = None  # Dataset statistics for normalization

        # State tracking
        self.is_loaded = False
        self.last_images = {}
        self.last_joint_positions = None

    @abstractmethod
    async def load_policy(self):
        """Load the policy model. Must be implemented by subclasses."""

    @abstractmethod
    async def predict(
        self, images: dict[str, np.ndarray], joint_positions: np.ndarray, **kwargs
    ) -> np.ndarray:
        """Run inference. Must be implemented by subclasses."""

    def preprocess_images(
        self, images: dict[str, np.ndarray]
    ) -> dict[str, torch.Tensor]:
        """
        Preprocess images for inference.

        Args:
            images: Dictionary of {camera_name: rgb_image_array}

        Returns:
            Dictionary of {camera_name: preprocessed_tensor}

        """
        processed_images = {}

        for camera_name, image in images.items():
            if camera_name not in self.camera_names:
                logger.warning(f"Unexpected camera: {camera_name}")
                continue

            # Convert numpy array to PIL Image if needed
            if isinstance(image, np.ndarray):
                if image.dtype != np.uint8:
                    image = (image * 255).astype(np.uint8)
                pil_image = Image.fromarray(image)
            else:
                pil_image = image

            # Apply transforms if available
            if camera_name in self.image_transforms:
                tensor = self.image_transforms[camera_name](pil_image)
            else:
                # Default preprocessing: resize to 224x224 and normalize
                tensor = self._default_image_transform(pil_image)

            processed_images[camera_name] = tensor.to(self.device)

        return processed_images

    def _default_image_transform(self, image: Image.Image) -> torch.Tensor:
        """Default image preprocessing."""
        # Resize to 224x224 (common size for vision models)
        image = image.resize((224, 224), Image.Resampling.LANCZOS)

        # Convert to tensor and normalize to [0, 1]
        tensor = torch.from_numpy(np.array(image)).float() / 255.0

        # Rearrange from HWC to CHW
        if len(tensor.shape) == 3:
            tensor = tensor.permute(2, 0, 1)

        return tensor

    def preprocess_joint_positions(self, joint_positions: np.ndarray) -> torch.Tensor:
        """
        Preprocess joint positions for inference.

        Args:
            joint_positions: Array of joint positions in standard order

        Returns:
            Preprocessed joint tensor

        """
        # Validate and clamp joint values
        joint_positions = JointConfig.validate_joint_values(joint_positions)

        # Convert to tensor
        joint_tensor = torch.from_numpy(joint_positions).float().to(self.device)

        # Normalize if we have dataset statistics
        if self.stats and hasattr(self.stats, "joint_stats"):
            joint_tensor = self._normalize_joints(joint_tensor)

        return joint_tensor

    def _normalize_joints(self, joint_tensor: torch.Tensor) -> torch.Tensor:
        """Normalize joint values using dataset statistics."""
        # This would use the actual dataset statistics
        # For now, we assume joints are already normalized
        return joint_tensor

    def get_joint_commands_with_names(self, action: np.ndarray) -> list[dict]:
        """
        Convert action array to joint commands with names.

        Args:
            action: Array of joint actions in standard order

        Returns:
            List of joint command dictionaries

        """
        # Validate action values
        action = JointConfig.validate_joint_values(action)

        # Create commands with AI names (always use AI names for output)
        return JointConfig.create_joint_commands(action)

    def reset(self):
        """Reset the inference engine state."""
        self.last_images = {}
        self.last_joint_positions = None

        # Clear any model-specific state
        if hasattr(self.policy, "reset"):
            self.policy.reset()

    async def cleanup(self):
        """Clean up resources."""
        if self.policy:
            del self.policy
            self.policy = None

        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.is_loaded = False
        logger.info(f"Cleaned up inference engine for {self.policy_path}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        if hasattr(self, "policy") and self.policy:
            asyncio.create_task(self.cleanup())
