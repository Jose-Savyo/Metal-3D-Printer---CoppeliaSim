# scripts/console_cnc.py
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

print("🔌 Inicializando console de controle...")

# 1. Conexão e Setup
client = RemoteAPIClient()
sim = client.require('sim')

# Mapeamento (Atualize com seus nomes REAIS do Coppelia)
juntas = {
    'x': sim.getObject('/JuntaX'),
    'y': sim.getObject('/JuntaY'),
    'z': sim.getObject('/JuntaZ')
}

def mv(eixo, pos_mm):
    """
    Comando curto para mover. Ex: mv('x', 150)
    """
    if eixo not in juntas:
        print(f"Eixo '{eixo}' inválido. Use: x, y, z")
        return
    
    # Converte mm para metros
    pos_m = pos_mm / 1000.0
    sim.setJointTargetPosition(juntas[eixo], pos_m)
    print(f"🚀 {eixo.upper()} -> {pos_mm}mm")

def vel(eixo, valor_ms):
    """Ajusta a velocidade máxima (m/s)"""
    if eixo in juntas:
        sim.setObjectFloatParam(juntas[eixo], sim.jointfloatparam_upper_limit, valor_ms)
        print(f"⚡ Velocidade {eixo.upper()} ajustada: {valor_ms} m/s")

def start():
    sim.startSimulation()
    print("▶️ Simulação ON")

def stop():
    sim.stopSimulation()
    print("⏹️ Simulação OFF")

# Inicia automaticamente a física ao rodar
start()
print("\n✅ Console Pronto! Comandos disponíveis:")
print("   mv('x', 100)  -> Move X para 100mm")
print("   mv('y', 50)   -> Move Y para 50mm")
print("   stop()        -> Para a simulação")