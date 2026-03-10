from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        
        # Crear vendedor
        if not User.query.filter_by(username="vendedor").first():
            vendedor_user = User(username="vendedor", email="vendedor@gestionventas.com", role="vendedor")
            vendedor_user.set_password('1234') 
            db.session.add(vendedor_user)
            print("Usuario vendedor creado")
        
        
    app.run(debug=True)