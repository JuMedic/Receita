"""
Ponto de entrada principal do sistema.
"""
import asyncio
import signal
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import config
from src.utils.logger import app_logger
from src.orchestrator.system_orchestrator import SystemOrchestrator


async def main():
    """Função principal"""
    orchestrator = SystemOrchestrator()
    
    # Handlers de sinal para shutdown gracioso
    def signal_handler(sig, frame):
        app_logger.info(f"Sinal recebido: {sig}")
        asyncio.create_task(orchestrator.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await orchestrator.start()
    except Exception as e:
        app_logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        app_logger.info("Sistema interrompido")
    except Exception as e:
        app_logger.error(f"Erro ao iniciar: {e}", exc_info=True)
        sys.exit(1)
