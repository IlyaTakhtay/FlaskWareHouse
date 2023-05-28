import calendar
import locale
import os, json
import datetime

from flask import session
from flask import Blueprint, request, render_template, current_app, redirect, url_for
from database.sql_provider import SQLProvider
from database.db_work import insert
from database.db_work import select
from database.db_work import call_proc
from database.db_work import select_dict
from access import group_required
from access import login_required

now = datetime.datetime.now()

with open('configs/report_list.json', encoding='utf-8') as rl:
    report_list = json.load(rl)
with open('configs/report_url.json', encoding='utf-8') as ru:
    report_url = json.load(ru)

blueprint_report = Blueprint('blueprint_report', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@blueprint_report.route('/start-report', methods=['GET', 'POST'])
@group_required
def report():
    if request.method == 'GET':
        return render_template('report_menu.html', report_list=report_list)
        print(report_list)
    else:
        rep_id = request.form.get('rep_id')
        print('rep_id=', rep_id)
        if request.form.get('create_rep'):
            url_rep = report_url[rep_id]['create_rep']
        else:
            url_rep = report_url[rep_id]['view_rep']
        print('url_rep=', url_rep)
        return redirect(url_for(url_rep))


@blueprint_report.route('/create-report-1', methods=['GET', 'POST'])
@group_required
def create_rep1():
    if request.method == 'GET':
        now_date = now.strftime("%Y-%m")
        return render_template('report_form.html',now_date=now_date)
    else:
        rep_month = request.form.get('rep_date')
        rep_date = rep_month
        rep_year, rep_month = rep_month.split('-')
        if rep_month and rep_year:
            _sql = provider.get('check.sql', rep_month=rep_month, rep_year=rep_year)
            product_result, schema = select(current_app.config['db_config'], _sql)
            if product_result:
                return render_template('report_exist.html')
            res = call_proc(current_app.config['db_config'], 'generate_report', rep_month, rep_year)
            print('res=', res)
            return render_template('report_created.html')
        else:
            return "Repeat input"


@blueprint_report.route('/report-1', methods=['GET', 'POST'])
@group_required
def view_rep1():
    if request.method == 'GET':
        _sql = provider.get('all_reports.sql')
        product_result, schema = select(current_app.config['db_config'], _sql)
        locale.setlocale(locale.LC_ALL, 'ru_RU')
        rep_dates = []
        for product in product_result:
            rep_dates.append(calendar.month_name[product[0]] + " " + str(product[1]))
        return render_template('report_result.html', report_list = rep_dates)
    else:
        rep_name = report_list[1]['rep_name']
        rep_month = request.form.get('rep_date')
        rep_date = rep_month
        rep_month,rep_year = rep_month.split(' ')
        locale.setlocale(locale.LC_ALL, 'ru_RU')
        for index in range (1,13):
            if calendar.month_name[index] == rep_month:
                rep_month = index
                break
        if rep_month and rep_year:
            written_month = calendar.month_name[rep_month]
            _sql = provider.get('report.sql', rep_month=rep_month, rep_year=rep_year)
            product_result, schema = select(current_app.config['db_config'], _sql)
            schema = ("id поставщика","количество товара","стоимость товара")
            if not product_result:
                return "Repeat input"
            return render_template('rep.html', schema=schema, result=product_result, rep_month=written_month, rep_year=rep_year)
        else:
            return "Repeat input"


@blueprint_report.route('/create-report-2', methods=['GET', 'POST'])
@group_required
def create_rep2():
    return render_template("in_future.html")


@blueprint_report.route('/report-2', methods=['GET', 'POST'])
@group_required
def view_rep2():
    return render_template("in_future.html")
