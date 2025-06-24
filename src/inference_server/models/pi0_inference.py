import logging

import numpy as np
import torch
from lerobot.common.policies.pi0.modeling_pi0 import PI0Policy
from lerobot.common.utils.utils import init_logging

from .base_inference import BaseInferenceEngine

logger = logging.getLogger(__name__)


class Pi0InferenceEngine(BaseInferenceEngine):
    """
    Pi0 (Physical Intelligence) inference engine.

    Handles image preprocessing, joint normalization, and action prediction
    for Pi0 models with language instruction support.
    """

    def __init__(
        self,
        policy_path: str,
        camera_names: list[str],
        use_custom_joint_names: bool = True,
        device: str | None = None,
        language_instruction: str | None = None,
    ):
        super().__init__(policy_path, camera_names, use_custom_joint_names, device)

        # Pi0-specific configuration
        self.language_instruction = language_instruction
        self.supports_language = True

    async def load_policy(self):
        """Load the Pi0 policy from the specified path."""
        logger.info(f"Loading Pi0 policy from: {self.policy_path}")

        try:
            # Initialize hydra config for LeRobot
            init_logging()

            # Load the Pi0 policy
            self.policy = PI0Policy.from_pretrained(self.policy_path)
            self.policy.to(self.device)
            self.policy.eval()

            # Set up image transforms based on policy config
            if hasattr(self.policy, "config"):
                self._setup_image_transforms()

            self.is_loaded = True
            logger.info(f"✅ Pi0 policy loaded successfully on {self.device}")

        except Exception as e:
            logger.exception(f"Failed to load Pi0 policy from {self.policy_path}")
            msg = f"Failed to load Pi0 policy: {e}"
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
                    self.image_transforms[camera_name] = self.policy.image_processor
                else:
                    # Fall back to default transform
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
        Run Pi0 inference to predict actions.

        Args:
            images: Dictionary of {camera_name: rgb_image_array}
            joint_positions: Current joint positions in LeRobot standard order
            task: Optional language instruction (overrides instance language_instruction)

        Returns:
            Array of predicted actions

        """
        if not self.is_loaded:
            msg = "Policy not loaded. Call load_policy() first."
            raise RuntimeError(msg)

        try:
            # Preprocess inputs
            processed_images = self.preprocess_images(images)
            processed_joints = self.preprocess_joint_positions(joint_positions)

            # Get language instruction
            task = kwargs.get("task", self.language_instruction)

            # Prepare batch inputs for Pi0
            batch = self._prepare_batch(processed_images, processed_joints, task)

            # Run inference
            with torch.no_grad():
                action = self.policy.predict(batch)

                # Convert to numpy
                if isinstance(action, torch.Tensor):
                    action = action.cpu().numpy()

                logger.debug(f"Pi0 predicted action shape: {action.shape}")
                return action

        except Exception as e:
            logger.exception("Pi0 inference failed")
            msg = f"Pi0 inference failed: {e}"
            raise RuntimeError(msg) from e

    def _prepare_batch(
        self,
        images: dict[str, torch.Tensor],
        joints: torch.Tensor,
        task: str | None = None,
    ) -> dict:
        """
        Prepare batch inputs for Pi0 model.

        Args:
            images: Preprocessed images
            joints: Preprocessed joint positions
            task: Language instruction

        Returns:
            Batch dictionary for Pi0 model

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

        # Add language instruction if provided
        if task:
            batch["task"] = task

        return batch

    def get_model_info(self) -> dict:
        """Get Pi0-specific model information."""
        info = super().get_model_info()
        info.update({
            "policy_type": "pi0",
            "supports_language": self.supports_language,
            "language_instruction": self.language_instruction,
        })
        return info
