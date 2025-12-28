import sys
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

print("Conectando ao CoppeliaSim...")
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
# Variaveis auxiliares para a funcao de offset
WORK_OFFSETS = {
    'x': 0.0,
    'y': 0.0,
    'z': 0.0
}

def zerar_eixo(eixo):
    """
    Define a posição ATUAL do robô como o novo Zero (0.0) para aquele eixo.
    """
    if eixo not in handles:
        print(f"Eixo {eixo} invalido.")
        return

    # 1. Ler a posição absoluta atual do motor (MCS)
    pos_absoluta = sim.getJointPosition(handles[eixo])
    
    # 2. Salvar como offset
    WORK_OFFSETS[eixo] = pos_absoluta
    
    print(f"Eixo {eixo.upper()} zerado! (Offset salvo: {pos_absoluta*1000:.2f} mm)")

def zerar_tudo():
    """Zera X, Y e Z na posição atual"""
    for eixo in ['x', 'y', 'z']:
        zerar_eixo(eixo)

def mover_para_posicao_trabalho(eixo, valor_mm):
    """
    Recebe um comando em coordenadas de trabalho (WCS) e move o robô.
    """
    if eixo not in handles: return

    # 1. Converter mm para metros
    valor_m = valor_mm / 1000.0
    
    # 2. Aplicar o Offset (Matemática: Posição Máquina = Posição Desejada + Offset)
    posicao_real_coppelia = valor_m + WORK_OFFSETS[eixo]
    
    # 3. Enviar para o motor
    sim.setJointTargetPosition(handles[eixo], posicao_real_coppelia)

# Obtendo os handles (IDs)
handles = {}
try:
    for eixo, nome in mapa_juntas.items():
        # Tenta pegar pelo caminho completo ou pelo alias
        handles[eixo] = sim.getObject(nome)
    print("Juntas encontradas com sucesso.")
except Exception as e:
    print(f"Erro ao buscar juntas: {e}")
    sys.exit()

def ler_status_completo():
    status_str = ""
    for eixo in ['x', 'y', 'z']:
        # Leitura crua do sensor (Absoluta / Máquina)
        pos_abs_m = sim.getJointPosition(handles[eixo])
        
        # Cálculo da posição relativa (Trabalho)
        # Trabalho = Absoluto - Offset
        pos_trab_m = pos_abs_m - WORK_OFFSETS[eixo]
        
        # Formatação
        status_str += f"{eixo.upper()}: {pos_trab_m*1000:.1f} (Abs: {pos_abs_m*1000:.1f}) | "
    
    return status_str

def loop_principal():
    sim.startSimulation()
    print("\n--- TERMINAL CNC v2.0 ---")
    print("Comandos: [eixo] [valor_mm]  (Ex: x 100)")
    print("          'home' para zerar tudo")
    print("          'zero' para zerar um eixo")
    print("          'q' para sair")

    while True:
        try:
            # 1. Lê posições atuais
            pos = ler_status_completo()
            
            # 2. Cria o texto do prompt com as posições
            # Ex: [X: 100.0 | Y: 50.5 | Z: 0.0] > 
            #prompt_texto = f"\n[X:{pos['x']:.1f} | Y:{pos['y']:.1f} | Z:{pos['z']:.1f}] > "
            prompt_texto = "gCode > "

            # 3. Aguarda comando
            comando = input(prompt_texto).strip().lower()
            
            # --- Processamento dos Comandos ---
            if comando == 'q':
                break

            if comando == 'zero':
                e = input("Qual eixo zerar? (x, y, z ou 'tudo'): ").strip().lower()
                if e == 'tudo':
                    for ax in ['x', 'y', 'z']: zerar_eixo(ax)
                else:
                    zerar_eixo(e)
                continue

            
            if comando == 'home':
                print("Indo para Home...")
                for h in handles.values():
                    sim.setJointTargetPosition(h, 0.0)
                continue

            partes = comando.split()
            
            # Validação simples
            if len(partes) != 2:
                print("Formato inválido. Tente: x 150")
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
                print(f"Eixo '{eixo_cmd}' não existe.")

        except ValueError:
            print("Digite um número válido.")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro de comunicação: {e}")

    sim.stopSimulation()
    print("Encerrando conexão...")

if __name__ == "__main__":
    loop_principal()