#Changing commit message
from flask import Flask, flash, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, PasswordField, SubmitField ,IntegerField, DateField
from wtforms.validators import DataRequired, DataRequired, InputRequired
from wtforms.fields import DateField
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired, InputRequired




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
    zip_code = db.Column(db.String(10), nullable=False)

class RegistrationForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    name = StringField('Name')  # Add this line for the name field
    billing_address_id = StringField('Billing Address ID')
    zip_code = StringField('ZIP Code', validators=[DataRequired()])  # Add this line for the billing_address_id field
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

class DeviceModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    model_number = db.Column(db.String(50), nullable=False)
    enrolled_devices = db.relationship('EnrolledDevice', backref='device_model', lazy=True)

class EnrolledDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_location_id = db.Column(db.Integer, db.ForeignKey('service_location.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('device_model.id'), nullable=False)
    events = db.relationship('EventData', backref='enrolled_device', lazy=True)
    service_location = db.relationship('ServiceLocation', backref='enrolled_devices')

class EventData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('enrolled_device.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    label_id = db.Column(db.Integer, db.ForeignKey('event_label.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)

class EventLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label_name = db.Column(db.String(50), nullable=False, unique=True)
    events = db.relationship('EventData', backref='event_label', lazy=True)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)

class EnergyPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zip_code = db.Column(db.String(10), db.ForeignKey('address.zip_code'), nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    address = db.relationship('Address', backref='energy_prices', lazy=True)


class DeviceModelForm(FlaskForm):
    type = StringField('Device Type', validators=[DataRequired()])
    model_number = StringField('Model Number', validators=[DataRequired()])
    submit = SubmitField('Add Device Model')

class EnrollDeviceForm(FlaskForm):
    device_type = SelectField('Device Type', coerce=int, validators=[DataRequired()])
    service_location = SelectField('Service Location', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Enroll Device')

class AddEventForm(FlaskForm):
    timestamp = DateField('Timestamp', validators=[InputRequired()])
    label_id = SelectField('Label', coerce=int, validators=[InputRequired()])
    value = IntegerField('Value', validators=[InputRequired()])
    submit = SubmitField('Add Event')

class AddEventLabelForm(FlaskForm):
    label_name = StringField('Event Label', validators=[DataRequired()])
    submit = SubmitField('Add Label')

class EnergyPriceForm(FlaskForm):
    zip_code = StringField('Zip Code', validators=[DataRequired()])
    hour = IntegerField('Hour', validators=[DataRequired()])
    rate = FloatField('Rate', validators=[DataRequired()])
    submit = SubmitField('Add Energy Price')

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
            # Add the user to the database
            new_user = User(
                username=form.username.data,
                password=form.password.data,
                name=form.name.data,
                billing_address_id=form.billing_address_id.data,
                zip_code=form.zip_code.data
            )
            db.session.add(new_user)
            db.session.commit()

            # Add the ZIP code to the Address table
            new_address = Address(address=form.billing_address_id.data, zip_code=form.zip_code.data)
            db.session.add(new_address)
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

@app.route('/add_device_model', methods=['GET', 'POST'])
def add_device_model():
    form = DeviceModelForm()

    if form.validate_on_submit():
        new_device_model = DeviceModel(
            type=form.type.data,
            model_number=form.model_number.data
        )
        db.session.add(new_device_model)
        db.session.commit()
        return redirect(url_for('add_device_model'))

    return render_template('add_device_model.html', form=form)

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    form = AddDeviceForm()

    if form.validate_on_submit():
        # Create a new device model if it doesn't exist
        device_model = DeviceModel.query.filter_by(type=form.type.data, model_number=form.model_number.data).first()
        if not device_model:
            device_model = DeviceModel(type=form.type.data, model_number=form.model_number.data)
            db.session.add(device_model)
            db.session.commit()

        # Create a new enrolled device
        enrolled_device = EnrolledDevice(service_location_id=session['service_location_id'], device_model_id=device_model.id)
        db.session.add(enrolled_device)
        db.session.commit()
        return redirect(url_for('enroll_device'))

    return render_template('add_device.html', form=form)

@app.route('/enroll_device', methods=['GET', 'POST'])
def enroll_device():
    form = EnrollDeviceForm()

    # Query all device models for the select field choices
    form.device_type.choices = [(model.id, f"{model.type} - {model.model_number}") for model in DeviceModel.query.all()]

    # Query all service locations for the select field choices
    user_service_locations = ServiceLocation.query.filter_by(user_id=session['user_id']).all()
    form.service_location.choices = [(location.id, location.address) for location in user_service_locations]

    if form.validate_on_submit():
        # Retrieve the selected device model and service location
        selected_device_model = DeviceModel.query.get(form.device_type.data)
        selected_service_location = ServiceLocation.query.get(form.service_location.data)

        # Enroll the device with the selected model and service location
        enrolled_device = EnrolledDevice(
            device_model=selected_device_model,
            service_location=selected_service_location
        )
        db.session.add(enrolled_device)
        db.session.commit()

        # Redirect to the profile page after enrollment
        return redirect(url_for('profile'))

    return render_template('enroll_device.html', form=form)

@app.route('/enrolled_devices')
def enrolled_devices():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.service_locations:
            service_location = user.service_locations[0]  # Assuming the user has only one service location
            enrolled_devices = EnrolledDevice.query.filter_by(service_location_id=service_location.id).all()
            return render_template('enrolled_devices.html', user=user, enrolled_devices=enrolled_devices)
        else:
            flash("Please add a service location before viewing enrolled devices.", 'warning')
            return redirect(url_for('add_service_location'))
    else:
        return redirect(url_for('login'))

@app.route('/remove_enrolled_device/<int:device_id>')
def remove_enrolled_device(device_id):
    enrolled_device = EnrolledDevice.query.get(device_id)
    
    if enrolled_device:
        # Remove the enrolled device from the database
        db.session.delete(enrolled_device)
        db.session.commit()

    return redirect(url_for('profile'))

@app.route('/add_event/<int:device_id>', methods=['GET', 'POST'])
def add_event(device_id):
    form = AddEventForm()
    event_labels = EventLabel.query.all()

    # Pass event label choices to the form
    form.label_id.choices = [(label.id, label.label_name) for label in event_labels]


    if form.validate_on_submit():
        new_event = EventData(
            device_id=device_id,
            timestamp=form.timestamp.data,
            label_id=form.label_id.data,
            value=form.value.data
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('add_event', device_id=device_id))

    return render_template('add_event.html', form=form, device_id=device_id)

@app.route('/add_event_label', methods=['GET', 'POST'])
def add_event_label():
    form = AddEventLabelForm()

    if form.validate_on_submit():
        new_label = EventLabel(label_name=form.label_name.data)
        db.session.add(new_label)
        db.session.commit()

        # Optionally, you can redirect to another page after adding the label
        return redirect(url_for('index'))

    return render_template('add_event_label.html', form=form)

@app.route('/add_energy_price', methods=['GET', 'POST'])
def add_energy_price():
    form = EnergyPriceForm()

    if form.validate_on_submit():
        new_energy_price = EnergyPrice(
            zip_code=form.zip_code.data,
            hour=form.hour.data,
            rate=form.rate.data
        )
        db.session.add(new_energy_price)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_energy_price.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
