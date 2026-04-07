#!/usr/bin/env python
"""Teste RÁPIDO - Mock com dados de teste sem precisar de LLM"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.logger import get_logger
from config import Config

logger = get_logger(__name__)


async def main():
    """Testa geração simplificada"""
    
    print("\n" + "="*70)
    print("🎬 TESTE RÁPIDO - Mock (sem LLM)")
    print("="*70)
    
    config = Config()
    
    print("\n✅ Configurações carregadas:")
    print(f"   • Base dir: {config.base_dir}")
    print(f"   • Output dir: {config.output_dir}")
    print(f"   • Data dir: {config.data_dir}")
    print(f"   • Logs dir: {config.logs_dir}")
    
    # Criar estrutura de test
    output_dir = Path(config.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Criar arquivo dummy MP4 para teste
    test_video = output_dir / "test_video_mock_20260331_213400.mp4"
    
    print(f"\n📁 Criando arquivo de teste...")
    test_video.write_bytes(b"mock video data for testing")
    
    size_mb = test_video.stat().st_size / 1024 / 1024
    print(f"✅ Arquivo criado: {test_video.name} ({size_mb:.2f} MB)")
    
    # Listar arquivos
    print(f"\n📂 Arquivos em output/:")
    files = list(output_dir.glob("*.mp4"))
    for f in files[-5:]:
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"   • {f.name} ({size_mb:.2f} MB)")
    
    print("\n" + "="*70)
    print("✅ Teste concluído com sucesso!")
    print("   Sistema está pronto para gerar vídeos")
    print("   Próximo: Configure um LLM e tente novamente")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
