import random
import time
import psutil
import cProfile
import pstats
import os
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

def gerar_numeros_aleatorios(parte, num_numeros, valor_maximo, arquivo_final):
    """Função para gerar números aleatórios e adicioná-los ao arquivo compartilhado."""
    with open(arquivo_final, 'a') as arquivo:
        for _ in range(num_numeros):
            numero = random.randint(0, valor_maximo)
            arquivo.write(f"{numero}\n")

def main():
    # Define o nome do arquivo de saída
    nome_do_arquivo = 'numeros_aleatorios_0_a_1M.txt'
    
    # Remove o arquivo anterior se existir, para começar um novo
    if os.path.exists(nome_do_arquivo):
        os.remove(nome_do_arquivo)
    
    total_numeros = 1000000  # 1 Milhão de números
    valor_maximo  = 1000000  # Máximo valor para números aleatórios
    num_workers = 5  # Usar metade dos núcleos do processador

    # Medir o tempo de execução da geração
    inicio = time.time()

    # Dividir o trabalho entre os workers
    numeros_por_worker = total_numeros // num_workers

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        executor.map(
            gerar_numeros_aleatorios,
            range(num_workers),
            [numeros_por_worker] * num_workers,
            [valor_maximo] * num_workers,
            [nome_do_arquivo] * num_workers
        )

    fim = time.time()
    tempo_gasto = fim - inicio

    # Medir uso de CPU e RAM
    processo = psutil.Process()
    uso_cpu = processo.cpu_percent(interval=None)
    uso_memoria = processo.memory_info().rss / (1024 * 1024 * 1024)  # Convertendo para GB


    print(f"Arquivo '{nome_do_arquivo}' criado com sucesso.")
    
    # Exibição das métricas
    print("\n=== Métricas de Execução ===")
    print(f"Tempo de criação: {tempo_gasto:.6f} segundos")
    print(f"Número de núcleos utilizados: {num_workers}")
    print(f"Uso de CPU durante criação: {uso_cpu:.2f}%")
    print(f"Consumo de RAM durante criação: {uso_memoria:.6f} GB","\n")

# Executando o profiling com cProfile
if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
