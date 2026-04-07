#!/usr/bin/env python3
"""Verifica se o áudio foi gerado com narração real via pyttsx3."""

import os
import numpy as np
from scipy.io import wavfile

# Procura arquivo de áudio mais recente
audio_dir = 'output'
audio_files = [f for f in os.listdir(audio_dir) if f.startswith('audio_') and f.endswith('.wav')]
if not audio_files:
    print('❌ Nenhum arquivo de áudio encontrado')
    exit(1)

audio_file = os.path.join(audio_dir, sorted(audio_files)[-1])
print(f'Analisando: {audio_file}')
print()

try:
    # Lê arquivo WAV
    sample_rate, data = wavfile.read(audio_file)
    
    # Converte stereo para mono se necessário
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    
    # Converte para float32
    if data.dtype == np.int16:
        audio_float = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        audio_float = data.astype(np.float32) / 2147483648.0
    else:
        audio_float = data.astype(np.float32)
    
    # Estatísticas gerais
    rms = np.sqrt(np.mean(audio_float ** 2))
    peak = np.max(np.abs(audio_float))
    mean = np.mean(audio_float)
    duration = len(audio_float) / sample_rate
    
    print(f'📊 ESTATÍSTICAS DO ÁUDIO:')
    print(f'   Taxa: {sample_rate} Hz')
    print(f'   Duração: {duration:.1f}s ({int(duration/60)}min {int(duration%60)}s)')
    print(f'   Samples: {len(audio_float):,}')
    print(f'   RMS (energia): {rms:.6f}')
    print(f'   Pico: {peak:.6f}')
    print(f'   Média: {mean:.6f}')
    print()
    
    # Análise de frequência em 3 segundos no meio do áudio
    mid_point = len(audio_float) // 2
    window = audio_float[mid_point:mid_point + sample_rate*3]  # 3 segundos
    
    fft = np.fft.fft(window)
    freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
    magnitude = np.abs(fft)
    
    # Pega componentes com maior energia (frequências principais)
    peak_indices = np.argsort(magnitude)[-5:][::-1]
    peak_freqs = freqs[peak_indices]
    
    print(f'🎙️  CARACTERÍSTICAS DE FREQUÊNCIA (3s do meio do áudio):')
    for i, (idx, freq) in enumerate(zip(peak_indices, peak_freqs)):
        if freq > 0:  # Só frequências positivas
            print(f'   {i+1}. {freq:.0f} Hz (magnitude: {magnitude[idx]:.1f})')
    print()
    
    # Análise de variação (se há mudanças, indica fala real)
    # Calcula diferenças absolutas entre amostras consecutivas
    diff = np.abs(np.diff(audio_float))
    std_diff = np.std(diff)
    mean_diff = np.mean(diff)
    
    print(f'📈 ANÁLISE DE VARIAÇÃO (indica movimento/fala):')
    print(f'   Variação média: {mean_diff:.6f}')
    print(f'   Std da variação: {std_diff:.6f}')
    print()
    
    # Diagnóstico final
    print(f'🔍 DIAGNÓSTICO:')
    
    is_silent = rms < 0.001
    is_noisy = rms > 0.5
    is_speech = (rms > 0.01 and rms < 0.3 and std_diff > 0.0001)
    
    if is_silent:
        print(f'   ❌ Áudio SILENCIOSO (RMS < 0.001)')
    elif is_noisy:
        print(f'   ⚠️  Áudio com muito RUÍDO (RMS > 0.5)')
    elif is_speech:
        print(f'   ✅ FALA/NARRAÇÃO DETECTADA!')
        print(f'      - RMS em range de fala: {rms:.4f}')
        print(f'      - Variação detectada: {std_diff:.6f}')
        print(f'      - Frequências principais: {peak_freqs[:2].astype(int)}')
    else:
        print(f'   ⚠️  Conteúdo indefinido (RMS: {rms:.4f})')
    
    print()
    print(f'✨ STATUS: {"🎙️  NARRAÇÃO REAL" if is_speech else ("❌ FALHA" if is_silent else "⚠️  POSSÍVEL CONTEÚDO")}')
    
except Exception as e:
    print(f'❌ Erro ao analisar áudio: {e}')
    import traceback
    traceback.print_exc()
