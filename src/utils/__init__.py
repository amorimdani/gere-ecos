"""
Módulo de Utilitários - Funções auxiliares para gerenciamento de arquivos
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """Gerenciador centralizado de arquivos da aplicação"""
    
    @staticmethod
    def save_json(file_path: str, data: Dict[str, Any]) -> bool:
        """
        Salva dados em arquivo JSON.
        
        Args:
            file_path: Caminho do arquivo
            data: Dados a serem salvos
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Arquivo JSON salvo: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar JSON {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        Carrega dados de arquivo JSON.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            dict: Dados carregados ou dicionário vazio
        """
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Arquivo JSON não encontrado: {file_path}")
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar JSON {file_path}: {str(e)}")
            return {}
    
    @staticmethod
    def append_to_file(file_path: str, content: str) -> bool:
        """
        Adiciona conteúdo ao final de um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo a adicionar
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content + "\n")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar ao arquivo {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def save_video_record(video_title: str, video_url: str, config) -> bool:
        """
        Registra um vídeo publicado no arquivo videos_publicados.txt.
        
        Args:
            video_title: Título do vídeo
            video_url: URL do vídeo no YouTube
            config: Configuração da aplicação
            
        Returns:
            bool: True se sucesso
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = f"[{timestamp}] {video_title} | {video_url}"
        video_log_path = os.path.join(config.data_dir, "videos_publicados.txt")
        return FileManager.append_to_file(video_log_path, record)
    
    @staticmethod
    def get_video_records(config) -> List[str]:
        """
        Obtém todos os registros de vídeos publicados.
        
        Args:
            config: Configuração da aplicação
            
        Returns:
            list: Lista de registros
        """
        video_log_path = os.path.join(config.data_dir, "videos_publicados.txt")
        try:
            if os.path.exists(video_log_path):
                with open(video_log_path, 'r', encoding='utf-8') as f:
                    return f.readlines()
        except Exception as e:
            logger.error(f"Erro ao ler registros de vídeos: {str(e)}")
        return []


def get_file_manager() -> FileManager:
    """Função helper para obter o gerenciador de arquivos"""
    return FileManager()
