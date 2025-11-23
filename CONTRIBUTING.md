# Como Contribuir para o JC Online

Obrigado por se interessar em contribuir para o JC Online.  
Este é um projeto acadêmico e sua colaboração é muito bem-vinda.  
Siga este guia para configurar seu ambiente e participar do desenvolvimento.

---

## 1. Código de Conduta

- Mantenha sempre o respeito ao interagir em issues e pull requests.
- Críticas devem ser construtivas e objetivas.
- Não será tolerado qualquer comportamento ofensivo ou discriminatório.

---

## 2. Pré-requisitos

Antes de começar, instale:

- Git: https://git-scm.com/downloads  
- Python 3.10 ou superior: https://www.python.org/downloads  
- IDE recomendada: VS Code ou PyCharm

---

## 3. Clonando o Repositório

```bash
git clone https://github.com/RafaelLc-DEV/jc-projetos2.git
cd jc-projetos2
4. Criando e Ativando o Ambiente Virtual
Windows
bash
Copiar código
python -m venv venv
.\venv\Scripts\activate
Linux / macOS
bash
Copiar código
python3 -m venv venv
source venv/bin/activate
5. Instalando Dependências
Com o ambiente virtual ativo:

bash
Copiar código
pip install -r requirements.txt
6. Banco de Dados e Execução do Projeto
Aplique as migrações e inicie o servidor:

bash
Copiar código
python manage.py migrate
python manage.py createsuperuser   # opcional
python manage.py runserver
Acesse no navegador:

cpp
Copiar código
http://127.0.0.1:8000
7. Como Contribuir
Crie uma branch para sua funcionalidade:

bash
Copiar código
git checkout -b minha-feature
Faça commits claros e objetivos.

Envie sua branch:

bash
Copiar código
git push origin minha-feature
Abra um Pull Request explicando suas alterações.