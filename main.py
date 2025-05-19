from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

# arquivo init - conexão com a api e banco de dados

# instanciação do app
# swagger: doc para interagir com a api
app = FastAPI()

# driver que vai usar://usuario:senha@endereço de ip:porta/...
# .env no gitignore, em projetos reais
engine = create_engine('postgresql://postgres:root@localhost:900/postgres')

# criar a sessão para manipulação de banco de dados
# não commitar sozinho, não atualizar o banco sozinho, definir a engine a partir da string de conexão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# criar a base de dados
Base = declarative_base()

# se fosse mvc - view chamar, controler api, e model classes que manipulariam o banco de dados
# cada tabela vira uma classe na model - conjunto de classes que refletem as tabelas

# model autor e model 
class Author(Base):

    __tablename__ = 'author'

    # variáveis da classe, primary_key=True é auto incremento
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    age = Column(Integer)

class Post(Base):

    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    created = Column(DateTime)
    subtitle = Column(String(122))
    authorid = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'))
    author = relationship('Author')

# migration
Base.metadata.create_all(bind=engine)

# criar post, ler get, atualizar put ou patch, delete é delete

# @ é a property de uma classe - atributos que podem ou não ter valores default
@app.post('/authors')
# é uma função, não método, então não usa self
def create_author(name: str, age: int):

    if not name:
        return JSONResponse(content={'error': 'Name is required'}, status_code=400)
    if not age:
        return JSONResponse(content={'error': 'Age is required'}, status_code=400)

  # manipulação do banco de dados - pode dar erro
    try:
        author = Author(name=name, age=age)
        # adição do objeto instanciado
        session.add(author)
        # dar commit
        session.commit()
        return JSONResponse(content={'id': author.id, 'name': author.name, 'age': author.age}, status_code=201)
    except Exception as e:
        # evitar o commit pela metade
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# @ é a property de uma classe - atributos que podem ou não ter valores default
@app.post('/posts')
# é uma função, não método, então não usa self
def create_post(title: str, subtitle: str, authorid: int):

  # manipulação do banco de dados - pode dar erro
    try:
        if not title:
            return JSONResponse(content={'error': 'Title is required'}, status_code=400)
        if not subtitle:
            return JSONResponse(content={'error': 'Subtitle is required'}, status_code=400)
        if not authorid:
            return JSONResponse(content={'error': 'AuthorId is required'}, status_code=400)
        
        author = session.query(Author).filter_by(id=authorid).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        
        post = Post(title=title, created=datetime.now(), subtitle=subtitle, authorid=authorid)
        # adição do objeto instanciado
        session.add(post)
        # dar commit
        session.commit()
        return JSONResponse(content={'id': post.id, 'title': post.title, 'subtitle': post.subtitle, 'authorid': post.authorid}, status_code=201)

    except Exception as e:
        # evitar o commit pela metade
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.put("/authors")
def put_author(id: int, name: str, age: int):
    
    try:
        if not id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
        if not name:
            return JSONResponse(content={'error': 'Name is required'}, status_code=400)
        if not age:
            return JSONResponse(content={'error': 'Age is required'}, status_code=400)
        
        # puxa do banco
        author = session.query(Author).filter_by(id=id).first()
        # verifica se não é nulo
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        # atribui ao objeto.name o name do parâmetro
        author.name = name
        author.age = age
        session.commit()
        return JSONResponse(content={'id': author.id, 'name': author.name, 'age': author.age}, status_code=200)
    
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.put("/posts")
def put_post(id: int, title: str, subtitle: str, authorid: str):
    
    try:
        if not id:
            return JSONResponse(content={'error': 'Id is required'}, status_code=400)
        if not title:
            return JSONResponse(content={'error': 'Title is required'}, status_code=400)
        if not subtitle:
            return JSONResponse(content={'error': 'Subtitle is required'}, status_code=400)
        if not authorid:
            return JSONResponse(content={'error': 'AuthorId is required'}, status_code=400)
        
        # puxa do banco
        post = session.query(Post).filter_by(id=id).first()
        # verifica se não é nulo
        if not post:
            return JSONResponse(content={'error': 'Post not found'}, status_code=404)
        
        author = session.query(Author).filter_by(id=authorid).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)

        # atribui ao objeto.name o name do parâmetro
        post.title = title
        post.subtitle = subtitle
        post.authorid = authorid
        session.commit()
        return JSONResponse(content={'id': post.id, 'title': post.title, 'created': str(post.title),'subtitle': post.subtitle, 'idauthor': post.authorid}, status_code=200)
    
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.delete("/authors")
def delete_author(id: int):
    
    try:

        if not id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
        
        author = session.query(Author).filter_by(id=id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        
        session.delete(author)
        session.commit()
        return JSONResponse(content={'message': 'Author deleted successfully'}, status_code=200)
    
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.delete("/posts")
def delete_post(id: int):
    
    try:
        if not id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
        
        post = session.query(Post).filter_by(id=id).first()
        if not post:
            return JSONResponse(content={'error': 'Post not found'}, status_code=404)
        
        session.delete(post)
        session.commit()
        return JSONResponse(content={'message': 'Post deleted successfully'}, status_code=200)
    
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get('/authors/all')
def get_all_authors():
    try:
        author_list = session.query(Author).all()
        if not author_list:
            return JSONResponse(content={'error': 'No authors found'}, status_code=404)
        authors = []
        for author in author_list:
            authors.append({'id':author.id, 'name': author.name, 'age': author.age})
        return JSONResponse(content=authors, status_code=200)
    
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get('/posts/all')
def get_all_posts():
    try:
        posts = session.query(Post).all()

        if not posts:
            return JSONResponse(content={'error': 'No posts found'}, status_code=404)

        post_list = []
        for post in posts:
            
            author = session.query(Author).filter_by(id=post.authorid).first()
            if not author:
                return JSONResponse(content={'error': 'Author not found'}, status_code=404)
            
            post_list.append({
                'id': post.id,
                'title': post.title,
                'created': str(post.created),
                'authorid': author.id,
                'author_name': author.name
            })
        return JSONResponse(content=post_list, status_code=200)
    
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500) 

@app.get('/authors/{author_id}')
def get_author(author_id: int):

    try:
        if not author_id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    
        author = session.query(Author).filter_by(id=author_id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        return JSONResponse(content={'id': author.id, 'name': author.name, 'age': author.age}, status_code=200)
    
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get('/posts/{post_id}')
def get_post(post_id: int):

    try:
        if not post_id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    
        post = session.query(Post).filter_by(id=post_id).first()
        if not post:
            return JSONResponse(content={'error': 'Post not found'}, status_code=404)
        return JSONResponse(content={'id': post.id, 'title': post.title, 'created': str(post.created),'subtitle': post.subtitle, 'authorid': post.authorid}, status_code=200)

    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
@app.get('/authorsposts/{author_id}')
def get_authorsposts(author_id: int):
    
    try:
        if not author_id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
        
        author = session.query(Author).filter_by(id=author_id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        
        post_list = session.query(Post).filter_by(authorid=author_id).all()
        if not post_list:
            return JSONResponse(content={'error': 'Author with no posts'}, status_code=404)
        
        posts = []
        for post in post_list: # perguntar sobre created
            posts.append({'id':post.id, 'title': post.title, 'created': str(post.created), 'subtitle': post.subtitle})

        return JSONResponse(content=posts, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)