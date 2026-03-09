from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from models import db, User, Company, Student, PlacementDrive, Application
from models import Roles, CompanyApprovalStatus, DriveStatus, ApplicationStatus
from forms import LoginForm, StudentRegistrationForm, CompanyRegistrationForm , CompanyProfileUpdateForm, PlacementDriveForm, ApplicationStatusUpdateForm, StudentUpdateForm
from datetime import datetime
from  sqlalchemy.exc import IntegrityError
import os
from werkzeug.utils import secure_filename 

def create_app(database_uri="sqlite:///placement.db"):
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = "placement-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "static/resumes"
    app.config["ALLOWED_EXTENTIONS"] = {"pdf","doc","docx"}
    os.makedirs(app.config["UPLOAD_FOLDER"],exist_ok=True)

    def allowed_file(filename):
        return "." in filename and filename.rsplit(".",1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    class LoginUser(UserMixin):
        pass

    @login_manager.user_loader
    def load_user(user_id):
        uid = User.query.get(int(user_id))
        if not uid:
            return None
        u_obj = LoginUser()
        u_obj.id = uid.id
        return u_obj
    


    def is_admin():
        return current_user and User.query.get(int(current_user.id)).role == Roles.ADMIN.value
    def is_company():
        return current_user and User.query.get(int(current_user.id)).role == Roles.COMPANY.value
    def is_student():
        return current_user and User.query.get(int(current_user.id)).role == Roles.STUDENT.value
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/login',methods=["GET", "POST"])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.strip()).first()
            if user and user.passwd == form.password.data:
                login_user(user)

                if user.role == Roles.ADMIN.value:
                    return redirect(url_for("admin_dashboard"))
                elif user.role == Roles.COMPANY.value:
                    return redirect(url_for("company_dashboard"))
                elif user.role == Roles.STUDENT.value:
                    return redirect(url_for("student_dashboard"))
            else:
                flash("Invalid credentials")

        return render_template("auth/login.html", form=form)
    
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))
    
    @app.route("/register/student", methods=["GET", "POST"])
    def register_student():
        form = StudentRegistrationForm()

        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data.strip()).first():
                flash("Email already exists")
                return redirect(url_for("register_student"))
            
            userReg = User(
                name=form.name.data.strip(),
                email=form.email.data.strip(),
                passwd=form.password.data,
                role=Roles.STUDENT.value
            )
            db.session.add(userReg)
            db.session.commit()

            newStudent =Student(user_id=userReg.id,
                                name = form.name.data,
                                branch = form.branch.data,
                                cgpa = form.cgpa.data,
                                graduation_year = form.graduation_year.data,
                                )
            db.session.add(newStudent)
            db.session.commit()

            flash("Student Registered")
            return redirect(url_for("login"))
        return render_template("auth/register_student.html", form=form)
    
    @app.route("/register/company", methods=["GET", "POST"])
    def register_company():
        form = CompanyRegistrationForm()

        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data.strip()).first():
                flash("Email already exists")
                return redirect(url_for("register_company"))

            new_user = User(
                name=form.name.data.strip(),
                email=form.email.data.strip(),
                passwd=form.password.data,
                role=Roles.COMPANY.value
            )

            db.session.add(new_user)
            db.session.commit()

            new_company = Company(
                user_id=new_user.id,
                company_name=form.name.data,
                company_email = form.email.data,
                hr_contact=form.hr_contact.data,
                website=form.website.data,
                approval_status=CompanyApprovalStatus.PENDING.value
            )

            db.session.add(new_company)
            db.session.commit()
            
            flash("Company registration submitted. Await admin approval.")
            return redirect(url_for("login"))

        return render_template("auth/register_company.html", form=form)

# ADMIN ROUTES
# ADMIN ROUTES
# ADMIN ROUTES
# ADMIN ROUTES
# ADMIN ROUTES
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if not is_admin():
            flash("Access not permitted")
            return redirect(url_for("index"))
        students = Student.query.all()
        drives = PlacementDrive.query.all()
        companies = Company.query.all()

        total_students = Student.query.count()
        total_companies = Company.query.filter_by(approval_status = CompanyApprovalStatus.APPROVED.value).count()
        total_drives = PlacementDrive.query.count()
        total_applications = Application.query.count()

        student_results = []
        company_results= []
        query = request.args.get("q", "").strip()

        if query:
            if query.isdigit():
                company_results = Company.query.filter_by(id= int(query)).all()
                student_results = Student.query.filter_by(id = int(query)).all()
            else:
                student_results = Student.query.join(User).filter(User.name.ilike(f"%{query}%") |
                                                                User.email.ilike(f"%{query}%")).all()
                company_results = Company.query.join(User).filter(User.name.ilike(f"%{query}%") |
                                                                User.email.ilike(f"%{query}%")).all()
                

            student_results = Student.query.join(User).filter(
                User.name.ilike(f"%{query}%") |
                User.email.ilike(f"%{query}%")).all()
        return render_template("admin/dashboard.html", companies=companies, students=students, drives=drives,
                            total_students=total_students, total_applications=total_applications, 
                            total_companies = total_companies, total_drives= total_drives, query= query,
                            company_results= company_results, student_results =student_results)
    
    
    @app.route("/admin/companies")
    @login_required
    def admin_companies():
        if not is_admin():
            flash("Access denied")
            return redirect(url_for("index"))

        companies = Company.query.all()
        return render_template("admin/companies.html", companies=companies)
    
    
    @app.route("/admin/company/<int:company_id>/update_status/<string:action>")
    @login_required
    def admin_update_company_status(company_id, action):
        if not is_admin():
            flash("Access denied")
            return redirect(url_for("index"))

        company = Company.query.get_or_404(company_id)

        if action == "approve":
            company.approval_status = CompanyApprovalStatus.APPROVED.value
            flash("Company approved successfully")

        elif action == "reject":
            company.approval_status = CompanyApprovalStatus.REJECTED.value
            flash("Company rejected")

        db.session.commit()
        return redirect(url_for("admin_companies"))
    

    @app.route("/admin/company/<int:company_id>/blacklist")
    @login_required
    def admin_blacklist_company(company_id):
        if not is_admin():
            flash("Access denied")
            return redirect(url_for("index"))

        company = Company.query.get_or_404(company_id)
        if company.is_blacklisted:
            company.is_blacklisted = False
            flash(f"{company.company_name} is no longer Blacklisted")
        else:
            company.is_blacklisted = True
            flash(f"{company.company_name} is blacklisted")

        db.session.commit()

        return redirect(url_for("admin_companies"))

    @app.route("/admin/students")
    @login_required
    def admin_students():
        if not is_admin():
            flash("Access denied")
            return redirect(url_for("index"))

        students = Student.query.all()
        return render_template("admin/students.html", students=students)

    @app.route("/admin/student/<int:student_id>/deactivate")
    @login_required
    def admin_deactivate_student(student_id):
        if not is_admin():
            flash("Access denied")
            return redirect(url_for("index"))

        student = Student.query.get_or_404(student_id)
        if student.user.is_active:
            student.user.is_active = False
            db.session.commit()
            flash("Student account deactivated")
        else:
            student.user.is_active = True    
            db.session.commit()
            flash("Student account Activated")


        return redirect(url_for("admin_students"))
    
    @app.route('/admin/student/<int:student_id>/edit_student', methods = ["POST", "GET"])
    @login_required
    def admin_edit_student(student_id):
        if not is_admin():
            flash("Access denied")
            return redirect(url_for('index'))
        student = Student.query.get_or_404(student_id)
        user = student.user

        form = StudentUpdateForm()
        if form.validate_on_submit():
            user.name = form.name.data.strip()
            student.name = form.name.data.strip()
            student.branch = form.branch.data
            student.cgpa = form.cgpa.data
            student.graduation_year = form.graduation_year.data
            

            db.session.commit()
            flash("Student Profile updated successfully")
            return redirect(url_for("admin_students"))

        form.name.data = user.name
        form.branch.data = student.branch
        form.cgpa.data = student.cgpa
        form.graduation_year.data = student.graduation_year

        return render_template('admin/edit_student.html', form=form, student = student)

    @app.route('/admin/student/<int:student_id>/delete_student')
    @login_required
    def admin_delete_student(student_id):
        if not is_admin():
            flash("You cannot perform this action")
            return redirect(url_for('admin_students'))
        student = Student.query.get_or_404(student_id)
        applicationlist = Application.query.filter_by(student_id = student.id)
        user = student.user

        try:
            for appl in applicationlist:
                db.session.delete(appl)

            db.session.delete(student)
            if user:
                db.session.delete(user)

            db.session.commit()
            flash("Student profile deleted successfully")

        except Exception as e:
            db.session.rollback()
            flash("Error deleting student")
        return redirect(url_for('admin_students'))


    @app.route("/admin/drives")
    @login_required
    def admin_drives():
        if not is_admin():
            flash("Access denied")
            return redirect(url_for("index"))

        drives = PlacementDrive.query.all()
        return render_template("admin/drives.html", drives=drives)
    
    @app.route("/admin/drive/<int:drive_id>/update_status/<string:action>")
    @login_required
    def admin_update_drive_status(drive_id, action):
        if not is_admin():
            flash("Access denied")
            return redirect(url_for("index"))

        drive = PlacementDrive.query.get_or_404(drive_id)

        if action == "approve":
            drive.status = DriveStatus.APPROVED.value
            flash("Drive approved")

        elif action == "reject":
            drive.status = DriveStatus.CLOSED.value
            flash("Drive rejected")

        db.session.commit()
        return redirect(url_for("admin_drives"))
    
    @app.route('/admin/drives/<int:drive_id>/applications')
    @login_required
    def admin_view_applications(drive_id):
        if not is_admin:
            flash("access denied")
            return redirect(url_for('index'))
        applications = Application.query.filter_by(drive_id = drive_id)
        currentdrive = PlacementDrive.query.filter_by(id = drive_id).first()

        return render_template('admin/view_applications.html', drive=currentdrive, applications = applications)







    
    @app.route('/admin/companies/<int:company_id>/edit', methods=["GET","POST"])
    @login_required
    def admin_edits_company(company_id):
        if not is_admin():
            flash("Access denied")
            return redirect(url_for('admin_companies'))
        currcompany = Company.query.get_or_404(company_id)
        comuser = currcompany.user

        form = CompanyProfileUpdateForm()

        if form.validate_on_submit():
            currcompany.company_name = form.name.data 
            comuser.name = form.name.data
            currcompany.hr_contact = form.hr_contact.data 
            currcompany.website  = form.website.data 

            db.session.commit()
            flash("Company details updated")
            return redirect(url_for('admin_companies'))
        
        form.name.data = currcompany.company_name
        form.hr_contact.data =currcompany.hr_contact
        form.website.data = currcompany.website

        return render_template('/admin/edit_company.html', form = form)








# COMPANY ROUTES
# COMPANY ROUTES
# COMPANY ROUTES
# COMPANY ROUTES
# COMPANY ROUTES


    @app.route("/company/dashboard")
    @login_required
    def company_dashboard():
        if not is_company():
            flash("Access denied")
            return redirect(url_for("index"))

        company = Company.query.filter_by(user_id=current_user.id).first()

        if not company:
            flash("Company profile not found")
            return redirect(url_for("index"))

        if company.approval_status != CompanyApprovalStatus.APPROVED.value:
            flash("Company not approved yet")
            return redirect(url_for("index"))

        if company.is_blacklisted:
            flash("Company is blacklisted")
            return redirect(url_for("index"))

        drives = PlacementDrive.query.filter_by(company_id=company.id).all()

        return render_template("company/dashboard.html",company=company,drives=drives)
    

    @app.route("/company/drive/create", methods=["GET", "POST"])
    @login_required
    def create_drive():
        if not is_company():
            flash("Access denied")
            return redirect(url_for("index"))

        company = Company.query.filter_by(user_id=current_user.id).first()

        if company.approval_status != CompanyApprovalStatus.APPROVED.value:
            flash("Company not approved")
            return redirect(url_for("company_dashboard"))

        if company.is_blacklisted:
            flash("Company is blacklisted")
            return redirect(url_for("company_dashboard"))

        form = PlacementDriveForm()

        if form.validate_on_submit():
            new_drive = PlacementDrive(
                company_id=company.id,
                job_title=form.job_title.data,
                job_description=form.job_description.data,
                eligibility_criteria=form.eligibility_criteria.data,
                application_deadline=form.application_deadline.data,
                status=DriveStatus.PENDING.value
            )

            db.session.add(new_drive)
            db.session.commit()

            flash("Placement drive created. Awaiting admin approval.")
            return redirect(url_for("company_dashboard"))

        return render_template("company/create_drive.html", form=form)
    
    @app.route("/company/drive/<int:drive_id>/close")
    @login_required
    def close_drive(drive_id):
        if not is_company():
            flash("Access denied")
            return redirect(url_for("index"))

        drive = PlacementDrive.query.get_or_404(drive_id)

        company = Company.query.filter_by(user_id=current_user.id).first()

        if drive.company_id != company.id:
            flash("Unauthorized action")
            return redirect(url_for("company_dashboard"))

        drive.status = DriveStatus.CLOSED.value
        db.session.commit()

        flash("Drive closed successfully")
        return redirect(url_for("company_dashboard"))
    
        
    
    @app.route("/company/drive/<int:drive_id>/applications")
    @login_required
    def view_applications(drive_id):
        if not is_company():
            flash("Access denied")
            return redirect(url_for("index"))

        drive = PlacementDrive.query.get_or_404(drive_id)
        company = Company.query.filter_by(user_id=current_user.id).first()

        if drive.company_id != company.id:
            flash("Unauthorized access")
            return redirect(url_for("company_dashboard"))

        applications = Application.query.filter_by(drive_id=drive.id).all()

        return render_template("company/applications.html", drive=drive,applications=applications)

    @app.route("/company/application/<int:application_id>/update", methods=["GET", "POST"])
    @login_required
    def update_application_status(application_id):
        if not is_company():
            flash("Access denied")
            return redirect(url_for("index"))

        application = Application.query.get_or_404(application_id)
        company = Company.query.filter_by(user_id=current_user.id).first()

        if application.drive.company_id != company.id:
            flash("Unauthorized action")
            return redirect(url_for("company_dashboard"))

        form = ApplicationStatusUpdateForm()

        if form.validate_on_submit():
            application.status = form.status.data
            db.session.commit()

            flash("Application status updated")
            return redirect(
                url_for("view_applications", drive_id=application.drive_id)
            )

        return render_template("company/update_application.html",form=form,application=application)
    


    @app.route("/company/profile")
    @login_required
    def company_profile():
        if not is_company():
            flash("Access denied")
            return redirect(url_for("index"))

        company = Company.query.filter_by(user_id=current_user.id).first()

        return render_template("company/profile.html", company=company)






    # @app.route("/company/dashboard")
    # @login_required
    # def company_dashboard():
    #     if not is_company():
    #         flash("Access denied")
    #         return redirect(url_for("index"))

    #     company = Company.query.filter_by(user_id=current_user.id).first()

    #     if company.approval_status != CompanyApprovalStatus.APPROVED.value:
    #         flash("Company not approved by admin yet")
    #         return redirect(url_for("index"))

    #     drives = PlacementDrive.query.filter_by(company_id=company.id).all()

    #     return render_template("company/dashboard.html", company=company, drives=drives)
    



    # STUDENT ROUTES
    # STUDENT ROUTES
    # STUDENT ROUTES
    # STUDENT ROUTES
    # STUDENT ROUTES




    @app.route("/student/dashboard")
    @login_required
    def student_dashboard():
        if not is_student():
            flash("Access denied")
            return redirect(url_for("index"))

        approved_drives = PlacementDrive.query.filter_by(status=DriveStatus.APPROVED.value).all()
        student = Student.query.filter_by(user_id=current_user.id).first()
        applications = Application.query.filter_by(student_id=student.id).all()
        

        return render_template("student/dashboard.html",drives=approved_drives,applications=applications, student=student,
        current_date = datetime.today().date())
    
    @app.route("/student/apply/<int:drive_id>")
    @login_required
    def apply_drive(drive_id):
        if not is_student():
            flash("Access denied")
            return redirect(url_for("index"))

        student = Student.query.filter_by(user_id=current_user.id).first()
        drive = PlacementDrive.query.get_or_404(drive_id)

        if drive.status != DriveStatus.APPROVED.value:
            flash("Drive not available for application")
            return redirect(url_for("student_dashboard"))

        if drive.application_deadline and drive.application_deadline < datetime.today().date():
            flash("Application deadline has passed")
            return redirect(url_for("student_dashboard"))

        existing_application = Application.query.filter_by(student_id=student.id,drive_id=drive.id).first()

        if existing_application:
            flash("You have already applied for this drive")
            return redirect(url_for("student_dashboard"))

        new_application = Application(
            student_id=student.id,
            drive_id=drive.id,
            status=ApplicationStatus.APPLIED.value
        )

        db.session.add(new_application)
        db.session.commit()

        flash("Application submitted successfully")
        return redirect(url_for("student_dashboard"))
    
    @app.route("/student/application/<int:application_id>")
    @login_required
    def view_application(application_id):
        if not is_student():
            flash("Access denied")
            return redirect(url_for("index"))
    
        application = Application.query.get_or_404(application_id)
        student = Student.query.filter_by(user_id=current_user.id).first()
    
        if application.student_id != student.id:
            flash("Unauthorized access")
            return redirect(url_for("student_dashboard"))
    
        return render_template("student/application_detail.html",application=application)
    

    @app.route("/student/history")
    @login_required
    def student_history():
        if not is_student():
            flash("Access denied")
            return redirect(url_for("index"))

        student = Student.query.filter_by(user_id=current_user.id).first()

        selected_applications = Application.query.filter_by(
            student_id=student.id,
            status=ApplicationStatus.SELECTED.value).all()

        return render_template("student/history.html",applications=selected_applications)
    
    @app.route("/student/profile/edit", methods=["GET", "POST"])
    @login_required
    def edit_student_profile():
        if not is_student():
            flash("Access denied")
            return redirect(url_for("index"))

        student = Student.query.filter_by(user_id=current_user.id).first()
        user = student.user

        form = StudentUpdateForm()

        if form.validate_on_submit():
            user.name = form.name.data.strip()
            student.name = form.name.data.strip()
            student.branch = form.branch.data
            student.cgpa = form.cgpa.data
            student.graduation_year = form.graduation_year.data

            file = request.files.get("resume")

            if file :
                filename = secure_filename(file.filename)
                fname = f"{student.name}-{filename}"
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], fname)
                file.save(file_path)
                student.resume = fname
            

            db.session.commit()
            flash("Profile updated successfully")
            return redirect(url_for("student_dashboard"))

        form.name.data = user.name
        form.branch.data = student.branch
        form.cgpa.data = student.cgpa
        form.graduation_year.data = student.graduation_year
        

        return render_template("student/edit_profile.html", form=form, student = student)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)    

    







