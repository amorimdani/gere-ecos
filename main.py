"""
Main Entry Point - Fábrica de Vídeos Autônoma
Inicializa a aplicação e executa a interface Streamlit
"""

import sys
import os
from pathlib import Path

# Adiciona diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import Config
from src.config.logger import get_logger

logger = get_logger(__name__)


def main():
    """Função principal"""
    try:
        logger.info("=" * 80)
        logger.info("🎥 Fábrica de Vídeos Autônoma - Ecos de Sabedoria")
        logger.info("=" * 80)
        
        # Carrega configurações
        config = Config()
        logger.info(f"Configurações carregadas de: {config.base_dir}")
        
        # Valida credenciais
        credentials = config.validate_credentials()
        logger.info(f"Status das credenciais: {credentials}")
        
        # Inicia interface Streamlit
        logger.info("Iniciando interface Streamlit...")
        import subprocess
        app_path = os.path.join(config.src_dir, "ui", "streamlit_app.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
        
    except Exception as e:
        logger.error(f"Erro ao iniciar aplicação: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
