import random
import time
import psutil
import cProfile
import pstats
import os
from concurrent.futures import ProcessPoolExecutor

def carregar_bloco_do_arquivo(nome_do_arquivo, inicio, tamanho_bloco):
    """Carrega um bloco do arquivo a partir de uma posição inicial especificada."""
    with open(nome_do_arquivo, 'r') as arquivo:
        arquivo.seek(inicio)
        bloco = []
        bytes_lidos = 0

        while bytes_lidos < tamanho_bloco:
            linha = arquivo.readline()
            if not linha:  # Fim do arquivo
                break
            if linha.strip():
                bloco.append(int(linha.strip()))
            bytes_lidos += len(linha)
    
    return bloco

def buscar_numero_parcial(numeros_parte, numero_buscado):
    """Busca o número em uma parte da lista."""
    return numero_buscado in numeros_parte

def processar_blocos(nome_do_arquivo, numero_buscado, num_workers, tamanho_bloco, max_ram_gb):
    """Processa o arquivo em blocos de até max_ram_gb GB em paralelo, mantendo métricas."""
    tamanho_arquivo = os.path.getsize(nome_do_arquivo)
    max_ram_bytes = max_ram_gb * 1024 * 1024 * 1024
    inicio = 0

    total_ram_usada = 0
    num_descartes = 0

    while inicio < tamanho_arquivo:
        # Determinar quantos blocos carregar para atingir o limite de RAM
        blocos = []
        ram_usada = 0

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futuros = []
            while ram_usada < max_ram_bytes and inicio < tamanho_arquivo:
                futuros.append(
                    executor.submit(carregar_bloco_do_arquivo, nome_do_arquivo, inicio, tamanho_bloco)
                )
                ram_usada += tamanho_bloco
                inicio += tamanho_bloco

            # Acumular a RAM usada
            total_ram_usada += ram_usada

            # Coletar resultados dos blocos carregados
            for futuro in futuros:
                blocos.append(futuro.result())
            
            # Realizar a busca nos blocos carregados
            resultados_busca = executor.map(buscar_numero_parcial, blocos, [numero_buscado] * len(blocos))
            if any(resultados_busca):
                return True, total_ram_usada, num_descartes, num_workers

            # Incrementar o contador de descartes de blocos
            num_descartes += 1

    return False, total_ram_usada, num_descartes, num_workers

def main():
    # Especifica o caminho do arquivo
    nome_do_arquivo = os.path.join("Com paralelismo", "1 T", "numeros_aleatorios_0_a_1T.txt")
    
    # Sorteio de um número aleatório entre 0 e 1 Trilhão
    numero_buscado = random.randint(0, 1000000000000)
    print(f"Buscando o número {numero_buscado}...")

    # Medir o tempo de execução da busca
    inicio = time.time()

    # Medir uso de CPU e RAM antes da busca
    processo = psutil.Process()
    uso_cpu_inicio = processo.cpu_percent(interval=None)
    uso_memoria_inicio = processo.memory_info().rss / (1024 * 1024 * 1024)  # Convertendo para GB

    # Configurações para o carregamento e busca
    num_workers = 25  # Utilizando múltiplos núcleos
    tamanho_bloco = 1024 * 1024 * 10  # Ler 10MB por vez
    max_ram_gb = 2  # Limite de 2GB de RAM

    encontrado, total_ram_usada, num_descartes, num_workers = processar_blocos(
        nome_do_arquivo, numero_buscado, num_workers, tamanho_bloco, max_ram_gb)

    # Medir uso de CPU e RAM após a busca
    uso_cpu_fim = processo.cpu_percent(interval=None)
    uso_memoria_fim = processo.memory_info().rss / (1024 * 1024 * 1024)  # Convertendo para GB

    fim = time.time()
    tempo_gasto = fim - inicio

    # Resultados da busca
    if encontrado:
        print(f"Número {numero_buscado} encontrado!")
    else:
        print(f"Número {numero_buscado} não encontrado.")
    
    # Exibição das métricas
    print("\n=== Métricas de Execução ===")
    print(f"Tempo de busca: {tempo_gasto:.6f} segundos")
    print(f"Número de núcleos utilizados: {num_workers}")
    print(f"Uso de CPU durante a busca: {uso_cpu_fim - uso_cpu_inicio:.2f}%")
    print(f"Consumo de RAM durante a busca: {uso_memoria_fim - uso_memoria_inicio:.6f} GB")
    print(f"Total de RAM acumulada usada: {total_ram_usada / (1024 * 1024 * 1024):.6f} GB")
    print(f"Número de vezes que blocos foram descartados: {num_descartes}","\n")

# Executando o profiling com cProfile
if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()