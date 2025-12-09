import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

# Mock sounddevice and soundfile before importing controller
sys.modules['sounddevice'] = MagicMock()
sys.modules['soundfile'] = MagicMock()
sys.modules['pyaudio'] = MagicMock()

from controller import controlador
from model import modelo

class TestFFTParams(unittest.TestCase):
    def setUp(self):
        # Mock view
        self.mock_view = MagicMock()
        self.mock_view.btngbr.isChecked.return_value = False
        
        # Initialize controller with mocked view
        with patch('model.pyaudio.PyAudio') as mock_pa:
            self.controller = controlador()
            self.controller.cVista = self.mock_view
            
            # Ensure model has the mock stream
            self.controller.cModel.pyaudio_instance = mock_pa.return_value
            self.controller.cModel.stream = MagicMock()
            self.controller.cModel.stream.is_active.return_value = True

    def test_update_fft_parameters(self):
        # Initial values
        # Force set initial values to ensure we see a change
        self.controller.cModel.rate = 44100
        self.controller.cModel.chunk = 1024
        
        initial_rate = self.controller.cModel.rate
        initial_chunk = self.controller.cModel.chunk
        print(f"Initial Rate: {initial_rate}, Initial Chunk: {initial_chunk}")
        
        # New values
        new_rate = 48000
        new_chunk = 2048
        
        # Call update method
        print(f"Updating to Rate: {new_rate}, Chunk: {new_chunk}")
        self.controller.update_fft_parameters(new_rate, new_chunk)
        
        # Verify model values updated
        self.assertEqual(self.controller.cModel.rate, new_rate)
        self.assertEqual(self.controller.cModel.chunk, new_chunk)
        print(f"Verified Rate: {self.controller.cModel.rate}, Verified Chunk: {self.controller.cModel.chunk}")
        
        # Verify stream was re-initialized
        # initialize_audio_stream calls open on pyaudio instance
        self.controller.cModel.pyaudio_instance.open.assert_called()
        print("Audio stream re-initialization verified")

if __name__ == '__main__':
    unittest.main()
