#Changing commit message
import sqlite3
from flask import Flask, flash, render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from sqlalchemy import DateTime, text
from wtforms import DateTimeLocalField, FloatField, StringField, PasswordField, SubmitField ,IntegerField, DateField
from wtforms.validators import DataRequired, DataRequired, InputRequired
from wtforms.fields import DateField
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash




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
    hour = db.Column(DateTime, nullable=False)  # Change this line
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
    timestamp = DateTimeLocalField('Timestamp', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    label_id = SelectField('Label', coerce=int, validators=[InputRequired()])
    value = IntegerField('Value', validators=[InputRequired()])
    submit = SubmitField('Add Event')

class AddEventLabelForm(FlaskForm):
    label_name = StringField('Event Label', validators=[DataRequired()])
    submit = SubmitField('Add Label')

class EnergyPriceForm(FlaskForm):
    zip_code = StringField('Zip Code', validators=[DataRequired()])
    hour = DateTimeLocalField('Hour', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
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
            username = form.username.data
            password = form.password.data
            name = form.name.data
            billing_address_id = form.billing_address_id.data
            zip_code = form.zip_code.data
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256')


            con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
            cur = con.cursor()

            # User creation
            cur.execute(
                "INSERT INTO User (username, password, name, billing_address_id, zip_code) VALUES (?, ?, ?, ?, ?)",
                (username, password, name, billing_address_id, zip_code),
            )

            # Address addition
            cur.execute(
                "INSERT INTO Address (address, zip_code) VALUES (?, ?)",
                (billing_address_id, zip_code),
            )

            con.commit()
            new_user = User.query.filter_by(username=username).first()

            con.close()
            
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
        if user and (user.password == form.password.data or check_password_hash(user.password, form.password.data)):
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

        all_zip_codes = db.session.query(EnergyPrice.zip_code).distinct().all()
        all_zip_codes = [zip_code[0] for zip_code in all_zip_codes]

        return render_template('profile.html', user=user, all_zip_codes=all_zip_codes)
    else:
        return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()

    if 'user_id' in session:
        user = User.query.get(session['user_id'])

        if form.validate_on_submit():
            # Update user profile information using insert queries
            user_id = session['user_id']
            name = form.name.data
            billing_address_id = form.billing_address_id.data

            con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
            cur = con.cursor()

            # Update user profile
            cur.execute(
                "UPDATE User SET name = ?, billing_address_id = ? WHERE id = ?",
                (name, billing_address_id, user_id),
            )

            con.commit()
            con.close()

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
        user_id = session['user_id']
        address = form.address.data
        unit_number = form.unit_number.data
        square_footage = form.square_footage.data
        bedrooms = form.bedrooms.data
        occupants = form.occupants.data

        con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
        cur = con.cursor()

        # Add new location using insert query
        cur.execute(
            "INSERT INTO Service_Location (user_id, address, unit_number, square_footage, bedrooms, occupants) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, address, unit_number, square_footage, bedrooms, occupants),
        )

        con.commit()
        con.close()

        return redirect(url_for('profile'))

    return render_template('add_service_location.html', form=form)

@app.route('/edit_service_location/<int:location_id>', methods=['GET', 'POST'])
def edit_service_location(location_id):
    form = EditServiceLocationForm()
    location = ServiceLocation.query.get(location_id)

    if form.validate_on_submit():
        address = form.address.data
        unit_number = form.unit_number.data
        square_footage = form.square_footage.data
        bedrooms = form.bedrooms.data
        occupants = form.occupants.data

        con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
        cur = con.cursor()

        # Update service location using insert query
        cur.execute(
            "UPDATE Service_Location SET address = ?, unit_number = ?, square_footage = ?, bedrooms = ?, occupants = ? "
            "WHERE id = ?",
            (address, unit_number, square_footage, bedrooms, occupants, location_id),
        )

        con.commit()
        con.close()

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
        device_type = form.type.data
        model_number = form.model_number.data

        con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
        cur = con.cursor()

        # Add new device model using insert query
        cur.execute(
            "INSERT INTO DeviceModel (type, model_number) VALUES (?, ?)",
            (device_type, model_number),
        )

        con.commit()
        con.close()

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
    con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
    cur = con.cursor()
    cur.execute("SELECT id, type, model_number FROM Device_Model")
    device_models = cur.fetchall()
    con.close()
    form.device_type.choices = [(model[0], f"{model[1]} - {model[2]}") for model in device_models]

    # Query all service locations for the select field choices
    user_id = session['user_id']
    con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
    cur = con.cursor()
    cur.execute("SELECT id, address FROM Service_Location WHERE user_id = ?", (user_id,))
    service_locations = cur.fetchall()
    con.close()
    form.service_location.choices = [(location[0], location[1]) for location in service_locations]

    if form.validate_on_submit():
        device_type_id = form.device_type.data
        service_location_id = form.service_location.data

        con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
        cur = con.cursor()

        # Enroll the device with the selected model and service location using insert query
        cur.execute(
            "INSERT INTO Enrolled_Device (service_location_id, model_id) VALUES (?, ?)",
            (service_location_id, device_type_id),
        )

        con.commit()
        con.close()

        # Redirect to the profile page after enrollment
        return redirect(url_for('profile'))

    return render_template('enroll_device.html', form=form)

@app.route('/enrolled_devices')
def enrolled_devices():
    if 'user_id' in session:
        user_id = session['user_id']

        con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
        cur = con.cursor()

        # Retrieve the user's service location ID
        cur.execute("SELECT id FROM ServiceLocation WHERE user_id = ? LIMIT 1", (user_id,))
        service_location_id = cur.fetchone()

        if service_location_id:
            service_location_id = service_location_id[0]
            # Fetch enrolled devices using raw query
            cur.execute("SELECT * FROM EnrolledDevice WHERE service_location_id = ?", (service_location_id,))
            enrolled_devices = cur.fetchall()

            # Fetch device models for displaying information
            devices_info = []
            for device in enrolled_devices:
                device_id = device[0]
                model_info = cur.execute("SELECT type, model_number FROM DeviceModel WHERE id = ?", (device[3],)).fetchone()
                devices_info.append({'id': device_id, 'type': model_info[0], 'model_number': model_info[1]})

            con.close()

            return render_template('enrolled_devices.html', user=user, devices_info=devices_info)
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

    con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
    cur = con.cursor()

    # Fetch event labels for dropdown choices
    cur.execute("SELECT id, label_name FROM Event_Label")
    event_labels = cur.fetchall()

    # Pass event label choices to the form
    form.label_id.choices = [(label[0], label[1]) for label in event_labels]

    if form.validate_on_submit():
        # Insert new event using raw query
        if not isinstance(form.timestamp.data, datetime):
            # Convert the string input to a datetime object
            form.timestamp.data = datetime.strptime(form.timestamp.data, '%Y-%m-%dT%H:%M')
        cur.execute(
            "INSERT INTO Event_Data (device_id, timestamp, label_id, value) VALUES (?, ?, ?, ?)",
            (device_id, form.timestamp.data, form.label_id.data, form.value.data)
        )
        con.commit()
        con.close()

        return redirect(url_for('add_event', device_id=device_id))

    return render_template('add_event.html', form=form, device_id=device_id)

@app.route('/add_event_label', methods=['GET', 'POST'])
def add_event_label():
    form = AddEventLabelForm()

    con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
    cur = con.cursor()

    if form.validate_on_submit():
        # Insert new event label using raw query
        cur.execute("INSERT INTO Event_Label (label_name) VALUES (?)", (form.label_name.data,))
        con.commit()
        con.close()

        # Optionally, you can redirect to another page after adding the label
        return redirect(url_for('index'))

    return render_template('add_event_label.html', form=form)

@app.route('/add_energy_price', methods=['GET', 'POST'])
def add_energy_price():
    form = EnergyPriceForm()

    con = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
    cur = con.cursor()

    if form.validate_on_submit():
        # Check if form.hour.data is already a datetime object
        if not isinstance(form.hour.data, datetime):
            # Convert the string input to a datetime object
            form.hour.data = datetime.strptime(form.hour.data, '%Y-%m-%dT%H:%M')

        # Insert new energy price using raw query
        cur.execute(
            "INSERT INTO Energy_Price (zip_code, hour, rate) VALUES (?, ?, ?)",
            (form.zip_code.data, form.hour.data, form.rate.data)
        )
        con.commit()
        con.close()

        return redirect(url_for('index'))

    return render_template('add_energy_price.html', form=form)

@app.route('/energy_consumption/<int:service_location_id>/<string:time_resolution>')
def energy_consumption(service_location_id, time_resolution):
    # Fetch daily energy consumption data based on the selected time resolution
    if time_resolution == 'day':
        query = """
            SELECT DATE(e.Timestamp) AS date, SUM(e.Value) AS total_energy
            FROM event_data e
            JOIN enrolled_device ed ON e.Device_ID = ed.id
            WHERE ed.Service_Location_ID = :service_location_id
            GROUP BY date
        """
        con2 = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
        cur2 = con2.cursor()
        data = cur2.execute(query, (service_location_id,)).fetchall()
    elif time_resolution == 'month':
        # Adjust the query for monthly data if needed
        query = """
            SELECT strftime('%m', e.Timestamp) AS month, SUM(e.Value) AS total_energy
            FROM event_data e
            JOIN enrolled_device ed ON e.Device_ID = ed.id
            WHERE ed.Service_Location_ID = :service_location_id
            GROUP BY month
        """
        con2 = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
        cur2 = con2.cursor()
        data = cur2.execute(query, (service_location_id,)).fetchall()
        pass
    else:
        return "Invalid time resolution"

    # Extract data for the chart
    labels = [str(row[0]) for row in data]
    values = [row[1] for row in data]
    con2.close()
    return render_template('energy_consumption.html', labels=labels, values=values, time_resolution=time_resolution)

@app.route('/device_energy_consumption/<int:service_location_id>')
def device_energy_consumption(service_location_id):
    # Fetch energy consumption per device for the last month
    query = """
        SELECT * from device_energy_consumption where service_location_id=:service_location_id
    """
    con2 = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
    cur2 = con2.cursor()
    data = cur2.execute(query, (service_location_id,)).fetchall()
    con2.close()
    # Extract data for the chart
    # Extract data for the chart
    model_ids = [row[0] for row in data]
    total_energies = [row[2] for row in data]


    return render_template('device_energy_consumption.html', model_ids=model_ids,  total_energies=total_energies)


@app.route('/monthly_energy_cost/<int:service_location_id>')
def monthly_energy_cost(service_location_id):
    # Fetch data for the line graph of monthly cost of electricity
    query = """
        SELECT * FROM monthly_energy_cost WHERE id = :service_location_id
    """
    con3 = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
    cur3 = con3.cursor()
    data = cur3.execute(query, (service_location_id,)).fetchall()
    con3.close()

    # Extract data for the line graph
    months = [row[0] for row in data]
    total_energy_costs = [row[2] for row in data]

    return render_template('monthly_energy_cost.html', months=months, total_energy_costs=total_energy_costs)

@app.route('/energy_price_zipcode')
def energy_price_zipcode():
    # Fetch data for the average usage consumption
    zip_code = request.args.get('zip_code')
    query = """
        Select hour,rate from energy_price where zip_code=:zip_code
    """
    con3 = sqlite3.connect("C:\\Smart-Home-Energy-Management-System\\instance\\site.db")
    cur3 = con3.cursor()
    data = cur3.execute(query, (zip_code,)).fetchall()
    con3.close()

    # Extract data for the plot
    hour = [row[0] for row in data]
    rate = [row[1] for row in data]

    return render_template('energy_price_zipcode.html', hours=hour,
                           rates=rate)




if __name__ == '__main__':
    app.run(debug=True)
