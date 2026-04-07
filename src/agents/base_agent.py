"""
Base Agent - Classe base para todos os agentes
Define interface comum e tratamento de erros
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from config.logger import get_logger


class AgentStatus(Enum):
    """Estados possíveis de um agente"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class BaseAgent(ABC):
    """
    Classe base abstrata para todos os agentes da aplicação.
    Define interface comum, retry logic e tratamento de erros.
    """
    
    def __init__(self, agent_name: str = None, max_retries: int = 3, name: str = None):
        """
        Inicializa o agente base.
        
        Args:
            agent_name: Nome do agente para logging (novo parâmetro padrão)
            name: Alias legado para agent_name (mantido p/ compatibilidade)
            max_retries: Número máximo de tentativas
        """
        # Suporte retrocompatível: se "name" for usado, prioriza-o
        if agent_name is None and name is not None:
            agent_name = name
        
        self.agent_name = agent_name or self.__class__.__name__
        self.max_retries = max_retries
        self.config = Config()
        self.logger = get_logger(f"agent.{self.agent_name}")
        self.status = AgentStatus.IDLE
        self.last_error: Optional[str] = None
        self.execution_start: Optional[datetime] = None
    
    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a lógica do agente.
        
        Args:
            payload: Dados de entrada para o agente
            
        Returns:
            dict: Resultado da execução
        """
        pass
    
    async def run(self, payload: Dict[str, Any], 
                  use_retry: bool = True) -> Dict[str, Any]:
        """
        Executa o agente com retry automático.
        
        Args:
            payload: Dados de entrada
            use_retry: Se deve usar sistema de retry
            
        Returns:
            dict: Resultado da execução
        """
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                self.status = AgentStatus.RUNNING
                self.execution_start = datetime.now()
                self.logger.info(f"Iniciando execução (tentativa {attempt + 1}/{self.max_retries})")
                
                result = await self.execute(payload)
                
                self.status = AgentStatus.SUCCESS
                execution_time = (datetime.now() - self.execution_start).total_seconds()
                self.logger.info(f"Execução concluída com sucesso em {execution_time:.2f}s")
                
                return {
                    "success": True,
                    "data": result,
                    "agent": self.agent_name,
                    "attempt": attempt + 1,
                    "execution_time": execution_time
                }
                
            except Exception as e:
                last_error = str(e)
                self.last_error = last_error
                attempt += 1
                
                if attempt < self.max_retries and use_retry:
                    self.status = AgentStatus.RETRYING
                    self.logger.warning(
                        f"Erro na tentativa {attempt}: {last_error}. "
                        f"Tentando novamente em {attempt * 2} segundos..."
                    )
                    await asyncio.sleep(attempt * 2)  # Backoff exponencial
                else:
                    self.status = AgentStatus.FAILED
                    self.logger.error(
                        f"Falha permanente após {attempt} tentativas: {last_error}"
                    )
                    return {
                        "success": False,
                        "error": last_error,
                        "agent": self.agent_name,
                        "attempt": attempt
                    }
        
        return {
            "success": False,
            "error": last_error,
            "agent": self.agent_name,
            "attempt": self.max_retries
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do agente"""
        return {
            "agent": self.agent_name,
            "status": self.status.value,
            "last_error": self.last_error,
            "execution_start": self.execution_start.isoformat() if self.execution_start else None
        }
    
    def log_info(self, message: str):
        """Log de informação"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log de aviso"""
        self.logger.warning(message)
    
    def log_error(self, message: str, exc_info=False):
        """Log de erro"""
        self.logger.error(message, exc_info=exc_info)
