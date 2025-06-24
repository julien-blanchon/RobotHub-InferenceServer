import logging

import cv2
import numpy as np
import torch
from lerobot.common.policies.act.modeling_act import ACTPolicy
from lerobot.common.utils.utils import init_logging

from .base_inference import BaseInferenceEngine

logger = logging.getLogger(__name__)


class ACTInferenceEngine(BaseInferenceEngine):
    """
    ACT (Action Chunking Transformer) inference engine.

    Handles image preprocessing, joint normalization, and action prediction
    for ACT models with proper action chunking.
    """

    def __init__(
        self,
        policy_path: str,
        camera_names: list[str],
        use_custom_joint_names: bool = True,
        device: str | None = None,
    ):
        super().__init__(policy_path, camera_names, use_custom_joint_names, device)

        # ACT-specific configuration
        self.chunk_size = 10  # Default chunk size for ACT
        self.action_history = []  # Store recent actions for chunking

    async def load_policy(self):
        """Load the ACT policy from the specified path."""
        logger.info(f"Loading ACT policy from: {self.policy_path}")

        try:
            # Initialize hydra config for LeRobot
            init_logging()

            # Load the ACT policy
            self.policy = ACTPolicy.from_pretrained(self.policy_path)
            self.policy.to(self.device)
            self.policy.eval()

            # Set up image transforms based on policy config
            if hasattr(self.policy, "config"):
                self._setup_image_transforms()

            self.is_loaded = True
            logger.info(f"✅ ACT policy loaded successfully on {self.device}")

        except Exception as e:
            logger.exception(f"Failed to load ACT policy from {self.policy_path}")
            msg = f"Failed to load ACT policy: {e}"
            raise RuntimeError(msg) from e

    def _setup_image_transforms(self):
        """Set up image transforms based on the policy configuration."""
        try:
            # Get image size from policy config
            config = self.policy.config
            image_size = getattr(config, "image_size", 224)

            # Create transforms for each camera
            for camera_name in self.camera_names:
                # Use policy-specific transforms if available
                if hasattr(self.policy, "image_processor"):
                    # Use the policy's image processor
                    self.image_transforms[camera_name] = self.policy.image_processor
                else:
                    # Fall back to default transform with correct size
                    from torchvision import transforms

                    self.image_transforms[camera_name] = transforms.Compose([
                        transforms.Resize((image_size, image_size)),
                        transforms.ToTensor(),
                        transforms.Normalize(
                            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                        ),
                    ])

        except Exception as e:
            logger.warning(f"Could not set up image transforms: {e}. Using defaults.")

    async def predict(
        self, images: dict[str, np.ndarray], joint_positions: np.ndarray, **kwargs
    ) -> np.ndarray:
        """
        Run ACT inference to predict actions.

        Args:
            images: Dictionary of {camera_name: rgb_image_array}
            joint_positions: Current joint positions in LeRobot standard order
            **kwargs: Additional arguments (unused for ACT)

        Returns:
            Array of predicted actions (chunk of actions for ACT)

        """
        if not self.is_loaded:
            msg = "Policy not loaded. Call load_policy() first."
            raise RuntimeError(msg)

        try:
            # Preprocess inputs
            processed_images = self.preprocess_images(images)
            processed_joints = self.preprocess_joint_positions(joint_positions)

            # Prepare batch inputs for ACT
            batch = self._prepare_batch(processed_images, processed_joints)

            # Run inference
            with torch.no_grad():
                # ACT returns a chunk of actions
                action_chunk = self.policy.predict(batch)

                # Convert to numpy
                if isinstance(action_chunk, torch.Tensor):
                    action_chunk = action_chunk.cpu().numpy()

                # Store in action history
                self.action_history.append(action_chunk)
                if len(self.action_history) > 10:  # Keep last 10 chunks
                    self.action_history.pop(0)

                logger.debug(f"ACT predicted action chunk shape: {action_chunk.shape}")
                return action_chunk

        except Exception as e:
            logger.exception("ACT inference failed")
            msg = f"ACT inference failed: {e}"
            raise RuntimeError(msg) from e

    def _prepare_batch(
        self, images: dict[str, torch.Tensor], joints: torch.Tensor
    ) -> dict:
        """
        Prepare batch inputs for ACT model.

        Args:
            images: Preprocessed images
            joints: Preprocessed joint positions

        Returns:
            Batch dictionary for ACT model

        """
        batch = {}

        # Add images to batch
        for camera_name, image_tensor in images.items():
            # Add batch dimension if needed
            if len(image_tensor.shape) == 3:
                image_tensor = image_tensor.unsqueeze(0)
            batch[f"observation.images.{camera_name}"] = image_tensor

        # Add joint positions
        if len(joints.shape) == 1:
            joints = joints.unsqueeze(0)
        batch["observation.state"] = joints

        return batch

    def reset(self):
        """Reset ACT-specific state."""
        super().reset()
        self.action_history = []

        # Reset ACT model state if it has one
        if self.policy and hasattr(self.policy, "reset"):
            self.policy.reset()

    def get_model_info(self) -> dict:
        """Get ACT-specific model information."""
        info = super().get_model_info()
        info.update({
            "policy_type": "act",
            "chunk_size": self.chunk_size,
            "action_history_length": len(self.action_history),
        })
        return info


# Utility functions for data transformation


def image_bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convert BGR image to RGB (useful for OpenCV cameras)."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def resize_image(image: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    """Resize image to target size (width, height)."""
    return cv2.resize(image, target_size)
