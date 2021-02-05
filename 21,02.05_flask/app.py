from datetime import datetime,timedelta,date
from flask import Flask,render_template,request,redirect,make_response,url_for
import mysql.connector
import numpy as np
#import urllib
import calendar
import os
#import matplotlib.ticker as ticker
import my_graph as my
import geoip2.database
import json
import ipaddress
import pandas as pd

config = {
    'user':'root',
    'password':'Kudotimu72',
    'host':'localhost',
    }

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()


DB_NAME = 'honeypot_logs'
TBL_connect = 'connect_info'

cursor.execute('use {}'.format(DB_NAME))

app = Flask(__name__)

@app.route('/', methods={'GET','POST'})
def index():
    x = [0]
    y = [0]
    if request.method == 'GET':
        due_date = datetime.now().date()
        due_uni = due_date.strftime('%Y-%m-%d')
        period = 'day'
        th_period = 'hour'
        return render_template('index.html',
        period=period,list_x = x,list_y = y,th_period=th_period,due_uni=due_uni)

    else:
        due_uni = request.form.get('due')
        year = int(due_uni[0:4])
        month = int(due_uni[5:7])
        day = int(due_uni[8:10])
        due_date = datetime.strptime(due_uni,'%Y-%m-%d').date()

        status = request.form.get('period')
        if status == 'day':
            rows = my.graph_day(due_uni)
            th_period = 'hour'
        elif status == 'week':
            rows = my.graph_week(year,month,day,due_date)
            th_period = 'day'
        elif status == 'month':
            rows = my.graph_month(year,month)
            th_period = 'day'
        elif status == 'year':
            rows = my.graph_year(year)
            th_period = 'month'
                        
        period = request.form.get('period')

        x = []
        y = []
        print(x,y)

        for row in rows:
            x.append(row[0])
            y.append(row[1])

        x = [int(i) for i in x]
        print(type(x),x)
        print(type(y),y)
        return render_template('index.html',
        period=period,list_x = x,list_y = y,th_period=th_period,due_uni=due_uni)
    
@app.route('/out_table', methods={'GET','POST'})
def out_table():
    if request.method == 'GET':
        table_name = []
        rows_new = []
        period = 'day'
        due_date = datetime.now().date()
        due_uni = due_date.strftime('%Y-%m-%d')
        print(due_uni,type(due_uni))
        return render_template('out_table.html',columns=table_name,rows = rows_new,due_uni = due_uni,period = period)
    else :
        due_uni = request.form.get('due')
        period = request.form.get('period')
        due_list = due_uni.split('-')
        print(due_uni)
        year = int(due_list[0])
        month = int(due_list[1])
        day = int(due_list[2])
        due_date = datetime.strptime(due_uni,'%Y-%m-%d').date()
        reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        cursor.execute('show columns from connect_info;')
        columns = cursor.fetchall()
        
        table_name = []
        column_list = []
        #columns
        for column in columns:
            if 'connect_' in column[0]:
                column_list = column[0].split('_')
                table_name.append(column_list.pop())
            else:
                table_name.append(column[0])
        num = table_name.index('remote_hostname')
        del table_name[num]
        table_name.insert(num,'country')
        
        rows_new = []
        due_list = []
        rows = []
        
        status = request.form.get('period')
        print(status)
        if status == 'day':
            for row in my.table_day(due_uni):
                rows.append(row)
        elif status == 'week':
            for row in my.table_week(due_date):
                rows.append(row)
        elif status == 'month':
            for row in my.table_month(year,month):
                rows.append(row)
        elif status == 'year':
            for row in my.table_year(year):
                rows.append(row)
        
        num_ip = table_name.index('remote_host')
        #date
        for row in rows:
            row_list = list(row)
            if 'p0fconnection' in row:
                continue
            response = reader.city(row[num_ip])
            # print(response.country.name)
            row_list.insert(num+1,response.country.name)
                
            del row_list[num]
            rows_new.append(row_list)
        #print rows_new
            
    return render_template('out_table.html',columns=table_name,rows = rows_new,due_uni = due_uni,period = period)

@app.route('/world_map',methods={'GET','POST'})
def world_map():
    reader = geoip2.database.Reader("GeoLite2-City.mmdb")
    due_uni = request.form.get('due')
    if request.method == 'GET':
        due_date = datetime.now().date()
        due_uni = due_date.strftime('%Y-%m-%d')
        period = 'day'
        countries = []
        connections = []
            
        return render_template('world_map.html',
            countries = countries,connections = connections,connections_max = 0,due_uni = due_uni,period = period)

    else:
        due_uni = request.form.get('due')
        year = int(due_uni[0:4])
        month = int(due_uni[5:7])
        day = int(due_uni[8:10])
        due_date = datetime.strptime(due_uni,'%Y-%m-%d').date()

        status = request.form.get('period')
        if status == 'day':
            rows = my.map_day(due_uni)
            th_period = 'hour'
        elif status == 'week':
            rows = my.map_week(year,month,day,due_date)
            th_period = 'day'
        elif status == 'month':
            rows = my.map_month(year,month)
            th_period = 'day'
        elif status == 'year':
            rows = my.map_year(year)
            th_period = 'month'
                        
        period = request.form.get('period')

        #ipアドレスがプライベートアドレス出ないとき、国名のリストを作る。
        data = [] #list型のin_dataが子のリストを作る

        for row in rows:
            if ipaddress.ip_address(row[0]).is_private:
                continue
            else:
                #response = reader.city(row[0]).country.nameがエラーを吐く可能性があるためtry
                try:
                    response = reader.city(row[0]).country.name
                    #list型のdataを親に持つリストを作る。
                    in_data = []
                    in_data.append(response)
                    in_data.append(row[1])
                    data.append(in_data)
                except:
                    continue

        #重複のない国名と件数のリスト:uniqe_~~
        uniqe_countries = []
        uniqe_connections = []

        for i in data:
            if i[0] not in uniqe_countries:
                uniqe_countries.append(i[0])
                uniqe_connections.append(i[1])
            else:
                num = uniqe_countries.index(i[0])
                uniqe_connections[num] += i[1]

        print(uniqe_countries,uniqe_connections)
        
        if not uniqe_connections:
            connections_max = 0
        else:
            connections_max = max(uniqe_connections)
            print(connections_max)

        df = pd.DataFrame([uniqe_countries,uniqe_connections])
        df.to_csv("pandas_list.csv")

        return render_template("world_map.html",
        countries = uniqe_countries,connections = uniqe_connections,connections_max = connections_max,due_uni = due_uni,period = period)

    

if __name__ == "__main__":
    app.run(debug=True, port=9999)
