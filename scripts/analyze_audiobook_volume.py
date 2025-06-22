#!/usr/bin/env python3
"""
Analyze audiobook volume levels to detect if volume decreases over time.
"""

import sys
from pathlib import Path
import numpy as np
from pydub import AudioSegment
import matplotlib.pyplot as plt
from typing import List, Tuple

def analyze_audio_volume(audio_path: Path, chunk_duration_ms: int = 10000) -> Tuple[List[float], List[float]]:
    """
    Analyze audio volume levels throughout the file.
    
    Args:
        audio_path: Path to the audio file
        chunk_duration_ms: Duration of each chunk to analyze (default 10 seconds)
    
    Returns:
        (timestamps, rms_levels) - lists of timestamps and corresponding RMS levels in dB
    """
    print(f"Loading audio file: {audio_path}")
    audio = AudioSegment.from_mp3(str(audio_path))
    
    total_duration_ms = len(audio)
    print(f"Total duration: {total_duration_ms / 1000:.1f} seconds")
    
    timestamps = []
    rms_levels = []
    
    # Analyze in chunks
    for start_ms in range(0, total_duration_ms, chunk_duration_ms):
        end_ms = min(start_ms + chunk_duration_ms, total_duration_ms)
        chunk = audio[start_ms:end_ms]
        
        # Calculate RMS (root mean square) - a measure of average loudness
        rms = chunk.rms
        # Convert to dB
        if rms > 0:
            db = 20 * np.log10(rms)
        else:
            db = -120  # Silence
            
        timestamps.append(start_ms / 1000)  # Convert to seconds
        rms_levels.append(db)
        
    return timestamps, rms_levels

def plot_volume_analysis(audio_paths: List[Path], output_path: Path = None):
    """
    Plot volume analysis for one or more audio files.
    """
    plt.figure(figsize=(12, 6))
    
    for audio_path in audio_paths:
        if not audio_path.exists():
            print(f"File not found: {audio_path}")
            continue
            
        timestamps, rms_levels = analyze_audio_volume(audio_path)
        
        # Plot the volume levels
        plt.plot(timestamps, rms_levels, label=audio_path.name, linewidth=2)
        
        # Calculate and print statistics
        avg_db = np.mean(rms_levels)
        std_db = np.std(rms_levels)
        start_avg = np.mean(rms_levels[:5])  # First 5 chunks
        end_avg = np.mean(rms_levels[-5:])   # Last 5 chunks
        
        print(f"\nAnalysis for {audio_path.name}:")
        print(f"  Average volume: {avg_db:.1f} dB")
        print(f"  Std deviation: {std_db:.1f} dB")
        print(f"  Start average (first 50s): {start_avg:.1f} dB")
        print(f"  End average (last 50s): {end_avg:.1f} dB")
        print(f"  Volume drop: {start_avg - end_avg:.1f} dB")
        
        if start_avg - end_avg > 3:
            print("  ⚠️  Significant volume drop detected!")
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('Volume Level (dB)')
    plt.title('Audiobook Volume Analysis')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\nPlot saved to: {output_path}")
    else:
        plt.show()

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_audiobook_volume.py <audiobook.mp3> [audiobook2.mp3 ...]")
        print("\nThis will analyze the volume levels throughout the audiobook(s)")
        print("and show if there's a volume drop over time.")
        sys.exit(1)
    
    audio_paths = [Path(arg) for arg in sys.argv[1:]]
    
    # Check if matplotlib display is available
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        output_path = Path("volume_analysis.png")
        plot_volume_analysis(audio_paths, output_path)
    except Exception as e:
        print(f"Error creating plot: {e}")
        # Still do the analysis without plotting
        for audio_path in audio_paths:
            if audio_path.exists():
                analyze_audio_volume(audio_path)

if __name__ == "__main__":
    main()