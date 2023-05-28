from datetime import date
import os

from flask import Blueprint, session, request, render_template, current_app, redirect, url_for
from database.sql_provider import SQLProvider
from database.db_work import insert, select, select_dict
from access import login_required

blueprint_order = Blueprint('blueprint_order', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_order.route('/check-order', methods=['GET', 'POST'])
@login_required
def check_invoice():
    if request.method == 'GET':
        return render_template('check_products.html')
    else:
        inv_id = request.form.get('inv_id')
        _sql = provider.get('check_invoice.sql', inv_id=inv_id)
        invoice_result, schema = select(current_app.config['db_config'], _sql)
        schema = ("id", "Название товара", "Количество", "Объем", "Стоимость", "Дата прибытия")
    return render_template('result_products.html', schema=schema, result=invoice_result)


@blueprint_order.route('/products')
@login_required
def check_products_external():
    sup_id = session.get('sup_id')
    print(sup_id)
    _sql = provider.get('available_products.sql', sup_id=sup_id)
    invoice_result, schema = select(current_app.config['db_config'], _sql)
    invoice_result = list(invoice_result)
    print(invoice_result[1][3])
    for i in range(len(invoice_result)):
        if invoice_result[i][3] is not None:
            differ = round((invoice_result[i][3] - invoice_result[i][2]).days * 10 + \
                           0.7 * (invoice_result[i][1]) + pow(invoice_result[i][4],
                                                              1 / (1 + invoice_result[i][4])) * 1 / 1 +
                           invoice_result[i][4])
            invoice_result[i] = list(invoice_result[i])
            invoice_result[i][4] = (invoice_result[i][3] - invoice_result[i][2]).days
            invoice_result[i].append(differ)
        else:
            invoice_result[i] = list(invoice_result[i])
            invoice_result[i].append(invoice_result[i][4])
            invoice_result[i][4] = None
    schema = ("Название товара", "Количество", "Начало хранения", "Конец хранения",
              "Осталось дней", "Общая стоимость хранения")
    print('res', invoice_result)
    return render_template('available_products.html', schema=schema, result=invoice_result)


@blueprint_order.route('/start', methods=['GET', 'POST'])
@login_required
def start_order():
    db_config = current_app.config['db_config']
    if request.method == 'GET':
        basket_items = session.get('basket', {})
        print(session)
        schema = ("Название", "Стоимость", "Количество", "Объем")
        return render_template('customer_order.html', basket=basket_items, schema=schema)
    else:
        kkey = 0
        if request.form.get('form_id') == 'item_form':
            product_name = request.form.get('product_name')
            cost = request.form.get('cost')
            amount = request.form.get('amount')
            volume = request.form.get('volume')
            sql = provider.get('pr_id.sql')
            print(sql)
            sql2 = provider.get('product_list.sql')
            print(sql2)
            pr_list = select(db_config, sql2)
            print(pr_list)
            basket_items = session.get('basket', {})
            if not session.get('basket', {}):  # если нет корзины
                pr_id = str(select_dict(db_config, sql)[0]['pr_id'] + 1)
            else:  # если есть корзина
                for i in basket_items.keys():  # если есть товар в корзине
                    if basket_items[i]['product_name'] == product_name \
                            and basket_items[i]['cost'] == cost \
                            and basket_items[i]['volume'] == volume:
                        # если товар с такими же параметрами есть в корзине
                        pr_id = i
                        kkey = 1
                if kkey == 0:
                    pr_id = str(int(max(session.get('basket', {}).keys(), key=int)) + 1)
            item = make_dict(product_name, cost, amount, volume)
            add_to_basket(pr_id, item)
            print('basket', basket_items)
        return redirect(url_for('blueprint_order.start_order'))


def make_dict(product_name, cost, amount, volume):
    item = {
        'product_name': product_name,
        'cost': cost,
        'amount': amount,
        'volume': volume
    }
    return item


def add_to_basket(pr_id: str, item: dict):
    curr_basket = session.get('basket', {})
    print(item)
    if pr_id in curr_basket:
        curr_basket[pr_id]['amount'] = int(curr_basket[pr_id]['amount']) + int(item['amount'])
    else:
        curr_basket[pr_id] = {
            'product_name': item['product_name'],
            'amount': item['amount'],
            'cost': item['cost'],
            'volume': item['volume']
        }
        session['basket'] = curr_basket
        session.permanent = True  # ?
    return True


@blueprint_order.route('/clear-basket')
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
    return redirect(url_for('blueprint_order.start_order'))


@blueprint_order.route('/save-order', methods=['GET', 'POST'])
def save_order():
    db_config = current_app.config['db_config']
    key = 0
    all_cost = 0
    all_count = 0
    key_list = []
    basket_keys = []
    time_arr = request.form.get('start_date')
    time_dep = request.form.get('storing_date')
    sup_id = session.get('sup_id')
    current_basket = session.get('basket', {})
    sql_max = provider.get('pr_id.sql')
    maximum = select_dict(db_config, sql_max)[0]['pr_id']
    product_list = select_dict(db_config, provider.get('product_list.sql'))
    for x in current_basket.keys():
        basket_keys.append(x)
        for y in range(len(product_list)):
            if current_basket[x]['product_name'] == product_list[y]['product_name'] \
                    and str(current_basket[x]['volume']) == str(product_list[y]['volume']):
                print('yes')
                key_list.append(y)
                break
            else:
                if y == (len(product_list) - 1):
                    key_list.append(int(x))
    for x in basket_keys:
        current_basket[str(key_list[key])] = current_basket.pop(x)
        key = key + 1
    for x in current_basket.keys():  # вставка товаров, которые ещё не были на складе
        all_cost = int(all_cost) + int(current_basket[x]['cost'])
        all_count = int(all_count) + int(current_basket[x]['amount'])
        if int(x) > maximum:
            pr_id = x
            product_name = current_basket[x]['product_name']
            volume = current_basket[x]['volume']
            sql_insert = provider.get('insert.sql', pr_id=pr_id, product_name=product_name, volume=volume)
            print(sql_insert)
            insert(db_config, sql_insert)
    print(all_cost, all_count)
    inv_id = save_order_with_list(db_config, sup_id, time_arr, time_dep, all_cost, all_count, current_basket)
    if inv_id:
        session.pop('basket')
        return render_template('order_created.html', order_id=inv_id)
    else:
        return 'FAIL!'


def save_order_with_list(db_config: dict, sup_id: int, time_arr, time_dep, all_cost, all_count, current_basket: dict):
    time_order = date.today()
    _sql1 = provider.get('inv_id.sql')
    inv_id = int(select(db_config, _sql1)[0][0][0]) + 1
    _sql1 = provider.get('insert_invoice.sql', inv_id=inv_id, sup_id=sup_id, time_order=time_order, time_arr=time_arr,
                         time_dep=time_dep,
                         all_cost=all_cost, all_count=all_count)
    insert(db_config, _sql1)  # вносим в таблицу с ордерами данные о юзере и данные о дате

    if int(inv_id) > 0:
        _sql2 = provider.get('p_inv_id.sql')  # берем теперь наш order_id
        p_inv_id = int(select(db_config, _sql2)[0][0][0])  # вытаскиваем от туда максимальный p in inv id
        if p_inv_id:
            for key in current_basket:
                p_inv_id = int(p_inv_id) + 1
                print('key', key)
                amount = current_basket[key]['amount']  # вытаскиваем из корзины то, сколько у нас товара
                cost = current_basket[key]['cost']  # вытаскиваем из корзины то, сколько стоит
                _sql3 = provider.get('insert_product_in_invoice.sql', p_inv_id=p_inv_id, pr_id=key, inv_id=inv_id,
                                     amount=amount, cost=cost)
                print('sql3', _sql3)
                insert(db_config,
                       _sql3)  # вставляем в таблицу с содержимым корзины информацию о номере заказа id заказа и
                # количестве
            return inv_id
