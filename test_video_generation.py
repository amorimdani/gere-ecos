#!/usr/bin/env python
"""Teste rápido de geração de vídeo - para desenvolvimento"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents import create_orchestrator_agent
from config.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Testa geração de vídeo"""
    
    print("\n" + "="*70)
    print("🎬 TESTE DE GERAÇÃO DE VÍDEO")
    print("="*70)
    
    try:
        print("\n📍 Criando OrchestratorAgent...")
        orchestrator = await create_orchestrator_agent()
        print("✅ OrchestratorAgent criado")
        
        print("\n📍 Executando pipeline completo...")
        print("   (Content → Audio → Visual → Editor)")
        
        result = await orchestrator.execute({
            "action": "run_once",
            "theme": "estoicismo",
            "publish": False  # Apenas teste, sem publicar
        })
        
        if result["success"]:
            duration = result["data"].get("duration_seconds", 0)
            print(f"\n✅ SUCESSO! Vídeo gerado em {duration:.0f}s")
            print(f"   Arquivo salvo em: output/")
            
            # Listar arquivos
            output_dir = Path("output")
            if output_dir.exists():
                files = list(output_dir.glob("*.mp4"))
                if files:
                    print(f"\n📂 Arquivos gerados:")
                    for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                        size_mb = f.stat().st_size / 1024 / 1024
                        print(f"   • {f.name} ({size_mb:.1f} MB)")
        else:
            print(f"\n❌ ERRO: {result['error']}")
            print(f"   Stages completados: {len(result['data'].get('cycle_data', {}).get('stages', {}))}")
    
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(main())
