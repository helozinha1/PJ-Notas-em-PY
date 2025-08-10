# App de Notas 📚

Este é um sistema web simples para gerenciar alunos, turmas e as notas de seus projetos. O aplicativo permite que professores e administradores da escola mantenham um registro organizado do desempenho acadêmico dos alunos.

---

### Funcionalidades ✨

- **Gerenciamento de Alunos 🧑‍🎓**: Adicionar, visualizar, editar e remover alunos.
- **Gerenciamento de Turmas 🏫**: Criar, editar e remover turmas, e associar alunos a elas.
- **Gerenciamento de Notas 📝**: Adicionar e editar projetos com notas para cada aluno.
- **Cálculo de Média 📊**: A aplicação calcula e exibe a média geral de cada aluno.
- **Design Responsivo 📱**: A interface se adapta a diferentes tamanhos de tela, oferecendo uma experiência otimizada em desktops e celulares.

---

### Tecnologias Utilizadas 💻

**Frontend:**
- HTML
- CSS (com Bootstrap 5)
- JavaScript

**Backend:**
- Python (com o framework Flask)

**Banco de Dados:**
- SQLite (ou outro banco de dados compatível com Flask)

---

### Instalação e Execução ⚙️

Para rodar o projeto localmente, siga os passos abaixo:

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/helozinha1/PJ-Notas-em-PY.git
   cd PJ-Notas-em-PY
   ```

2. **Crie e ative um ambiente virtual (recomendado):**
   ```bash
   # No Windows
   python -m venv venv
   venv\Scripts\activate

   # No macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências do Python:**
   ```bash
   pip install Flask Flask-SQLAlchemy
   ```

4. **Inicialize o banco de dados e rode a aplicação:**
   ```bash
   flask run
   ```

5. **Acesse a aplicação:**  
   Abra seu navegador e vá para [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

### Como Usar 🧭

- **Página Inicial:** Exibe uma visão geral do sistema.
- **Página de Alunos:** Adicione novos alunos e visualize, edite ou remova os existentes. Ao clicar em um aluno, você verá seus projetos e notas.
- **Página de Turmas:** Adicione turmas e gerencie as descrições.
- **Modais:** Os formulários de edição e adição são exibidos em modais para uma melhor experiência do usuário.

---

**Criado por:** Helloysa
