# effects.py - Audio effects engine
import numpy as np
from scipy import signal
import os

class AudioEffects:
    """Audio effects processor"""
    
    @staticmethod
    def fade_in(data, sr, duration=0.5):
        """
        Fade in audio over specified duration
        
        Args:
            data: Audio data (numpy array)
            sr: Sample rate
            duration: Fade duration in seconds
        
        Returns:
            Audio data with fade in applied
        """
        samples = int(duration * sr)
        samples = min(samples, len(data))  # Don't exceed audio length
        
        fade = np.linspace(0, 1, samples)
        result = data.copy()
        result[:samples] = result[:samples] * fade
        
        return result
    
    @staticmethod
    def fade_out(data, sr, duration=0.5):
        """
        Fade out audio over specified duration
        
        Args:
            data: Audio data (numpy array)
            sr: Sample rate
            duration: Fade duration in seconds
        
        Returns:
            Audio data with fade out applied
        """
        samples = int(duration * sr)
        samples = min(samples, len(data))  # Don't exceed audio length
        
        fade = np.linspace(1, 0, samples)
        result = data.copy()
        result[-samples:] = result[-samples:] * fade
        
        return result
    
    @staticmethod
    def normalize(data, target_level=0.95):
        """
        Normalize audio to target level
        
        Args:
            data: Audio data
            target_level: Target peak level (0.0 to 1.0)
        
        Returns:
            Normalized audio data
        """
        peak = np.max(np.abs(data))
        if peak > 0:
            return data * (target_level / peak)
        return data
    
    @staticmethod
    def add_echo(data, sr, delay=0.3, decay=0.5):
        """
        Add echo effect
        
        Args:
            data: Audio data
            sr: Sample rate
            delay: Echo delay in seconds
            decay: Echo decay factor (0.0 to 1.0)
        
        Returns:
            Audio with echo applied
        """
        delay_samples = int(delay * sr)
        
        # Create output buffer with extra space for echo
        output = np.zeros(len(data) + delay_samples)
        
        # Original sound
        output[:len(data)] = data
        
        # Add echo
        output[delay_samples:delay_samples + len(data)] += data * decay
        
        # Trim back to original length
        return output[:len(data)]
    
    @staticmethod
    def change_speed(data, rate=1.0):
        """
        Change playback speed (affects pitch)
        
        Args:
            data: Audio data
            rate: Speed multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double)
        
        Returns:
            Speed-adjusted audio
        """
        if rate == 1.0:
            return data
        
        # Simple resampling
        indices = np.arange(0, len(data), rate)
        indices = indices[indices < len(data)]
        
        return np.interp(indices, np.arange(len(data)), data).astype(np.float32)
    
    @staticmethod
    def compress(data, threshold=0.5, ratio=4.0):
        """
        Dynamic range compression
        
        Args:
            data: Audio data
            threshold: Compression threshold (0.0 to 1.0)
            ratio: Compression ratio
        
        Returns:
            Compressed audio
        """
        result = data.copy()
        
        # Apply compression to samples above threshold
        mask = np.abs(result) > threshold
        sign = np.sign(result[mask])
        
        # Compress the portion above threshold
        excess = np.abs(result[mask]) - threshold
        result[mask] = sign * (threshold + excess / ratio)
        
        return result
    
    @staticmethod
    def apply_effect(sound_name, effect_name, sounds, **kwargs):
        """
        Apply effect to a sound
        
        Args:
            sound_name: Name of sound to apply effect to
            effect_name: Name of effect ('fade_in', 'fade_out', 'normalize', etc.)
            sounds: Dictionary of all sounds
            **kwargs: Additional effect parameters
        
        Returns:
            True if successful, False otherwise
        """
        if sound_name not in sounds:
            return False
        
        sound = sounds[sound_name]
        data = sound['data']
        sr = 44100  # Sample rate
        
        try:
            if effect_name == 'fade_in':
                duration = kwargs.get('duration', 0.5)
                sound['data'] = AudioEffects.fade_in(data, sr, duration)
            
            elif effect_name == 'fade_out':
                duration = kwargs.get('duration', 0.5)
                sound['data'] = AudioEffects.fade_out(data, sr, duration)
            
            elif effect_name == 'normalize':
                target = kwargs.get('target_level', 0.95)
                sound['data'] = AudioEffects.normalize(data, target)
            
            elif effect_name == 'echo':
                delay = kwargs.get('delay', 0.3)
                decay = kwargs.get('decay', 0.5)
                sound['data'] = AudioEffects.add_echo(data, sr, delay, decay)
            
            elif effect_name == 'speed':
                rate = kwargs.get('rate', 1.0)
                sound['data'] = AudioEffects.change_speed(data, rate)
            
            elif effect_name == 'compress':
                threshold = kwargs.get('threshold', 0.5)
                ratio = kwargs.get('ratio', 4.0)
                sound['data'] = AudioEffects.compress(data, threshold, ratio)
            
            else:
                return False
            
            # Reset playback position
            sound['pos'] = 0
            
            return True
            
        except Exception as e:
            print(f"Error applying effect {effect_name}: {e}")
            return False