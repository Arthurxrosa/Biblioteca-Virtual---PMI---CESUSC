import psycopg2
from usuario import Usuario
from livro import Livro
from estante import Estante
from flask import Flask, request, render_template, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'secret_key'

# Configuração da conexão com o banco de dados (substitua pelas suas credenciais)
conn = psycopg2.connect(
    host="isabelle.db.elephantsql.com",
    port="5432",
    user="pfvofsbv",
    password="zA6kL72NE2RImcdNGnejkOpI1kGdjtSG",
    database="pfvofsbv",
    sslmode="require"
)

cursor = conn.cursor()

# Função para obter uma conexão com o banco de dados
def get_connection():
    connection = psycopg2.connect(
        host="isabelle.db.elephantsql.com",
        port="5432",
        user="pfvofsbv",
        password="zA6kL72NE2RImcdNGnejkOpI1kGdjtSG",
        database="pfvofsbv"
    )
    return connection



# Lógica de Cadastro de Usuário
def cadastrar_usuario1(nome, email, senha):
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s) RETURNING id;",
                       (nome, email, senha))
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.Error as e:
        conn.rollback()
        print("Erro ao cadastrar usuário:", e)
        return None

# Lógica de Autenticação de Usuário
def autenticar_usuario(email, senha):
    cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s;", (email, senha))
    usuario_data = cursor.fetchone()

    if usuario_data:
        user_id, nome, _, _ = usuario_data
        return Usuario(id=user_id, nome=nome, email=email, senha=senha)
    else:
        return None

# Lógica para Obter Informações do Usuário por ID
def obter_usuario_por_id(usuario_id):
    cursor.execute("SELECT * FROM usuarios WHERE id = %s;", (usuario_id,))
    usuario_data = cursor.fetchone()

    if usuario_data:
        user_id, nome, email, senha = usuario_data
        return Usuario(id=user_id, nome=nome, email=email, senha=senha)
    else:
        return None

# Lógica de Cadastro de Livro
def cadastrar_livro1(nome, autor, descricao, estante_id):
    cursor.execute("INSERT INTO livros (nome, autor, descricao, estante_id) VALUES (%s, %s, %s, %s)",
                   (nome, autor, descricao, estante_id))
    conn.commit()


# Lógica para Obter Livros por Estante
def obter_livros_por_estante(estante_id):
    cursor.execute("SELECT * FROM livros WHERE estante_id = %s", (estante_id,))
    livros_info = cursor.fetchall()

    livros = [Livro(*livro_info) for livro_info in livros_info]
    return livros


# Lógica de Cadastro de Estante
def cadastrar_estante(nome, usuario_id):
    cursor.execute("INSERT INTO estantes (nome, usuario_id) VALUES (%s, %s) RETURNING id;", (nome, usuario_id))
    estante_id = cursor.fetchone()[0]
    conn.commit()
    return estante_id

# Lógica para Obter Estantes por Usuário
def obter_estantes_por_usuario(usuario_id):
    cursor.execute("SELECT * FROM estantes WHERE usuario_id = %s;", (usuario_id,))
    estantes = cursor.fetchall()
    return [Estante(id=estante[0], nome=estante[1], usuario_id=estante[2]) for estante in estantes]


def execute_query(query, params=None):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)



# Função para editar um livro
def editar_livro(livro_id, nome, autor, descricao):
    query = "UPDATE livros SET nome = %s, autor = %s, descricao = %s WHERE id = %s"
    params = (nome, autor, descricao, livro_id)

    with get_connection() as conn:
        execute_query(query, params)



# Função para excluir um livro
def excluir_livro(livro_id):
    query = "DELETE FROM livros WHERE id = %s"
    params = (livro_id,)

    with get_connection() as conn:
        execute_query(query, params,)




def obter_livro_por_id(livro_id):
    cursor.execute("SELECT * FROM livros WHERE id = %s", (livro_id,))
    livro_info = cursor.fetchone()

    if livro_info:
        livro = Livro(id=livro_info[0], nome=livro_info[1], autor=livro_info[2], descricao=livro_info[3],
                      estante_id=livro_info[4])

        cursor.execute("SELECT * FROM estantes WHERE id = %s", (livro.estante_id,))
        estante_info = cursor.fetchone()

        estante = Estante(id=estante_info[0], nome=estante_info[1], usuario_id=estante_info[2])

        livro.estante = estante
        return livro
    else:
        return None





# Rota inicial (login)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = autenticar_usuario(email, senha)

        if usuario:
            session['user_id'] = usuario.id
            return redirect(url_for('biblioteca'))
        else:
            mensagem = 'Credenciais inválidas. Tente novamente.'
            return render_template('login.html', mensagem=mensagem)

    return render_template('login.html')

# Rota para a tela da biblioteca
@app.route('/biblioteca')
def biblioteca():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    estantes = obter_estantes_por_usuario(user_id)

    return render_template('biblioteca.html', estantes=estantes)

# Rota para sair (logout)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Rota para a tela de criação de estantes
@app.route('/criar_estante', methods=['GET', 'POST'])
def criar_estante():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome_estante = request.form['nome_estante']
        cadastrar_estante(nome_estante, user_id)

        return redirect(url_for('biblioteca'))

    return render_template('criar_estante.html')

# Rota para a tela da estante
@app.route('/estante/<int:estante_id>')
def estante(estante_id):
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    livros = obter_livros_por_estante(estante_id)

    return render_template('estante.html', estante=estante, livros=livros)

# Rota para a tela de cadastro de livros
@app.route('/cadastrar_livro/<int:estante_id>', methods=['GET','POST'])
def cadastrar_livro(estante_id):
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome_livro = request.form['nome_livro']
        autor_livro = request.form['autor_livro']
        descricao_livro = request.form['descricao_livro']

        cadastrar_livro1(nome_livro, autor_livro, descricao_livro, estante_id)

        return redirect(url_for('estante', estante_id=estante_id))

    return render_template('cadastrar_livro.html', estante_id=estante_id)



@app.route('/editar_livro/<int:livro_id>', methods=['GET', 'POST'])
def editar_livro_route(livro_id):
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    livro = obter_livro_por_id(livro_id)

    if not livro or livro.estante.usuario_id != user_id:
        return redirect(url_for('biblioteca'))

    if request.method == 'POST':
        nome_livro = request.form.get('nome')
        autor_livro = request.form.get('autor')
        descricao_livro = request.form.get('descricao')

        if nome_livro is not None and autor_livro is not None and descricao_livro is not None:
            editar_livro(livro_id, nome_livro, autor_livro, descricao_livro)
            return redirect(url_for('estante', estante_id=livro.estante.id))

    return render_template('editar_livro.html', livro=livro)



@app.route('/excluir_livro/<livro_id>', methods=['POST'])
def excluir_livro_route(livro_id):
    excluir_livro(livro_id)
    return redirect(url_for('biblioteca'))

# Rota para a tela de cadastro de usuário
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        usuario_id = cadastrar_usuario1(nome, email, senha)

        if usuario_id:
            session['user_id'] = usuario_id
            return redirect(url_for('biblioteca'))
        else:
            mensagem = 'Erro ao cadastrar usuário. Tente novamente.'
            return render_template('cadastro_usuario.html', mensagem=mensagem)

    return render_template('cadastro_usuario.html')


if __name__ == '__main__':
    app.run(debug=True)
