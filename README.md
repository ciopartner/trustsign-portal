Projeto Portal & e-commerce da TrustSign

Passos para configurar o ambiente de desenvolvimento:
1) Configurar o arquivo hosts. Entradas:
# Projeto TrustSign Portal
127.0.0.1       www.trustdev.com.br
127.0.0.1       ecommerce.trustdev.com.br

2) Criar o banco de dados:
./manage.py syncdb
./manage.py migrate
Executar uma vez para o portal e outra para o e-commerce

3) Entrar no Portal e criar o SITE com ID=2 para o e-commerce

4) Configurar o banco de dados:
  - Configurações do banco em settings_global.py
  - Configuração do roteamento do banco em routes.py
  - routes.py comentado em MIDDLEWARE_CLASSES
  - routes.py comentado em DATABASE_ROUTERS em settings_global
  - routes.py comentado por causa de bug no django 1.4.5

5) Setar a variável de ambiente TRUSTSIGN_ENVIRONMENT para
  - DEV
  - QAS
  - PRD

6) Dependências:
# apt-get install libncurses5-dev
# apt-get install python-dev
# apt-get install libssl-dev