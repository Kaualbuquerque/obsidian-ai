### **MOC: Segurança AWS**

A segurança na AWS opera sob o Modelo de Responsabilidade Compartilhada. Esta nota centraliza os mecanismos de governança de contas, gerenciamento de identidades e proteção de rede para blindar a infraestrutura.

### 🆔 Governança e Controle de Acesso Global

- **[[AWS IAM]]**: O pilar de Identity and Access Management. Controla de forma global a autenticação e autorização (quem pode acessar o quê) na conta através de Usuários, Grupos, Funções (Roles) e Políticas JSON baseadas no Princípio do Menor Privilégio.
    
- **[[AWS Organizations]]**: Serviço de gerenciamento centralizado para governar múltiplas contas AWS. Permite consolidar o faturamento, criar contas programaticamente e aplicar restrições máximas de segurança através de SCPs (Service Control Policies) em Unidades Organizacionais (OUs).
    

### 🛡️ Segurança de Rede e Perímetro

A proteção dos recursos internos (como servidores virtuais e bancos de dados) dentro de uma VPC é feita através de duas camadas complementares de firewall:

- **[[Security Groups]]**: Funcionam como um firewall virtual **com estado (stateful)** para controlar o tráfego de entrada e saída a nível de **instância** (ex: protegendo uma EC2 específica). Por padrão, bloqueiam toda a entrada e liberam toda a saída.
    
- **[[Network ACLs]]**: Funcionam como uma camada de segurança **sem estado (stateless)** a nível de **sub-rede**. Elas avaliam explicitamente regras de permissão (Allow) e negação (Deny) para todo o tráfego que cruza a fronteira da sub-rede, servindo como a primeira linha de defesa antes do tráfego chegar às instâncias.
    

#AWS/Segurança