from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

app = FastAPI()

engine = create_engine('postgresql://postgres:root@localhost:900/postgres')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()

class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    age = Column(Integer)

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    subtitle = Column(String(255))
    created = Column(DateTime)
    authorid = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'))
    categoryid = Column(Integer, ForeignKey('category.id', ondelete='SET NULL'))
    
    author = relationship('Author')
    category = relationship('Category')

# migration
Base.metadata.create_all(bind=engine)

@app.post("/authors")
def create_author(name: str, age: int):
    try:
        if not name:
            return JSONResponse(content={'error': 'Name is required'}, status_code=400)
        if age is None:
            return JSONResponse(content={'error': 'Age is required'}, status_code=400)
    
        author = Author(name=name, age=age)
        session.add(author)
        session.commit()
        return JSONResponse(content={'id': author.id, 'name': author.name, 'age': author.age}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.put("/authors")
def put_author(id: int, name: str, age: int):
    try:
        if not id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
        if not name:
            return JSONResponse(content={'error': 'Name is required'}, status_code=400)
        if age is None:
            return JSONResponse(content={'error': 'Age is required'}, status_code=400)
    
        author = session.query(Author).filter_by(id=id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        
        author.name = name
        author.age = age
        session.commit()
        return JSONResponse(content={'id': author.id, 'name': author.name, 'age': author.age}, status_code=200)
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

@app.get("/authors/all")
def get_all_authors():
    try:
        author_list = session.query(Author).all()
        if not author_list:
            return JSONResponse(content={'error': 'No authors found'}, status_code=404)
        
        authors = [{'id': a.id, 'name': a.name, 'age': a.age} for a in author_list]
        return JSONResponse(content=authors, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/authors/{author_id}")
def get_author_with_posts(author_id: int):
    try:
        author = session.query(Author).filter_by(id=author_id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        
        posts = session.query(Post).filter_by(authorid=author_id).all()
        post_list = [{'id': p.id, 'title': p.title, 'subtitle': p.subtitle, 'created': str(p.created), 'categoryid': p.categoryid} for p in posts]
        return JSONResponse(content={
            'author': {
                'id': author.id,
                'name': author.name,
                'age': author.age,
                'posts': post_list
            }
        }, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/categories")
def create_category(name: str):
    try:
        if not name:
            return JSONResponse(content={'error': 'Name is required'}, status_code=400)

        category = Category(name=name)
        session.add(category)
        session.commit()
        return JSONResponse(content={'id': category.id, 'name': category.name}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.put("/categories")
def update_category(id: int, name: str):
    try:
        if not id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
        if not name:
            return JSONResponse(content={'error': 'Name is required'}, status_code=400)
    
        category = session.query(Category).filter_by(id=id).first()
        if not category:
            return JSONResponse(content={'error': 'Category not found'}, status_code=404)
        
        category.name = name
        session.commit()
        return JSONResponse(content={'id': category.id, 'name': category.name}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.delete("/categories")
def delete_category(id: int):
    try:
        if not id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)

        category = session.query(Category).filter_by(id=id).first()
        if not category:
            return JSONResponse(content={'error': 'Category not found'}, status_code=404)
        
        session.delete(category)
        session.commit()
        return JSONResponse(content={'message': 'Category deleted successfully'}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/categories")
def get_all_categories():
    try:
        category_list = session.query(Category).all()
        if not category_list:
            return JSONResponse(content={'error': 'No categories found'}, status_code=404)
        
        categories = [{'id': c.id, 'name': c.name} for c in category_list]
        return JSONResponse(content=categories, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# pegar posts pela categoria
@app.get("/categories/{category_id}/posts")
def get_posts_by_category(category_id: int):
    try:
        category = session.query(Category).filter_by(id=category_id).first()
        if not category:
            return JSONResponse(content={'error': 'Category not found'}, status_code=404)

        posts = session.query(Post).filter_by(categoryid=category_id).all()
        if not posts:
            return JSONResponse(content={'error': 'No posts found'}, status_code=404)
    
        post_list = []
        for post in posts:
            # buscar o author de acordo com o authorid do post
            author = session.query(Author).filter_by(id=post.authorid).first()

            author_data = None
            if author:
                author_data = {
                    'id': author.id,
                    'name': author.name,
                    'age': author.age
                }

            post_data = {
                # post info
                'id': post.id,
                'title': post.title,
                'subtitle': post.subtitle,
                'created': str(post.created),
                # author data
                'author': author_data
            }

            post_list.append(post_data)

        return JSONResponse(content={
            'category': {
                'id': category.id,
                'name': category.name
            },
            'posts': post_list
        }, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/posts")
def create_post(title: str, subtitle: str, authorid: int, categoryid: int):
    try:
        if not title:
            return JSONResponse(content={'error': 'Title is required'}, status_code=400)
        if not subtitle:
            return JSONResponse(content={'error': 'Subtitle is required'}, status_code=400)
        if not categoryid:
            return JSONResponse(content={'error': 'Category ID is required'}, status_code=400)

        author = session.query(Author).filter_by(id=authorid).first()
        category = session.query(Category).filter_by(id=categoryid).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        if not category:
            return JSONResponse(content={'error': 'Category not found'}, status_code=404)
        
        post = Post(title=title, subtitle=subtitle, created=datetime.now(), authorid=authorid, categoryid=categoryid)
        session.add(post)
        session.commit()
        return JSONResponse(content={'id': post.id, 'title': post.title, 'subtitle': post.subtitle, 'created': str(post.created), 'authorid': post.authorid, 'categoryid': post.categoryid}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.put("/posts")
def put_post(id: int, title: str, subtitle: str, authorid: int, categoryid: int):
    try:
        if not id:
            return JSONResponse(content={'error': 'Id is required'}, status_code=400)
        if not title:
            return JSONResponse(content={'error': 'Title is required'}, status_code=400)
        if not categoryid:
            return JSONResponse(content={'error': 'Category ID is required'}, status_code=400)

        post = session.query(Post).filter_by(id=id).first()
        author = session.query(Author).filter_by(id=authorid).first()
        category = session.query(Category).filter_by(id=categoryid).first()
        if not post:
            return JSONResponse(content={'error': 'Post not found'}, status_code=404)
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        if not category:
            return JSONResponse(content={'error': 'Category not found'}, status_code=404)
        
        post.title = title
        post.subtitle = subtitle
        post.authorid = authorid
        post.categoryid = categoryid
        session.commit()
        return JSONResponse(content={'id': post.id, 'title': post.title, 'subtitle': post.subtitle, 'created': str(post.created), 'authorid': post.authorid, 'categoryid': post.categoryid}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# 4. Crie um endpoint GET para retornar todos os posts filtrados por: id da categoria, idade mínima do autor e termo contido no título ou subtítulo do post
@app.get("/posts")
def get_posts():
    try:
        posts = session.query(Post).all()
        if not posts:
            return JSONResponse(content={'error': 'No post found'}, status_code=404)
        
        post_list = []
        for post in posts:
            # buscar o author de acordo com o authorid do post
            author = session.query(Author).filter_by(id=post.authorid).first()
            # buscar o author de acordo com o categoryid do post
            category = session.query(Category).filter_by(id=post.categoryid).first()

            author_data = None
            if author:
                author_data = {
                    'id': author.id,
                    'name': author.name,
                    'age': author.age
                }

            category_data = None
            if category:
                category_data = {
                    'id': category.id,
                    'name': category.name
                }

            post_data = {
                # post info
                'id': post.id,
                'title': post.title,
                'subtitle': post.subtitle,
                'created': str(post.created),
                # author data
                'author': author_data,
                # category data
                'category': category_data
            }

            post_list.append(post_data)

        return JSONResponse(content=post_list, status_code=200)
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