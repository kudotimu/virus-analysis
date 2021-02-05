from datetime import datetime,timedelta,date
from flask import Flask,render_template,request,redirect,make_response
import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import BytesIO
import urllib
import calendar
import os
import matplotlib.dates as mdates

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

#graph
#------------------------------------------------------------
def graph_day(due):
    print('graph_day')
    DATE = 'connect_date'
    cursor.execute('select hour({0}),count(*) from connect_info where date({0})="{1}" group by hour({0});'.format(DATE,due))
    rows = cursor.fetchall()
    return rows
                
def graph_week(year,month,day,week_start_date):
    print('graph_week')
    DATE = 'connect_date'
    week_end_date = week_start_date + timedelta(days=6)
    week_start_str = week_start_date.strftime('%Y-%m-%d')
    week_end_str = week_end_date.strftime('%Y-%m-%d')
        
    cursor.execute('select day({0}),count(*) from connect_info where date({0}) between "{1}" and "{2}" group by day({0});'.format(DATE,week_start_str,week_end_str))
    
    rows = cursor.fetchall()
    return out_comp_week(rows,year,month,day,week_start_date,week_end_date)

def graph_month(year,month):
    print('graph_month')
    DATE='connect_date'
    cursor.execute('select day({0}),count(*) from connect_info where year({0})={1} and month({0})={2} group by day({0});'.format(DATE,year,month))
    rows = cursor.fetchall()

    month_start = date(year,month,1)
    month_end = date(year,month,calendar.monthrange(year,month)[1])
    return out_comp_month(rows,year,month,month_start,month_end)
    
def graph_year(year):
    print('graph_year')
    DATE='connect_date'
    
    cursor.execute('select month({0}),count(*) from connect_info where year({0})={1} group by month({0});'.format(DATE,year))
        
    rows = cursor.fetchall()
    return out_comp_year(1,rows)
#------------------------------------------------------------

#マップ用SQL 国名と件数を返す
#------------------------------------------------------------
remote = 'remote_host != ""'
def map_day(due):

    cursor.execute('select remote_host,count(*) from connect_info where {1} and date(connect_date) = "{0}" group by remote_host order by count(*) desc;'.format(due,remote))
    rows = cursor.fetchall()
    return rows

def map_week(year,month,day,week_start_date):
    print('map_week')
    DATE = 'connect_date'
    week_end_date = week_start_date + timedelta(days=6)
    week_start_str = week_start_date.strftime('%Y-%m-%d')
    week_end_str = week_end_date.strftime('%Y-%m-%d')
        
    cursor.execute('select remote_host,count(*) from connect_info where {3} and date({0}) between "{1}" and "{2}" group by remote_host order by count(*) desc;'.format(DATE,week_start_str,week_end_str,remote))
    
    rows = cursor.fetchall()
    return rows

def map_month(year,month):
    print('map_month')
    DATE='connect_date'
    cursor.execute('select remote_host,count(*) from connect_info where {3} and year({0})={1} and month({0})={2} group by remote_host order by count(*) desc;'.format(DATE,year,month,remote))
    rows = cursor.fetchall()

    return rows
    
def map_year(year):
    print('map_year')
    DATE='connect_date'
    
    cursor.execute('select remote_host,count(*) from connect_info where {2} and year({0})={1} group by remote_host order by count(*) desc;'.format(DATE,year,remote))
        
    rows = cursor.fetchall()
    return rows
#------------------------------------------------------------

#table
#------------------------------------------------------------
def table_day(due):
    print('table_day')
    DATE = 'connect_date'

    cursor.execute("select * from connect_info where date({}) = '{}' limit 100;".format(DATE,due))
    while True:
        rows = cursor.fetchmany(100)
        if not rows:
            break
        for row in rows:
            yield row

def table_week(week_start_date):
    print('table_week')
    DATE = 'connect_date'

    week_end_date = week_start_date + timedelta(days=6)
    week_start_str = week_start_date.strftime('%Y-%m-%d')
    week_end_str = week_end_date.strftime('%Y-%m-%d')
    
    cursor.execute('select * from connect_info where date({0}) between "{1}" and "{2}" limit 100;'.format(DATE,week_start_str,week_end_str))
    while True:
        rows = cursor.fetchmany(100)
        if not rows:
            break
        for row in rows:
            yield row

def table_month(year,month):
    print('table_month')
    DATE = 'connect_date'
    cursor.execute('select * from connect_info where year({0})={1} and month({0})={2} limit 100;'.format(DATE,year,month))
    while True:
        rows = cursor.fetchmany(100)
        if not rows:
            break
        for row in rows:
            yield row

def table_year(year):
    print('table_year')
    DATE = 'connect_date'
    cursor.execute('select * from connect_info where year({0})={1} limit 100;'.format(DATE,year))
    while True:
        rows = cursor.fetchmany(100)
        if not rows:
            break
        for row in rows:
            yield row
#------------------------------------------------------------

#補完
#------------------------------------------------------------
def out_comp_year(cnt,rows):
    x_month = []
    y_month = []
    for row in rows:
        while row[0] != cnt:
            x_month.append(cnt)
            y_month.append(0)
            cnt+=1
        else:
            x_month.append(cnt)
            y_month.append(row[1])
            cnt+=1
    while cnt < 13:
        x_month.append(cnt)
        y_month.append(0)
        cnt+=1

    plot_graph(x_month,y_month)

    rows = comp(x_month,y_month)
    return rows

def out_comp_month(rows,year,month,month_start,month_end):
    x_day = []
    y_day = []
    for row in rows:
        while row[0] != month_start.day:
            x_day.append(month_start.day)
            y_day.append(0)
            month_start += timedelta(days=1)
        else:
            x_day.append(month_start.day)
            y_day.append(row[1])
            month_start += timedelta(days=1)

    while month_start.day != ((month_end+timedelta(days=1)).day):
        x_day.append(month_start.day)
        y_day.append(0)
        month_start += timedelta(days=1)
    
    plot_graph(x_day,y_day)
    
    rows = comp(x_day,y_day)
    return rows

def out_comp_week(rows,year,month,day,week_start,week_end):
    x_day = []
    y_day = []
    for row in rows:
        while row[0] != week_start.day:
            x_day.append(week_start.day)
            y_day.append(0)
            week_start += timedelta(days=1)
        else:
            x_day.append(week_start.day)
            y_day.append(row[1])
            week_start += timedelta(days=1)

    while week_start != ((week_end+timedelta(days=1))):
        x_day.append(week_start.day)
        y_day.append(0)
        week_start += timedelta(days=1)

    plot_graph(x_day,y_day)

    rows = comp(x_day,y_day)
    
    return rows
#------------------------------------------------------------

def plot_graph(x,y):

    plt.figure()
    plt.bar(x,y)
    if os.path.exists('static/graph.png'):
        print(os.path.exists('static/graph.png'))
        os.remove("static/graph.png")
        print("remove")
        plt.savefig("static/graph.png")
    else:
        plt.savefig("static/graph.png")

def comp(x,y):
    rows = [[0]*2 for i in range(len(x))]

    for i in range(len(x)):
        rows[i][0] = str(x[i])
        print(type(x[i])),
        print(x[i])
        rows[i][1] = y[i]
    return rows
