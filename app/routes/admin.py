from flask import render_template, redirect, url_for, flash, request, session, make_response, send_file, Blueprint
from flask_login import login_user, LoginManager, login_required, logout_user, current_user


admin_bp =  Blueprint('admin_blueprint', __name__)

@admin_bp.route('/admin', methods = ['GET','POST'])
@login_required
def admin_index():
    return render_template("admin/index.html")
