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

          
    app.run(debug=True)