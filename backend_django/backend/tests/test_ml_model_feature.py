"""
FEATURE: Melanoma Detection & Prediction Pipeline
Tests the ML workflow - model loading, preprocessing, and prediction.
Includes one deliberate failure to highlight missing error handling.
"""

import os
import torch
from PIL import Image
from django.test import TestCase
from unittest.mock import MagicMock, patch
from backend.ml import detection_model


class MelanomaDetectionFeatureTest(TestCase):
    """
    Tests the three core ML units:
    - load_model(): model loading from .pth file
    - preprocess_image(): image normalization & resizing
    - predict_melanoma(): end-to-end prediction pipeline
    """

    def setUp(self):
        """Create a dummy image for prediction tests"""
        self.test_image_path = "test_temp_image.jpg"
        image = Image.new("RGB", (300, 300), color=(255, 0, 0))
        image.save(self.test_image_path)

    def tearDown(self):
        """Cleanup temporary test image"""
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)

    # Test 1: Model loading works
    def test_model_loads_successfully(self):
        """UNIT: load_model() should return a valid torch.nn.Module"""
        model = detection_model.load_model()
        self.assertIsInstance(model, torch.nn.Module)
        self.assertFalse(model.training)  # should be in eval() mode

    # Test 2: Preprocess converts image into correct tensor shape
    def test_preprocess_image_shape_and_type(self):
        """UNIT: preprocess_image() should return 1x3x224x224 tensor"""
        tensor = detection_model.preprocess_image(self.test_image_path)
        self.assertEqual(tensor.shape, (1, 3, 224, 224))
        self.assertTrue(torch.is_tensor(tensor))

    # Test 3: Full prediction returns valid output structure
    def test_predict_melanoma_output_structure(self):
        """UNIT: predict_melanoma() returns correct dictionary keys"""
        model = detection_model.load_model()
        result = detection_model.predict_melanoma(model, self.test_image_path)

        # Expect result keys
        expected_keys = {"prediction", "confidence", "risk", "recommendations"}
        self.assertTrue(expected_keys.issubset(result.keys()))
        self.assertIn(result["prediction"], ["Benign", "Melanoma"])
        self.assertIsInstance(result["confidence"], float)
        self.assertIsInstance(result["recommendations"], list)

    # Test 4: Missing file not handled properly
    def test_predict_melanoma_with_invalid_file_type(self):
        """
        UNIT: predict_melanoma() error handling
        EXPECTED: Should handle missing/corrupted image gracefully.
        ACTUAL: Raises unhandled exception -> FAILS.
        """
        model = detection_model.load_model()
        invalid_path = "image.pdf"

        # We expect exception since function has no try/except for bad files
        with self.assertRaises(FileNotFoundError):
            detection_model.predict_melanoma(model, invalid_path)

    # Test 5: Mock model output to test classification logic
    @patch("backend.ml.detection_model.EfficientNetClassifier.forward")
    def test_predict_melanoma_classification_logic(self, forward):
        """
        UNIT: predict_melanoma() classification branch
        Simulates model predicting Melanoma with high confidence.
        """
        # output tensor for class index 1 (Melanoma)
        output = torch.tensor([[0.1, 0.9]])
        forward.return_value = output

        model = detection_model.load_model()
        result = detection_model.predict_melanoma(model, self.test_image_path)

        self.assertEqual(result["prediction"], "Melanoma")
        self.assertEqual(result["risk"], "High")
        self.assertGreater(result["confidence"], 80)
