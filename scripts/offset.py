import sys
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

# ==========================================
# CLASSE DO CONTROLADOR (O Cérebro)
# ==========================================
class ControladorCNC:
    def __init__(self):
        print("Conectando ao CoppeliaSim...")
        self.client = RemoteAPIClient()
        self.sim = self.client.require('sim')
        
        # Mapa de Juntas
        self.mapa = {
            'x': '/eixoX', 
            'y': '/eixoY', 
            'z': '/eixoZ'
        }

        self.handles = {}
        
        # MEMÓRIA DE OFFSETS (Começa tudo zerado)
        self.offsets = {
            'x': 0.0, 
            'y': 0.0, 
            'z': 0.0
        }

        # Conexão e busca de handles
        try:
            for eixo, nome in self.mapa.items():
                self.handles[eixo] = self.sim.getObject(nome)
            print("✅ Conexão OK! Juntas encontradas.")
        except Exception as e:
            print(f"Erro Crítico: {e}")
            sys.exit()

    def ler_posicao_real_maquina(self, eixo):
        """Lê o sensor direto do Coppelia (Valor Absoluto)"""
        return self.sim.getJointPosition(self.handles[eixo])

    def zerar_eixo(self, eixo):
        """Define a posição ATUAL como o novo Zero"""
        if eixo not in self.handles: return
        
        # 1. Onde estou agora de verdade?
        pos_real = self.ler_posicao_real_maquina(eixo)
        
        # 2. Salvo essa posição como a minha 'Tara' (Offset)
        self.offsets[eixo] = pos_real
        
        print(f"   [DEBUG] Eixo {eixo.upper()} Zerado!")
        print(f"   [DEBUG] Zero Máquina: {pos_real:.4f}m")
        print(f"   [DEBUG] Novo Offset salvo: {self.offsets[eixo]:.4f}m")

    def mover(self, eixo, valor_usuario_mm):
        """Recebe valor em mm (Trabalho) e move o motor (Máquina)"""
        if eixo not in self.handles: return

        # 1. Converter entrada para metros
        alvo_trabalho_m = valor_usuario_mm / 1000.0
        
        # 2. MATEMÁTICA DO WCS
        # Posição Motor = Onde o usuário quer ir + A Tara (Offset)
        offset_atual = self.offsets[eixo]
        alvo_motor_m = alvo_trabalho_m + offset_atual

        # 3. DEBUG (Para você ver a conta acontecendo)
        print(f"   [CALCULO] Usuário pede: {valor_usuario_mm}mm")
        print(f"   [CALCULO] Offset atual: {offset_atual*1000:.1f}mm")
        print(f"   [CALCULO] Enviando p/ Motor: {alvo_motor_m*1000:.1f}mm (Absoluto)")

        # 4. Envia comando
        self.sim.setJointTargetPosition(self.handles[eixo], alvo_motor_m)

    def get_texto_display(self):
        """Gera o texto do prompt com as coordenadas corrigidas"""
        txt = ""
        for eixo in ['x', 'y', 'z']:
            # Pega posição real
            pos_real = self.ler_posicao_real_maquina(eixo)
            # Subtrai o offset para mostrar ao usuário
            pos_display = (pos_real - self.offsets[eixo]) * 1000.0
            txt += f"{eixo.upper()}:{pos_display:.1f} "
        return txt

# ==========================================
# LOOP PRINCIPAL
# ==========================================
def main():
    cnc = ControladorCNC()
    cnc.sim.startSimulation()
    
    print("\n--- CNC SYSTEM READY ---")
    print("Comandos: x 100, y 50, z 10")
    print("Comandos: zero x (zera o eixo x)")
    print("Comandos: zero tudo (zera todos)")
    
    while True:
        try:
            # Mostra posição baseada no offset atual
            prompt = f"\n[{cnc.get_texto_display()}] > "
            entrada = input(prompt).strip().lower()

            if entrada == 'q': break
            
            partes = entrada.split()
            if len(partes) < 2: continue

            cmd, param = partes[0], partes[1]

            # --- COMANDO ZERO ---
            if cmd == 'zero':
                if param == 'tudo':
                    for e in ['x', 'y', 'z']: cnc.zerar_eixo(e)
                elif param in ['x', 'y', 'z']:
                    cnc.zerar_eixo(param)
                else:
                    print("⚠️ Eixo inválido para zerar.")
                continue

            # --- COMANDO MOVER ---
            if cmd in ['x', 'y', 'z']:
                try:
                    valor = float(param)
                    cnc.mover(cmd, valor)
                    time.sleep(0.1) # Breve pausa para o motor reagir
                except ValueError:
                    print("Valor numérico inválido.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro: {e}")

    cnc.sim.stopSimulation()

if __name__ == "__main__":
    main()