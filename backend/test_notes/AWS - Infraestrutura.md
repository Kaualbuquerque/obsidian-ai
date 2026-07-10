---
tags: [AWS]
compromisso: 
date: 
---

# AWS - Infraestrutura

# AWS - Infraestrutura

### **MOC: Infraestrutura AWS**

A base para entender a nuvem da AWS está em como os recursos são distribuídos e entregues globalmente com alta disponibilidade, tolerância a falhas e baixa latência.

### 🧱 Conceitos Fundamentais

- **[[Cliente - Servidor]]**: O modelo arquitetural base que dita como as aplicações modernas interagem na nuvem, onde o cliente solicita recursos e processamento sob demanda para os servidores da AWS.
    
- **[[Implatanção da Computação em Nuvem]]**: Define as três estratégias de arquitetura para a entrega de recursos de TI:
    
    - **Nuvem Pública**: Totalmente gerenciada e operada pela AWS.
        
    - **Nuvem Híbrida**: Conecta a infraestrutura local (On-premises) com os recursos da nuvem.
        
    - **Nuvem Privada**: Recursos de computação utilizados exclusivamente por uma única empresa, operados localmente.
        

### 🌍 Arquitetura Física e Geográfica

Todo o ecossistema de serviços da AWS depende de sua robusta **[[Infraestrutura global]]**, que é segmentada hierarquicamente para garantir resiliência máxima:

1. **[[Regiões]]**: Áreas geográficas isoladas ao redor do mundo que contêm múltiplos datacenters. Elas permitem a conformidade com leis locais de dados e redução de latência.
    
2. **[[Zonas de disponibilidade]]**: Subdivisões de uma Região, compostas por um ou mais datacenters físicos discretos com energia, infraestrutura e conectividade redundantes. São projetadas para isolamento de falhas.
    
3. **[[Locais de borda]]**: Pontos de presença distribuídos globalmente, utilizados por serviços de rede para entregar conteúdo aos usuários finais com a menor latência possível.
    

#AWS/Infraestrutura