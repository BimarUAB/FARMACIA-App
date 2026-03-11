from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Crear admin
        if not User.query.filter_by(username="admin").first():
            admin_user = User(username="admin", email="admin@gestionventas.com", role="admin")
            admin_user.set_password('1234')  
            db.session.add(admin_user)
            print("Usuario admin creado")

        # Crear vendedor
        if not User.query.filter_by(username="vendedor").first():
            vendedor_user = User(username="vendedor", email="vendedor@gestionventas.com", role="vendedor")
            vendedor_user.set_password('1234') 
            db.session.add(vendedor_user)
            print("Usuario vendedor creado")
      
        # Crear usuario normal (opcional)
        if not User.query.filter_by(username="usuario").first():
            usuario_normal = User(username="usuario", email="usuario@gestionventas.com", role="usuario")
            usuario_normal.set_password('1234')  
            db.session.add(usuario_normal)
            print("Usuario normal creado")
        
        db.session.commit()
        
        # Verificar usuarios creados
        # usuarios = User.query.all()
        # print(f"\n Total de usuarios: {len(usuarios)}")
        # for u in usuarios:
           #  print(f"   - {u.username} ({u.role}) - {u.email}")
    
    app.run(debug=True)