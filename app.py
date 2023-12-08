from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField ,IntegerField, DateField
from wtforms.validators import DataRequired, DataRequired, InputRequired
from wtforms.fields import DateField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(100), nullable=True)  # Add this line for the name field
    billing_address_id = db.Column(db.Integer, nullable=True)  # Add this line for the billing_address_id field
    service_locations = db.relationship('ServiceLocation', backref='user', lazy=True)

class RegistrationForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    name = StringField('Name')  # Add this line for the name field
    billing_address_id = StringField('Billing Address ID')  # Add this line for the billing_address_id field
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ServiceLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    unit_number = db.Column(db.String(20), nullable=True)
    square_footage = db.Column(db.Integer, nullable=True)
    bedrooms = db.Column(db.Integer, nullable=True)
    occupants = db.Column(db.Integer, nullable=True)

class AddServiceLocationForm(FlaskForm):
    customer = StringField('Customer')
    address = StringField('Address')
    unit_number = StringField('Unit Number')
    date_taken_over = DateField('Date Taken Over', validators=[DataRequired()])
    square_footage = IntegerField('Square Footage')
    bedrooms = IntegerField('Bedrooms')
    occupants = IntegerField('Occupants')
    submit = SubmitField('Add Service Location')

class EditServiceLocationForm(FlaskForm):
    customer = StringField('Customer', validators=[InputRequired()])
    address = StringField('Address', validators=[InputRequired()])
    unit_number = StringField('Unit Number', validators=[InputRequired()])
    date_taken_over = DateField('Date Taken Over', validators=[InputRequired()])
    square_footage = IntegerField('Square Footage', validators=[InputRequired()])
    bedrooms = IntegerField('Bedrooms', validators=[InputRequired()])
    occupants = IntegerField('Occupants', validators=[InputRequired()])
    submit = SubmitField('Save Changes')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    billing_address_id = StringField('Billing Address ID', validators=[InputRequired()])
    submit = SubmitField('Save Changes')

@app.route('/')
def index():
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
        return render_template('index.html', message=f"Welcome, {current_user.username}!", current_user=current_user)
    else:
        return render_template('index.html', message="Welcome to the Energy Monitoring System!", current_user=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    error_message = None

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            error_message = "Username already exists. Please choose a different one."
        else:
            new_user = User(username=form.username.data, password=form.password.data, name=form.name.data, billing_address_id=form.billing_address_id.data)
            db.session.add(new_user)
            db.session.commit()

            # Set the user's session after successful registration
            session['user_id'] = new_user.id

            return redirect(url_for('index'))

    return render_template('register.html', form=form, error_message=error_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error_message = None

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            # Set a session variable to indicate that the user is logged in
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            # Provide specific error messages
            if not user:
                error_message = "Invalid username. Please check your username and try again."
            else:
                error_message = "Invalid password. Please check your password and try again."

    return render_template('login.html', form=form, current_user=None, error_message=error_message)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()

    if 'user_id' in session:
        user = User.query.get(session['user_id'])

        if form.validate_on_submit():
            # Update user profile information
            user.name = form.name.data
            user.billing_address_id = form.billing_address_id.data
            db.session.commit()

            return redirect(url_for('profile'))

        # Pre-fill the form with existing user details
        form.name.data = user.name
        form.billing_address_id.data = user.billing_address_id

        return render_template('edit_profile.html', form=form)
    else:
        # Handle the case where the user is not logged in
        return redirect(url_for('login'))

@app.route('/add_service_location', methods=['GET', 'POST'])
def add_service_location():
    form = AddServiceLocationForm()

    if form.validate_on_submit():
        new_location = ServiceLocation(
            user_id=session['user_id'],
            address=form.address.data,
            unit_number=form.unit_number.data,
            square_footage=form.square_footage.data,
            bedrooms=form.bedrooms.data,
            occupants=form.occupants.data
        )
        db.session.add(new_location)
        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('add_service_location.html', form=form)

@app.route('/edit_service_location/<int:location_id>', methods=['GET', 'POST'])
def edit_service_location(location_id):
    form = EditServiceLocationForm()
    location = ServiceLocation.query.get(location_id)

    if form.validate_on_submit():
        location.address = form.address.data
        location.unit_number = form.unit_number.data
        location.square_footage = form.square_footage.data
        location.bedrooms = form.bedrooms.data
        location.occupants = form.occupants.data
        db.session.commit()
        return redirect(url_for('profile'))

    # Pre-fill the form with existing service location details
    form.address.data = location.address
    form.unit_number.data = location.unit_number
    form.square_footage.data = location.square_footage
    form.bedrooms.data = location.bedrooms
    form.occupants.data = location.occupants

    return render_template('edit_service_location.html', form=form, location=location)

@app.route('/remove_service_location/<int:location_id>')
def remove_service_location(location_id):
    location = ServiceLocation.query.get(location_id)
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for('profile'))



if __name__ == '__main__':
    app.run(debug=True)
