from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

def to_int(value):
    return int(value)


# Função para obter a conexão com o banco de dados
def get_db():
    conn = psycopg2.connect(
        host='silly.db.elephantsql.com',
        port=5432,
        database='ihmbqxbh',
        user='ihmbqxbh',
        password='2rAdiAjuMVma6LHLaCz5O3q5V8ioGE8V'
    )
    return conn

# Rota principal
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('estantes'))
    return redirect(url_for('login'))

# Rota de cadastro de usuário
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'username' in session:
        return redirect(url_for('estantes'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('cadastro.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('estantes'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = %s AND password = %s", (username, password))
        usuario = cur.fetchone()
        cur.close()
        conn.close()
        if usuario:
            session['username'] = username
            return redirect(url_for('estantes'))
        else:
            return render_template('login.html', error='Usuário ou senha inválidos')
    return render_template('login.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Rota para exibir as estantes
@app.route('/estantes')
def estantes():
    if 'username' in session:
        username = session['username']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM estantes WHERE username = %s", (username,))
        estantes = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('estantes.html', estantes=estantes)
    return redirect(url_for('login'))

# Rota para criar uma nova estante
@app.route('/nova_estante', methods=['GET', 'POST'])
def nova_estante():
    if 'username' in session:
        if request.method == 'POST':
            username = session['username']
            nome_estante = request.form['nome_estante']
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO estantes (username, nome_estante) VALUES (%s, %s)", (username, nome_estante))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('estantes'))
        return render_template('nova_estante.html')
    return redirect(url_for('login'))

# Rota para editar uma estante
@app.route('/editar_estante/<int:estante_id>', methods=['GET', 'POST'])
def editar_estante(estante_id):
    if 'username' in session:
        username = session['username']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM estantes WHERE id = %s AND username = %s", (estante_id, username))
        estante = cur.fetchone()
        cur.close()
        conn.close()
        if estante:
            if request.method == 'POST':
                nome_estante = request.form['nome_estante']
                conn = get_db()
                cur = conn.cursor()
                cur.execute("UPDATE estantes SET nome_estante = %s WHERE id = %s", (nome_estante, estante_id))
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for('estantes'))
            return render_template('editar_estante.html', estante=estante)
        else:
            return redirect(url_for('estantes'))
    return redirect(url_for('login'))

# Rota para excluir uma estante
@app.route('/excluir_estante/<int:estante_id>', methods=['POST'])
def excluir_estante(estante_id):
    if 'username' in session:
        username = session['username']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM estantes WHERE id = %s AND username = %s", (estante_id, username))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('estantes'))
    return redirect(url_for('login'))

# Rota para exibir uma estante e seus livros
@app.route('/estante/<int:estante_id>')
def estante(estante_id):
    if 'username' in session:
        username = session['username']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM estantes WHERE id = %s AND username = %s", (estante_id, username))
        estante = cur.fetchone()
        if estante:
            cur.execute("SELECT * FROM livros WHERE estante_id = %s", (estante_id,))
            livros = cur.fetchall()
            cur.close()
            conn.close()
            return render_template('estante.html', estante=estante, livros=livros)
    return redirect(url_for('login'))

# Rota para criar um novo livro em uma estante
@app.route('/estante/<int:estante_id>/novo_livro', methods=['GET', 'POST'])
def novo_livro(estante_id):
    if 'username' in session:
        if request.method == 'POST':
            username = session['username']
            titulo = request.form['titulo']
            autor = request.form['autor']
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO livros (estante_id, username, titulo, autor) VALUES (%s, %s, %s, %s)", (estante_id, username, titulo, autor))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('estante', estante_id=estante_id))
        return render_template('novo_livro.html', estante_id=estante_id)
    return redirect(url_for('login'))

# Rota para editar um livro
@app.route('/estante/<int:estante_id>/editar_livro/<int:livro_id>', methods=['GET', 'POST'])
def editar_livro(livro_id, estante_id):
    if request.method == 'POST':
        # Obter os dados do formulário
        titulo = request.form['titulo']
        autor = request.form['autor']

        # Atualizar os dados do livro no banco de dados
        cur = get_db().cursor()
        cur.execute("UPDATE livros SET titulo = %s, autor = %s WHERE id = %s", (titulo, autor, livro_id))
        get_db().commit()

        # Redirecionar de volta para a estante
        return render_template('editar_livro.html', estante_id=estante_id, to_int=to_int)

    # Obter os dados do livro do banco de dados
    cur = get_db().cursor()
    cur.execute("SELECT * FROM livros WHERE id = %s", (livro_id,))
    livro = cur.fetchone()

    if livro:
        # Renderizar o template de edição de livro
        return render_template('editar_livro.html', livro=livro, estante_id=estante_id)
    else:
        # Livro não encontrado, redirecionar de volta para a estante
        return redirect(url_for('estante', estante_id=estante_id))




# Rota para excluir um livro
@app.route('/livro/<int:livro_id>/excluir', methods=['POST'])
def excluir_livro(livro_id):
    if 'username' in session:
        username = session['username']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT estante_id FROM livros WHERE id = %s AND username = %s", (livro_id, username))
        livro = cur.fetchone()
        if livro:
            cur.execute("DELETE FROM livros WHERE id = %s", (livro_id,))
            conn.commit()
            cur.close()
            conn.close()
            livro_dict = dict(livro)
            estante_id = livro_dict['estante_id']
            return redirect(url_for('estante', estante_id=estante_id))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
