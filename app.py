"""
OPC客户管理系统 - 主应用

!!! 新增字段检查清单（重要）!!!
每次在 models.py 中新增字段后，必须同步修改以下 4 处：
1. /add 路由     -> 从 request.form 读取并传给 Customer()
2. /edit 路由    -> 从 request.form 读取并赋值给 customer.xxx
3. add.html      -> 添加对应的表单控件
4. edit.html     -> 添加对应的表单控件（带 selected/value 回显）
5. index.html    -> 客户卡片中展示该字段
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Customer, User
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'opc-crm-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ 默认账号已创建: admin / admin123")


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))

        flash('账号或密码错误', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_username:
            flash('账号不能为空', 'danger')
            return render_template('admin.html', current_user=user)

        if new_password:
            if new_password != confirm_password:
                flash('两次输入的密码不一致', 'danger')
                return render_template('admin.html', current_user=user)
            user.set_password(new_password)

        user.username = new_username
        session['username'] = new_username
        db.session.commit()
        flash('设置已保存', 'success')

    return render_template('admin.html', current_user=user)


@app.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    if search:
        customers = Customer.query.filter(
            Customer.name.contains(search) |
            Customer.wechat.contains(search) |
            Customer.phone.contains(search) |
            Customer.project_name.contains(search)
        ).order_by(Customer.created_at.desc()).all()
    else:
        customers = Customer.query.order_by(Customer.created_at.desc()).all()

    total_amount = sum(c.payment_amount or 0 for c in customers)

    total_project_fee = 0
    for c in customers:
        try:
            total_project_fee += float(c.project_fee) if c.project_fee else 0
        except (ValueError, TypeError):
            pass

    pending_full_count = sum(1 for c in customers if c.payment_status != '付全款')

    return render_template('index.html', customers=customers, search=search,
                           total_amount=total_amount, total_project_fee=total_project_fee,
                           pending_full_count=pending_full_count)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('客户姓名不能为空', 'danger')
            return render_template('add.html')

        payment_amount = request.form.get('payment_amount', '0').strip()
        try:
            payment_amount = float(payment_amount) if payment_amount else 0
        except:
            payment_amount = 0

        join_date_str = request.form.get('join_date', '').strip()
        join_date = None
        if join_date_str:
            try:
                join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
            except:
                join_date = None

        customer = Customer(
            name=name,
            wechat=request.form.get('wechat', '').strip(),
            phone=request.form.get('phone', '').strip(),
            project_name=request.form.get('project_name', '').strip(),
            contract_no=request.form.get('contract_no', '').strip(),
            payment_status=request.form.get('payment_status', '').strip(),
            payment_amount=payment_amount,
            payment_method=request.form.get('payment_method', '').strip(),
            city=request.form.get('city', '').strip(),
            team_size=request.form.get('team_size', '').strip(),
            project_share=request.form.get('project_share', '').strip(),
            project_fee=request.form.get('project_fee', '').strip(),
            docking_sort=request.form.get('docking_sort', '').strip(),
            join_date=join_date,
            remark=request.form.get('remark', '').strip()
        )
        db.session.add(customer)
        db.session.commit()
        flash('客户添加成功', 'success')
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('客户姓名不能为空', 'danger')
            return render_template('edit.html', customer=customer)

        payment_amount = request.form.get('payment_amount', '0').strip()
        try:
            payment_amount = float(payment_amount) if payment_amount else 0
        except:
            payment_amount = 0

        join_date_str = request.form.get('join_date', '').strip()
        if join_date_str:
            try:
                customer.join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
            except:
                customer.join_date = None
        else:
            customer.join_date = None

        customer.name = name
        customer.wechat = request.form.get('wechat', '').strip()
        customer.phone = request.form.get('phone', '').strip()
        customer.project_name = request.form.get('project_name', '').strip()
        customer.contract_no = request.form.get('contract_no', '').strip()
        customer.payment_status = request.form.get('payment_status', '').strip()
        customer.payment_amount = payment_amount
        customer.payment_method = request.form.get('payment_method', '').strip()
        customer.city = request.form.get('city', '').strip()
        customer.team_size = request.form.get('team_size', '').strip()
        customer.project_share = request.form.get('project_share', '').strip()
        customer.project_fee = request.form.get('project_fee', '').strip()
        customer.docking_sort = request.form.get('docking_sort', '').strip()
        customer.remark = request.form.get('remark', '').strip()
        db.session.commit()
        flash('客户信息已更新', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', customer=customer)


@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('客户已删除', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)