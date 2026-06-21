### **MOC: Redes AWS**

Os serviços de rede da AWS fornecem a infraestrutura necessária para isolar recursos, rotear o tráfego de internet global de forma otimizada e conectar data centers locais de forma segura à nuvem.

### 🌐 Isolamento e Infraestrutura de Rede

- **[[Amazon VPC]]**: O pilar fundamental de rede na nuvem (Virtual Private Cloud). Permite provisionar uma seção isolada logicamente da nuvem AWS, onde você tem controle total sobre o ambiente de rede virtual, incluindo seleção de intervalos de endereços IP, criação de sub-redes e configuração de tabelas de roteamento e gateways.
    

### 🗺️ Roteamento e Conectividade Híbrida

- **[[Amazon Route 53]]**: Um serviço de DNS (Domain Name System) em nuvem altamente disponível e escalável. Ele traduz nomes de domínio legíveis por humanos (como `ai-dev-stack.com`) em endereços IP numéricos e gerencia políticas de roteamento globais para direcionar os usuários aos recursos corretos.
    
- **[[AWS Direct Connect]]**: A solução padrão para arquiteturas de **nuvem híbrida**. Ele cria uma conexão de rede dedicada e privada entre o seu datacenter físico (On-premises) e a AWS, contornando a internet pública para fornecer maior largura de banda, latência mais baixa e maior consistência de rede.
    

#AWS/Redes