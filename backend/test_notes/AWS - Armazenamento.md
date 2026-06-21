### **MOC: Armazenamento e Dados AWS**

A AWS divide a persistência de dados em três grandes pilares: armazenamento de arquivos/blocos para sistemas operacionais, bancos de dados gerenciados (relacionais e NoSQL) e soluções de análise de dados em larga escala.

### 💾 Armazenamento de Arquivos e Volumes (Storage)

Soluções de persistência direta para sistemas operacionais e aplicações estruturadas:

- **[[Amazon S3]]**: Armazenamento de objetos em escala global com altíssima durabilidade e disponibilidade. Ideal para arquivos estáticos, backups, mídias e data lakes.
    
- **[[Amazon EBS]]**: Volumes de bloco persistentes e de alta performance projetados para uso exclusivo com uma única instância **[[Amazon EC2]]** (funciona como o "HD/SSD interno" do servidor).
    
- **[[Amazon EFS]]**: Sistema de arquivos gerenciado, elástico e compartilhado. Permite que centenas de instâncias EC2 acessem simultaneamente os mesmos arquivos de forma concorrente.
    

### 🗄️ Bancos de Dados Gerenciados (Databases)

Ambientes otimizados para transações, consultas e persistência estruturada de dados:

- **[[Amazon RDS]]**: Serviço gerenciado para bancos de dados relacionais (SQL). Suporta motores tradicionais como PostgreSQL, MySQL e Oracle, cuidando de patches, backups e alta disponibilidade.
    
- **[[Amazon DynamoDB]]**: Banco de dados NoSQL de chave-valor totalmente gerenciado (Serverless). Projetado para oferecer latência de milissegundo de um dígito em qualquer escala de tráfego.
    

### 📊 Analytics e Migração de Dados

Ferramentas para movimentação e análise massiva de informações corporativas:

- **[[Amazon Redshift]]**: Um Data Warehouse corporativo de alta performance baseado em armazenamento colunar. Ideal para análises complexas de Big Data e Business Intelligence (BI).
    
- **[[Amazon DMS]]**: O _Database Migration Service_. Permite migrar bancos de dados para a AWS de forma contínua e com segurança, mantendo a origem totalmente ativa durante o processo de replicação.
    

#AWS/Armazenamento