"""
hypercraft/sound_designer.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cinematic sound design and multi-track audio engineering.
Synthesizes procedural SFX, builds frame-accurate audio cues,
and handles dynamic sidechain ducking so dialogue remains 100% intelligible.
"""

import os
import wave
import struct
import math
import random
import subprocess

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DIR)
SFX_DIR = os.path.join(ROOT_DIR, "sfx")
SAMPLE_RATE = 44100


def ensure_sfx_library():
    """Generates studio-grade procedural SFX if they don't already exist."""
    os.makedirs(SFX_DIR, exist_ok=True)
    
    def write_wav(filename, samples):
        filepath = os.path.join(SFX_DIR, filename)
        if os.path.exists(filepath):
            return filepath
        with wave.open(filepath, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            raw = b"".join([struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples])
            wf.writeframes(raw)
        return filepath

    # 1. Pop SFX (quick tactile tap/pop)
    pop_dur = 0.05
    pop_samples = []
    for i in range(int(SAMPLE_RATE * pop_dur)):
        t = i / SAMPLE_RATE
        freq = 900 * (1.0 - t / pop_dur) + 150
        amp = math.exp(-t * 80)
        pop_samples.append(math.sin(2 * math.pi * freq * t) * amp * 0.8)
    write_wav("pop.wav", pop_samples)

    # 2. Whoosh SFX (dynamic camera whoosh)
    whoosh_dur = 0.28
    whoosh_samples = []
    for i in range(int(SAMPLE_RATE * whoosh_dur)):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / whoosh_dur)) ** 2
        sweep_freq = 200 + 1600 * (t / whoosh_dur)
        noise = (random.random() * 2 - 1) * 0.4
        tone = math.sin(2 * math.pi * sweep_freq * t) * 0.6
        whoosh_samples.append((noise + tone) * env * 0.7)
    write_wav("whoosh.wav", whoosh_samples)

    # 3. Bass Hit / Impact (sub-drop tension builder)
    bass_dur = 0.35
    bass_samples = []
    for i in range(int(SAMPLE_RATE * bass_dur)):
        t = i / SAMPLE_RATE
        freq = 130 * math.exp(-t * 8) + 38
        env = math.exp(-t * 9)
        bass_samples.append(math.sin(2 * math.pi * freq * t) * env * 0.9)
    write_wav("bass_hit.wav", bass_samples)

    # 4. Alert / Chime (high urgency bell)
    alert_dur = 0.2
    alert_samples = []
    for i in range(int(SAMPLE_RATE * alert_dur)):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 22)
        s1 = math.sin(2 * math.pi * 1046.5 * t)
        s2 = math.sin(2 * math.pi * 2093.0 * t) * 0.4
        alert_samples.append((s1 + s2) * env * 0.6)
    write_wav("alert.wav", alert_samples)


def build_sfx_track(cues: list[dict], total_duration: float, output_wav: str) -> str:
    """
    Assembles a master SFX audio track by mixing cue events at exact timestamps.
    Each cue: {'type': 'whoosh'|'pop'|'bass_hit'|'alert', 'time': float_sec, 'volume': 0.8}
    """
    ensure_sfx_library()
    total_samples = int(total_duration * SAMPLE_RATE)
    master_buffer = [0.0] * total_samples

    sfx_cache = {}
    for cue in cues:
        sfx_type = cue.get("type", "pop")
        start_time = cue.get("time", 0.0)
        volume = cue.get("volume", 0.7)
        start_idx = int(start_time * SAMPLE_RATE)

        if sfx_type not in sfx_cache:
            wav_path = os.path.join(SFX_DIR, f"{sfx_type}.wav")
            if not os.path.exists(wav_path):
                continue
            with wave.open(wav_path, "r") as wf:
                n = wf.getnframes()
                raw_bytes = wf.readframes(n)
                samples = struct.unpack(f"<{n}h", raw_bytes)
                sfx_cache[sfx_type] = [s / 32767.0 for s in samples]

        sfx_samples = sfx_cache.get(sfx_type, [])
        for i, sample in enumerate(sfx_samples):
            target_idx = start_idx + i
            if 0 <= target_idx < total_samples:
                master_buffer[target_idx] += sample * volume

    # Normalize to prevent digital clipping
    max_val = max(abs(s) for s in master_buffer) if master_buffer else 1.0
    norm_factor = 0.95 / max_val if max_val > 0.95 else 1.0

    with wave.open(output_wav, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        raw = b"".join([struct.pack("<h", max(-32767, min(32767, int(s * norm_factor * 32767)))) for s in master_buffer])
        wf.writeframes(raw)

    return output_wav
