from application_files import db, create_app, login_manager
from flask import render_template
from config.commands import register_commands
from application_files.models.user import User
# Blueprints
from application_files.controllers.auth_controller import auth_bp
from application_files.controllers.users_controller import users_bp
from application_files.controllers.admin_controller import admin_bp

app = create_app()

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)

register_commands(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
