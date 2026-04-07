#!/usr/bin/env python3
"""Teste simples de áudio com scipy"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path

# Encontra o áudio mais recente
audio_files = sorted(Path('output').glob('audio*.wav'), key=lambda p: p.stat().st_mtime, reverse=True)

if not audio_files:
    print("Nenhum arquivo WAV encontrado")
    exit(1)

audio_file = str(audio_files[0])
print(f"Analisando: {Path(audio_file).name}")
print("-" * 60)

try:
    # Lê o WAV com scipy
    rate, data = wavfile.read(audio_file)
    
    print(f"Taxa de amostragem: {rate} Hz")
    print(f"Duração: {len(data) / rate:.1f} segundos")
    print(f"Canais: {len(data.shape)} dimensions")
    print(f"Tipo de dado: {data.dtype}")
    
    # Análise dos primeiros 30 segundos
    samples_to_analyze = min(int(rate * 30), len(data))
    segment = data[:samples_to_analyze]
    
    # Converte para float se necessário
    if data.dtype == np.int16:
        segment_float = segment.astype(np.float32) / 32768.0
    else:
        segment_float = segment.astype(np.float32)
    
    # Calcula RMS e pico
    rms = np.sqrt(np.mean(segment_float**2))
    peak = np.max(np.abs(segment_float))
    mean_val = np.mean(np.abs(segment_float))
    
    print(f"\nAnálise dos primeiros 30 segundos:")
    print(f"  RMS (energia): {rms:.6f}")
    print(f"  Pico: {peak:.6f}")
    print(f"  Média: {mean_val:.6f}")
    
    if rms > 0.001:
        print(f"\nRESULTADO: Audio TEM CONTEUDO!")
    else:
        print(f"\nRESULTADO: Audio esta SILENCIOSO")
        
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
