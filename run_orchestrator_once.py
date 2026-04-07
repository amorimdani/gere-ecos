#!/usr/bin/env python
"""Roda um ciclo completo da Fábrica de Vídeos (sem publicar)."""

import sys
import asyncio
from pathlib import Path

# Garantir que src esteja no path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents import create_orchestrator_agent  # type: ignore


async def main():
    orchestrator = await create_orchestrator_agent()
    result = await orchestrator.execute({
        "action": "run_once",
        "theme": "estoicismo",
        "publish": False,
    })
    print("\n===== RESULTADO DO CICLO =====")
    print("success:", result.get("success"))
    print("error:", result.get("error"))
    data = result.get("data", {}) or {}
    print("video_path:", data.get("video_path") or data.get("video_file"))
    print("provider:", data.get("provider") or data.get("llm_provider"))
    print("==============================\n")


if __name__ == "__main__":
    asyncio.run(main())
