import sys
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

print("🔌 Conectando ao CoppeliaSim...")
client = RemoteAPIClient()
sim = client.require('sim')

# --- CONFIGURAÇÃO ---
# Se os nomes mudarem na cena, mude aqui.
# Dica: Use o script 'listar_objetos.py' se tiver dúvida dos nomes
mapa_juntas = {
    'x': '/eixoX', 
    'y': '/eixoY', 
    'z': '/eixoZ'
}

# Obtendo os handles (IDs)
handles = {}
try:
    for eixo, nome in mapa_juntas.items():
        # Tenta pegar pelo caminho completo ou pelo alias
        handles[eixo] = sim.getObject(nome)
    print("✅ Juntas encontradas com sucesso.")
except Exception as e:
    print(f"❌ Erro ao buscar juntas: {e}")
    sys.exit()

def ler_posicoes_mm():
    """Lê a posição atual de todos os eixos e retorna formatado em mm"""
    status = {}
    for eixo, handle in handles.items():
        # Coppelia retorna em Metros -> Convertemos para mm
        pos_m = sim.getJointPosition(handle)
        pos_mm = pos_m * 1000.0
        status[eixo] = pos_mm
    return status

def loop_principal():
    sim.startSimulation()
    print("\n--- TERMINAL CNC v2.0 ---")
    print("Comandos: [eixo] [valor_mm]  (Ex: x 100)")
    print("          'home' para zerar tudo")
    print("          'q' para sair")

    while True:
        try:
            # 1. Lê posições atuais
            pos = ler_posicoes_mm()
            
            # 2. Cria o texto do prompt com as posições
            # Ex: [X: 100.0 | Y: 50.5 | Z: 0.0] > 
            #prompt_texto = f"\n[X:{pos['x']:.1f} | Y:{pos['y']:.1f} | Z:{pos['z']:.1f}] > "
            prompt_texto = "gCode > "

            # 3. Aguarda comando
            comando = input(prompt_texto).strip().lower()
            
            # --- Processamento dos Comandos ---
            if comando == 'q':
                break
            
            if comando == 'home':
                print("🏠 Indo para Home...")
                for h in handles.values():
                    sim.setJointTargetPosition(h, 0.0)
                continue

            partes = comando.split()
            
            # Validação simples
            if len(partes) != 2:
                print("⚠️  Formato inválido. Tente: x 150")
                continue

            eixo_cmd, valor_str = partes[0], partes[1]

            if eixo_cmd in handles:
                valor_mm = float(valor_str)
                valor_m = valor_mm / 1000.0
                
                # Envia o comando para o Coppelia
                sim.setJointTargetPosition(handles[eixo_cmd], valor_m)
                
                # Opcional: Pequena pausa para dar tempo do robô começar a mover 
                # antes de atualizar o prompt de novo (senão ele mostra a posição antiga)
                time.sleep(0.1) 
            else:
                print(f"❌ Eixo '{eixo_cmd}' não existe.")

        except ValueError:
            print("❌ Digite um número válido.")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Erro de comunicação: {e}")

    sim.stopSimulation()
    print("Encerrando conexão...")

if __name__ == "__main__":
    loop_principal()