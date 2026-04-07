"""
Módulo de Logger - Sistema centralizado de logging
Implementa logging em arquivo e console com níveis configuráveis
"""

import logging
import os
from datetime import datetime
from typing import Optional
from .config import Config


class Logger:
    """
    Classe para gerenciar logging da aplicação.
    Implementa logging em arquivo e console simultaneamente.
    """
    
    _instance: Optional["Logger"] = None
    _loggers: dict = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.config = Config()
        self.log_level = getattr(logging, self.config.app.log_level, logging.INFO)
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Configura o logger raiz da aplicação"""
        import sys
        
        root_logger = logging.getLogger()
        
        # Evita re-inicialização com handlers duplicados
        if root_logger.hasHandlers() and any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
            return
        
        # Limpa handlers existentes para evitar duplicação
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Desabilita propagação entre loggers para evitar logs duplicados
        root_logger.propagate = False
        
        # Cria handlers
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Tenta forçar UTF-8 no console
        if hasattr(console_handler, 'setEncoding'):
            console_handler.setEncoding('utf-8')
        
        file_handler = logging.FileHandler(
            os.path.join(self.config.logs_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log"),
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        root_logger.setLevel(self.log_level)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Obtém ou cria um logger específico para um módulo.
        
        Args:
            name: Nome do módulo (geralmente __name__)
            
        Returns:
            logging.Logger: Logger configurado
        """
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]
    
    @staticmethod
    def get() -> logging.Logger:
        """Retorna o logger raiz"""
        return logging.getLogger()


def get_logger(name: str) -> logging.Logger:
    """Função helper para obter logger facilmente"""
    return Logger().get_logger(name)
