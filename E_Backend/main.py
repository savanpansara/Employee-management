from flask import Flask, request, jsonify,send_from_directory # type: ignore
from flask_cors import CORS # type: ignore
from pymongo import MongoClient # type: ignore
from bson import ObjectId # type: ignore
import bcrypt # type: ignore
from werkzeug.utils import secure_filename # type: ignore
import os

# Initialize Flask app and allow CORS for all routes
app = Flask(__name__)
CORS(app,supports_credentials=True)


client = MongoClient('mongodb://localhost:27017/')
db = client['EmployeeMS']  
Eemployee= db['employee']
Eadmin=db['admin']
Ecategory=db['category']

@app.route('/')
def home():
    return "<h1>Hello, JENIL !  Welcome to the Management.</h1>"


# Employee Management
# --------------------

# Admin Route
@app.route('/adminlogin', methods=['POST'])
def admin_login():
    email = request.json.get('email')
    password = request.json.get('password')

    admin = Eadmin.find_one({"email": email})

    if admin:
        stored_password = admin['password']
        if (password==stored_password):
            return jsonify({"loginStatus": True})
        else:
            return jsonify({"loginStatus": False, "Error": "Invalid password"})
    else:
        return jsonify({"loginStatus": False, "Error": "User not found"})

@app.route('/add_admin/<id>', methods=['POST'])
def add_admin(id):
    em=Eemployee.find_one({"_id":ObjectId(id)})
    data = {
        "name": em['name'],
        "email":em['email'],
        "employee_id":id,
        "password": request.json.get("password")
    }
    add=Eadmin.insert_one(data)
    if add:
        return jsonify({"Status": True})
    else:
        return jsonify({"Status": False})
    
@app.route('/delete_admin/<id>', methods=['DELETE'])
def delete_admin(id):
    Eadmin.delete_one({"_id": ObjectId(id)})
    return jsonify({"Status": True})

@app.route('/admin_records', methods=['GET'])
def admin_records():
    admin_r=Eadmin.find().skip(1)
    admin_list=[]
    for ad in admin_r:
        admin_list.append({"id": str(ad["_id"]), "name": ad["name"],"email":ad["email"]})
    return jsonify({"Status": True, "Result": admin_list})

@app.route('/admin_count', methods=['GET'])
def admin_count():
    count=0
    admin_c=Eadmin.find()
    for a in admin_c:
        count+=1
    return jsonify({"Status": True, "Result": count})

# Categories Route

@app.route('/category', methods=['GET'])
def get_category():
    categories = Ecategory.find()
    category_list = []
    for category in categories:
        category_list.append({"id": str(category["_id"]), "name": category["name"]})
    return jsonify({"Status": True, "Result": category_list})

@app.route('/add_category', methods=['POST'])
def add_category():
    category_name = request.json.get('category')
    Ecategory.insert_one({"name": category_name})
    return jsonify({"Status": True})

@app.route('/category_employee/<id>', methods=['GET'])
def get_cat_employee(id):
    cat_employees = Eemployee.find({"category_id": str(id)})
    cat_employee_list = []
    for emp in cat_employees:
        cat_employee_list.append({
            "id": str(emp["_id"]),
            "name": emp["name"],
            "email": emp["email"],
            "salary": emp["salary"],
            "address": emp["address"],
            "mobile": emp["mobile"],
            "image":emp["image"]
        })
    return jsonify({"Status": True, "Result": cat_employee_list})

@app.route('/delete_category/<id>', methods=['DELETE'])
def delete_category(id):
    cat = Eemployee.find_one({"category_id": id})
    if not cat:
        Ecategory.delete_one({"_id": ObjectId(id)})
        return jsonify({"Status": True})
    else:
        return jsonify({"Status": False})

# Employee Route

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'images') 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        else:
            image_filename = None
    else:
        image_filename = None
    data = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "salary": request.form.get("salary"),
        "address": request.form.get("address"),
        "image": image_filename,
        "category_id": request.form.get("category_id"),
        "mobile": request.form.get("mobile")
    }
    Eemployee.insert_one(data)
    return jsonify({"Status": True})

@app.route('/edit_employee/<id>', methods=['PUT'])
def edit_employee(id):
    data = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "salary": request.form.get("salary"),
        "address": request.form.get("address"),
        "category_id": request.form.get("category_id"),
        "mobile": request.form.get("mobile")
    }
    Eemployee.update_one({"_id": ObjectId(id)},{"$set":data})
    return jsonify({"Status": True})

@app.route('/employee', methods=['GET'])
def get_employee():
    employees = Eemployee.find()
    employee_list = []
    for emp in employees:
        employee_list.append({
            "id": str(emp["_id"]),
            "name": emp["name"],
            "email": emp["email"],
            "salary": emp["salary"],
            "address": emp["address"],
            "mobile": emp["mobile"],
            "image":emp["image"]
        })
    return jsonify({"Status": True, "Result": employee_list})

@app.route('/delete_employee/<id>', methods=['DELETE'])
def delete_employee(id):
    Eemployee.delete_one({"_id": ObjectId(id)})
    return jsonify({"Status": True})

@app.route('/employee_count', methods=['GET'])
def employee_count():
    count=0
    em_c=Eemployee.find()
    for a in em_c:
        count+=1
    return jsonify({"Status": True, "Result": count})

@app.route('/salary_count', methods=['GET'])
def salary_count():
    salarycount=0
    salary_c=Eemployee.find()
    for a in salary_c:
        salarycount+=int(a['salary'])
    return jsonify({"Status": True, "Result": salarycount})


@app.route('/employee_detail/<id>', methods=['GET'])
def employee_detail(id):
    empl = Eemployee.find_one({"_id": ObjectId(id)})
    if empl:
        cat = Ecategory.find_one({"_id": ObjectId(empl["category_id"])})
        if cat:
            cat_name=cat['name']
        else:
            cat_name="None"
        employee_data = {
            "id": str(empl["_id"]),
            "name": empl["name"],
            "email": empl["email"],
            "category":cat_name,
            "salary": empl["salary"],
            "address": empl["address"],
            "mobile": empl["mobile"],
            "image": empl["image"]
        }
        return jsonify({"Status": True, "Result": employee_data})
    else:
        return jsonify({"Status": False, "Message": "Employee not found"})

# Logout 
@app.route('/logout', methods=['GET'])
def logout():
    return jsonify({"Status": True})



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False) 