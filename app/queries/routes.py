import os
from flask import session
from flask import Blueprint, request, render_template, current_app
from database.sql_provider import SQLProvider
from database.db_work import select
from access import group_required
from access import login_required


blueprint_queries = Blueprint('blueprint_queries', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_queries.route('/all-products')
@login_required
def check_products_internal():
    _sql = provider.get('check_products.sql')
    invoice_result, schema = select(current_app.config['db_config'], _sql)
    schema = ("id","Название товара", "Категория", "Объем")
    return render_template('result_products.html', schema=schema, result=invoice_result)


@blueprint_queries.route('/orders-history', methods=['GET', 'POST'])
@group_required
def check_order_history():
    if request.method == 'GET':
        return render_template('order_result.html')
    else:
        dates = request.form.get('dates')
        date_one, date_two = dates.split('- ')
        customer = request.form.get('customer')
        if date_one and date_two:
            _sql = provider.get('check_order_hsitory.sql', date_one=date_one, date_two=date_two, customer=customer)
            print(_sql)
            invoice_result, schema = select(current_app.config['db_config'], _sql)
            schema = ("id Накладной", "id Поставщика", "Дата заказа", "Дата прибытия", "Дата отправки",
                      "Количество товаров", "Стоимость товаров")
            return render_template('order_result.html', schema=schema, result=invoice_result)
        else:
            return "Repeat input"


@blueprint_queries.route('/clients', methods=['GET', 'POST'])
@group_required
def check_customer_supplier():
    print(session)
    if any(x == session.get('user_group', None) for x in ('manager', 'director')):
         _sql = provider.get('check_customer_supplier.sql')
         invoice_result, schema = select(current_app.config['db_config'], _sql)
         schema = ("id Клиента", "Название", "Телефон", "Номер счета в банке", "Начало сотрудничества", "Вид организации")
         return render_template('result_customer_supplier.html', schema=schema, result=invoice_result)
    else:
        if request.method == 'GET':
            return render_template('check_customer_supplier.html')
        else:
            invoice_id = request.form.get('inv_id')
            if invoice_id:
                _sql = provider.get('check_customer_supplier(loader).sql', inv_id=invoice_id)
                invoice_result, schema = select(current_app.config['db_config'], _sql)
                schema = ("id Клиента", "Название", "Телефон")
                return render_template('result_customer_supplier.html', schema=schema, result=invoice_result)
            else:
                return "Repeat input"