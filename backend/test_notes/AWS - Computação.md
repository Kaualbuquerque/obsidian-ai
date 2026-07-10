---
tags: [AWS]
compromisso: 
date: 
---

# AWS - Computação

# AWS - Computação

# AWS - Computação

### **MOC: Computação AWS**

A computação tradicional na AWS é baseada no fornecimento de poder de processamento sob demanda através de servidores virtuais flexíveis, que trabalham em conjunto com sistemas de balanceamento e alta disponibilidade.

### 💻 Servidores Virtuais e Infraestrutura Core

- **[[Amazon EC2]]**: O pilar central da computação tradicional (Elastic Compute Cloud). Permite provisionar e gerenciar servidores virtuais (instâncias) na nuvem em segundos, oferecendo controle total sobre o sistema operacional, armazenamento e configurações de rede.
    

### 📈 Escalabilidade e Alta Disponibilidade

Para garantir que a aplicação aguente picos de acesso sem desperdiçar dinheiro quando o tráfego estiver baixo, o EC2 depende de dois serviços complementares:

- **[[EC2 Auto Scaling]]**: Monitora continuamente suas aplicações e ajusta automaticamente o número de instâncias EC2 ativas (adicionando ou removendo servidores) de acordo com regras baseadas em métricas como uso de CPU ou tráfego de rede.
    
- **[[Elastic Load Balancing]]**: O balanceador de carga (ELB) distribui automaticamente o tráfego de entrada das aplicações entre múltiplos destinos, como várias instâncias EC2 ou contêineres, garantindo tolerância a falhas e alta disponibilidade através de diferentes **[[Zonas de disponibilidade]]**.
    

### ⚡ Computação Moderna e Serverless

Soluções que eliminam totalmente a necessidade de provisionar, gerenciar ou pagar por servidores ociosos:

- **[[AWS Lambda]]**: O coração do ecossistema Serverless. É um serviço de computação orientado a eventos que executa seu código de forma automática e elástica, cobrando estritamente pelos milissegundos de processamento utilizados.
    
- **[[Amazon API Gateway]]**: A porta de entrada para o mundo serverless. Funciona como um "roteador" ou gerenciador de APIs que recebe requisições HTTP públicas da internet e aciona diretamente as funções do **[[AWS Lambda]]** para processá-las, controlando tráfego e segurança no perímetro.

### 💰 Famílias e Modelos de Precificação

- **[[Tipos e Preços de instâncias]]**: O EC2 oferece uma matriz de opções baseada em duas frentes para otimizar a performance e o bolso:
    
    - **Famílias de Instâncias**: Otimizadas para diferentes cargas de trabalho (Ex: _General Purpose_ para servidores web gerais, _Compute Optimized_ para processamento pesado, _Memory Optimized_ para bancos de dados em memória).
        
    - **Modelos de Compra/Preço**: Estratégias de custo fundamentais (Ex: _On-Demand_ para flexibilidade total, _Reserved Instances_ / _Savings Plans_ para descontos de longo prazo com compromisso de uso, e _Spot Instances_ para usar capacidade ociosa da AWS com até 90% de desconto, ideal para tarefas tolerantes a falhas).