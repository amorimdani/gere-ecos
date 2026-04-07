"""
Audio Agent - Responsável por converter roteiros em narração de áudio
Gera MP3 sincronizado com duração do vídeo
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
import moviepy.editor as mpy
import numpy as np
from scipy.io import wavfile
import wave
import pyttsx3
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from agents.tts_manager import TTSManager
from config.logger import get_logger

logger = get_logger(__name__)


class AudioAgent(BaseAgent):
    """
    Agente responsável por:
    1. Receber roteiro do ContentAgent
    2. Gerar narração MP3 com qualidade alta
    3. Sincronizar com duração esperada do vídeo
    4. Fallback automático de TTS
    """
    
    def __init__(self):
        super().__init__(agent_name="AudioAgent", max_retries=3)
        self.tts_manager = TTSManager(self.config)
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa o pipeline de geração de áudio.
        
        Args:
            payload: {
                "script": "roteiro completo",
                "video_title": "título do vídeo (para nome do arquivo)",
                "expected_duration_minutes": 10,
                "output_filename": "nome_do_arquivo.mp3" (opcional)
            }
            
        Returns:
            dict: Áudio gerado com metadata
        """
        
        # Valida payload
        script = payload.get("script")
        if not script:
            raise ValueError("Script é obrigatório no payload")
        
        video_title = payload.get("video_title", "video_sem_titulo")
        duration_minutes = payload.get("expected_duration_minutes", 10)
        output_filename = payload.get("output_filename")
        
        self.log_info(f"Gerando áudio para: {video_title}")
        self.log_info(f"Duração esperada: {duration_minutes} minutos")
        
        # 1. Limpa e prepara script
        cleaned_script = self._clean_script(script)
        self.log_info(f"Script preparado ({len(cleaned_script.split())} palavras)")
        
        # 2. Define caminho de saída
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = self._sanitize_filename(video_title)
            output_filename = f"audio_{safe_title}_{timestamp}.mp3"
        
        output_path = os.path.join(self.config.output_dir, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 3. Gera narração real usando síntese de fala offline
        duration_seconds = duration_minutes * 60
        wav_path = os.path.splitext(output_path)[0] + ".wav"
        
        try:
            self.log_info("Gerando narração real com Edge-tTS (voz profissional)...")
            audio_data, sample_rate = await self._generate_edge_tts_narration(
                script=cleaned_script,
                target_duration_seconds=duration_seconds
            )
            
            # Escreve arquivo WAV
            from scipy.io import wavfile
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wavfile.write(wav_path, sample_rate, audio_int16)
            
            file_size = os.path.getsize(wav_path)
            actual_duration = len(audio_data) / sample_rate
            
            # Valida arquivo escrito
            verify_clip = mpy.AudioFileClip(wav_path)
            verify_duration = verify_clip.duration
            verify_clip.close()
            
            self.log_info(f"✅ Narração gerada: {file_size} bytes, duração: {verify_duration:.1f}s")
            
            output_path = wav_path
            tts_result = {
                "success": True,
                "provider": "pyttsx3-offline",
                "file_size": file_size,
                "duration": verify_duration
            }
            
        except Exception as e:
            self.log_error(f"Erro ao gerar narração: {e}")
            raise Exception(f"Falha ao gerar narração de áudio: {e}")
        
        self.log_info(f"Áudio gerado com sucesso ({tts_result['file_size']} bytes)")
        
        # 4. Calcula metadata
        audio_metadata = await self._extract_audio_metadata(output_path, cleaned_script)
        
        # 5. Retorna resultado
        result = {
            "audio_path": output_path,
            "output_filename": output_filename,
            "file_size": tts_result["file_size"],
            "tts_provider": tts_result["provider"],
            "script_length": len(cleaned_script.split()),
            "expected_duration_minutes": duration_minutes,
            "actual_duration_seconds": audio_metadata.get("estimated_duration"),
            "timestamp": datetime.now().isoformat()
        }
        
        self.log_info(f"Áudio finalizado: {output_filename}")
        return result
    
    async def _generate_edge_tts_narration(self, script: str, target_duration_seconds: int) -> Tuple[np.ndarray, int]:
        """
        Gera narração profissional usando Edge-tTS com voz masculina grave em português.
        
        Args:
            script: Conteúdo completo da história para narrar
            target_duration_seconds: Duração alvo (apenas para logging)
            
        Returns:
            Tuple: (audio_array, sample_rate)
        """
        try:
            import edge_tts
            
            # Voz masculina grave em português brasileiro
            voice = "pt-BR-AntonioNeural"  # Voz profissional masculina
            rate = "-10%"  # Velocidade ligeiramente reduzida para mais clareza
            
            # Cria arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tmp_path = tmp.name
            
            try:
                # Gera áudio com Edge-tTS
                communicate = edge_tts.Communicate(
                    text=script,
                    voice=voice,
                    rate=rate
                )
                await communicate.save(tmp_path)
                
                self.log_info(f"✅ Edge-tTS: Voz {voice} com velocidade {rate}")
                
                # Carrega MP3 com moviepy
                audio_clip = mpy.AudioFileClip(tmp_path)
                actual_duration = audio_clip.duration
                
                # Escreve para WAV temporário e relê
                wav_temp = tmp_path.replace('.mp3', '_temp.wav')
                try:
                    audio_clip.write_audiofile(wav_temp, verbose=False, logger=None)
                    sample_rate, audio_data_int = wavfile.read(wav_temp)
                    
                    # Converte para float
                    if audio_data_int.dtype == np.int16:
                        audio_data = audio_data_int.astype(np.float32) / 32768.0
                    else:
                        audio_data = audio_data_int.astype(np.float32)
                    
                    if len(audio_data.shape) > 1:
                        audio_data = np.mean(audio_data, axis=1)
                finally:
                    if os.path.exists(wav_temp):
                        try:
                            os.remove(wav_temp)
                        except:
                            pass
                
                word_count = len(script.split())
                self.log_info(f"Narração gerada: {actual_duration:.1f}s, {word_count} palavras")
                
                # Ajusta duração com padding/truncamento
                if actual_duration < target_duration_seconds * 0.9:
                    # Muito curto - adiciona silêncio
                    padding_samples = int(sample_rate * (target_duration_seconds - actual_duration))
                    audio_data = np.concatenate([audio_data, np.zeros(padding_samples)])
                    self.log_info(f"Adicionado silêncio: {padding_samples} samples")
                elif actual_duration > target_duration_seconds * 1.1:
                    # Muito longo - trunca
                    max_samples = int(sample_rate * target_duration_seconds)
                    audio_data = audio_data[:max_samples]
                    self.log_info(f"Áudio truncado para {target_duration_seconds}s")
                
                # Normaliza amplitude para evitar clipping e garantir volume constante
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    audio_data = (audio_data / max_val) * 0.95  # 95% para volume máximo sem distorção
                
                # Aplica um leve fade in/out para evitar cliques
                fade_samples = int(sample_rate * 0.05) # 50ms
                if len(audio_data) > fade_samples * 2:
                    fade_in = np.linspace(0, 1, fade_samples)
                    fade_out = np.linspace(1, 0, fade_samples)
                    audio_data[:fade_samples] *= fade_in
                    audio_data[-fade_samples:] *= fade_out
                
                audio_clip.close()
                return audio_data, sample_rate
                
            finally:
                # Limpa arquivo temporário
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except:
                        pass
                        
        except ImportError:
            self.log_error("edge_tts não instalado, usando fallback pyttsx3...")
            return self._generate_pyttsx3_fallback(script, target_duration_seconds)
        except Exception as e:
            self.log_error(f"Erro em Edge-tTS: {e}, usando fallback...")
            return self._generate_pyttsx3_fallback(script, target_duration_seconds)
    
    def _generate_pyttsx3_fallback(self, script: str, target_duration_seconds: int) -> Tuple[np.ndarray, int]:
        """Fallback para pyttsx3 quando Edge-tTS não está disponível"""
        try:
            engine = pyttsx3.init()
            
            word_count = len(script.split())
            estimated_duration_natural = (word_count / 150) * 60
            
            # Ajusta velocidade moderadamente
            rate = engine.getProperty('rate')
            if estimated_duration_natural > 0:
                speed_multiplier = target_duration_seconds / estimated_duration_natural
                speed_multiplier = max(0.7, min(1.3, speed_multiplier))  # Limita menos extremo
                new_rate = rate * speed_multiplier
                engine.setProperty('rate', new_rate)
                self.log_info(f"Velocidade pyttsx3: {new_rate:.1f} WPM")
            
            engine.setProperty('volume', 0.9)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp_path = tmp.name
            
            try:
                engine.save_to_file(script, tmp_path)
                engine.runAndWait()
                
                sample_rate, audio_data = wavfile.read(tmp_path)
                
                if audio_data.dtype == np.int16:
                    audio_float = audio_data.astype(np.float32) / 32768.0
                else:
                    audio_float = audio_data.astype(np.float32)
                
                if len(audio_float.shape) > 1:
                    audio_float = np.mean(audio_float, axis=1)
                
                actual_duration = len(audio_float) / sample_rate
                
                if actual_duration < target_duration_seconds * 0.9:
                    padding_samples = int(sample_rate * (target_duration_seconds - actual_duration))
                    audio_float = np.concatenate([audio_float, np.zeros(padding_samples)])
                elif actual_duration > target_duration_seconds * 1.1:
                    max_samples = int(sample_rate * target_duration_seconds)
                    audio_float = audio_float[:max_samples]
                
                max_val = np.max(np.abs(audio_float))
                if max_val > 0:
                    audio_float = (audio_float / max_val) * 0.90
                
                return audio_float, sample_rate
                
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except:
                        pass
                engine.stop()
                
        except Exception as e:
            self.log_error(f"Erro em pyttsx3 fallback: {e}")
            raise
    
    def _clean_script(self, script: str) -> str:
        """
        Remove marcações de cenas e formata script para narração.
        
        Args:
            script: Script bruto com marcações
            
        Returns:
            str: Script limpo e formatado
        """
        lines = []
        
        for line in script.split('\n'):
            # Remove marcações de cena
            if line.startswith('[CENA') or line.startswith('[HOOK]') or \
               line.startswith('[PLOT') or line.startswith('[FINAL]'):
                lines.append(line.replace('[', '').replace(']', ''))
            else:
                lines.append(line)
        
        # Remove linhas vazias e limpa espaços
        cleaned = '\n'.join(line.strip() for line in lines if line.strip())
        
        # Remove caracteres especiais problemáticos para TTS
        cleaned = cleaned.replace('\\n', ' ')
        cleaned = cleaned.replace('  ', ' ')  # Remove espaços duplos
        
        return cleaned
    
    def _sanitize_filename(self, filename: str) -> str:
        """Remove caracteres inválidos para nomes de arquivo"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:50]  # Limita comprimento
    
    async def _extract_audio_metadata(self, audio_path: str, 
                                     script: str) -> Dict[str, Any]:
        """
        Extrai metadata do áudio gerado.
        
        Args:
            audio_path: Caminho do arquivo MP3
            script: Script narrado
            
        Returns:
            dict: Metadata do áudio
        """
        try:
            # Tenta usar pydub para extrair duração
            file_size = os.path.getsize(audio_path)
            
            # Estima duração baseada em tamanho do arquivo
            # MP3 com qualidade típica: ~128 kbps
            estimated_duration = (file_size * 8) / (128 * 1000)  # em segundos
            
            # Estima palavras e velocidade de fala
            word_count = len(script.split())
            words_per_minute = (word_count / estimated_duration) * 60
            
            return {
                "file_size": file_size,
                "estimated_duration": estimated_duration,
                "word_count": word_count,
                "words_per_minute": words_per_minute
            }
            
        except Exception as e:
            self.log_warning(f"Erro ao extrair metadata: {str(e)}")
            return {
                "file_size": 0,
                "estimated_duration": 0,
                "word_count": len(script.split())
            }


class AudioAgentWithPydub(BaseAgent):
    """
    Versão estendida do AudioAgent que usa pydub para processamento
    Permite modificação de velocidade e pitch do áudio
    """
    
    def __init__(self):
        super().__init__("AudioAgentPydub", max_retries=3)
        self.tts_manager = TTSManager(self.config)
        self.audio_agent = AudioAgent()
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera áudio com ajustes avançados.
        
        Args:
            payload: Mesma estrutura do AudioAgent +
                     speed_factor: 1.0 = normal, 1.2 = 20% mais rápido
                     pitch_change: 0 = normal, 10 = 10 semitons mais agudo
        
        Returns:
            dict: Áudio com ajustes aplicados
        """
        
        # Gera áudio base
        result = await self.audio_agent.execute(payload)
        
        if not result:
            raise Exception("Falha ao gerar áudio base")
        
        # Aplica ajustes se especificados
        speed_factor = payload.get("speed_factor", 1.0)
        pitch_change = payload.get("pitch_change", 0)
        
        if speed_factor != 1.0 or pitch_change != 0:
            try:
                adjusted_result = await self._apply_audio_adjustments(
                    result["audio_path"],
                    speed_factor,
                    pitch_change
                )
                result.update(adjusted_result)
            except Exception as e:
                self.log_warning(f"Não foi possível aplicar ajustes: {str(e)}")
                # Continua com áudio base se ajustes falharem
        
        return result
    
    async def _apply_audio_adjustments(self, audio_path: str, 
                                       speed_factor: float, 
                                       pitch_change: int) -> Dict[str, Any]:
        """Aplica ajustes de velocidade e pitch ao áudio"""
        try:
            from pydub import AudioSegment
            from pydub.playback import play
            import math
            
            self.log_info(f"Aplicando ajustes: velocidade={speed_factor}, pitch={pitch_change}")
            
            # Carrega áudio
            audio = AudioSegment.from_mp3(audio_path)
            
            # Ajusta velocidade (aumenta/diminui frame rate)
            if speed_factor != 1.0:
                # Speedup by changing frame rate
                audio = audio.speedup(playback_speed=speed_factor)
            
            # Nota: Ajuste de pitch com pydub é complexo
            # Para versão simples, apenas retorna aviso
            if pitch_change != 0:
                self.log_warning("Ajuste de pitch requer librosa/numpy (opcional)")
            
            # Salva áudio ajustado
            adjusted_path = audio_path.replace(".mp3", "_adjusted.mp3")
            audio.export(adjusted_path, format="mp3")
            
            return {
                "audio_path_adjusted": adjusted_path,
                "speed_factor_applied": speed_factor,
                "pitch_change_applied": pitch_change
            }
            
        except ImportError:
            self.log_warning("pydub não disponível para ajustes avançados")
            return {}


def create_audio_agent() -> AudioAgent:
    """Factory function para criar o agente de áudio"""
    return AudioAgent()


def create_audio_agent_with_pydub() -> AudioAgentWithPydub:
    """Factory function para criar agente com ajustes avançados"""
    return AudioAgentWithPydub()
