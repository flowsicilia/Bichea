from index import app, db, User

with app.app_context():
    new_user = User(username='donpedro')
    new_user.set_password('test1234')
    db.session.add(new_user)
    db.session.commit()

    print("Usuario creado correctamente")