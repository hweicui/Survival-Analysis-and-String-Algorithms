import tkinter as tk
from tkinter import messagebox
from lifelines import CoxPHFitter, KaplanMeierFitter, NelsonAalenFitter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from lifelines.statistics import logrank_test

def data_import(event):
    # 获取文件路径
    file_path = file_entry.get()
    
    data = pd.read_csv(file_path)
    data = data.dropna()

    # 获取持续时间和事件列、性别列、年龄列和分组方式
    duration_column = duration_entry.get()
    event_column = event_entry.get()
    gender_colomn = gender_entry.get()
    age_colomn = age_entry.get()
    group_by = group_by_var.get()

    # 检查持续时间和事件列是否存在
    if duration_column not in data.columns or event_column not in data.columns:
        result_label.config(text='Invalid column name(s).')
        return

    # 按性别分组
    if group_by == 'Gender':
        data1 = data[data[gender_colomn] == 1]
        data2 = data[data[gender_colomn] == 2]
        label1 = 'MALE'
        label2 = 'FEMALE'
    # 按年龄分组
    elif group_by == 'Age':
        data1 = data[data[age_colomn] > 65]
        data2 = data[data[age_colomn] <= 65]
        label1 = 'ELDER'
        label2 = 'YOUNG'

    # 获取用户选择的生存分析方法
    analysis_method = analysis_method_var.get()

    if analysis_method == 'Kaplan-Meier':
        Kaplan_curve(data1, data2, label1, label2)
    elif analysis_method == 'Risk Function':
        Nelson_curve(data1, data2, label1, label2)
    
#分析方式

def Kaplan_curve(data1, data2, label1, label2):
    duration_column = duration_entry.get()
    event_column = event_entry.get()

    kfirst = KaplanMeierFitter()
    kfirst.fit(data1[duration_column], data1[event_column])
    ksecond = KaplanMeierFitter()
    ksecond.fit(data2[duration_column], data2[event_column])

    fig, ax = plt.subplots()
    kfirst.plot(ax=ax, label=label1)
    ksecond.plot(ax=ax, label=label2)

    ax.set_xlabel('Time')
    ax.set_ylabel('Survival Probability')
    ax.set_title('Kaplan-Meier Survival Curve')

    # Perform log-rank test to calculate p-value
    results = logrank_test(data1[duration_column], data2[duration_column], data1[event_column], data2[event_column])
    p_value = results.p_value

    plt.figtext(0.2, 0.02, f"p-value: {p_value:.3f}", ha='left')
    plt.legend()
    plt.show()


def Nelson_curve(data1, data2, label1, label2):
    duration_column = duration_entry.get()
    event_column = event_entry.get()

    nfirst = NelsonAalenFitter()
    nfirst.fit(data1[duration_column], data1[event_column])
    nsecond = NelsonAalenFitter()
    nsecond.fit(data2[duration_column], data2[event_column])

    fig, ax = plt.subplots()
    nfirst.plot(ax=ax, label=label1)
    nsecond.plot(ax=ax, label=label2)

    ax.set_xlabel('Time')
    ax.set_ylabel('Survival Probability')
    ax.set_title('Cumulative hazard')

    # Perform log-rank test to calculate p-value
    results = logrank_test(data1[duration_column], data2[duration_column], data1[event_column], data2[event_column])
    p_value = results.p_value

    plt.figtext(0.2, 0.02, f"p-value: {p_value:.3f}", ha='left')
    plt.legend()
    plt.show()


#指定数据统计
def select_attribute(df):
    attribute = attribute_entry.get()
    selected_column = None
    for column in df.columns:
        if attribute.lower() in column.lower():
            selected_column = column
            break
    return selected_column


def filter_na_values(df, selected_column):
    new_df = df.dropna(subset=[selected_column]).copy()
    return new_df


def calculate_statistics(new_df, selected_column):
    column_data = new_df[selected_column]
    mean = column_data.mean()
    median = column_data.median()
    upper_quartile = column_data.quantile(0.75)
    lower_quartile = column_data.quantile(0.25)
    upper_third = column_data.quantile(0.67)
    lower_third = column_data.quantile(0.33)

    return mean, median, upper_quartile, lower_quartile, upper_third, lower_third


def perform_statistics():
    file_path = file_entry.get()
    data = pd.read_csv(file_path, error_bad_lines=False)
    data = data.dropna()
    df = data
    if df is not None:
        selected_column = select_attribute(df)
        if selected_column is not None:
            new_df = filter_na_values(df, selected_column)
            mean, median, upper_quartile, lower_quartile, upper_third, lower_third = calculate_statistics(new_df, selected_column)
            messagebox.showinfo("Statistics", f"Mean: {mean}\nMedian: {median}\nUpper Quartile: {upper_quartile}\nLower Quartile: {lower_quartile}\nUpper Third: {upper_third}\nLower Third: {lower_third}")

# 创建主窗口
root = tk.Tk()
root.title('Survival Analysis Program')

# 创建文件选择输入框和按钮
file_label = tk.Label(root, text='Select File:')
file_label.pack()
file_entry = tk.Entry(root)
file_entry.pack()

# 创建持续时间和事件列输入框
duration_label = tk.Label(root, text='Duration Column:')
duration_label.pack()
duration_entry = tk.Entry(root)
duration_entry.pack()

event_label = tk.Label(root, text='Event Column:')
event_label.pack()
event_entry = tk.Entry(root)
event_entry.pack()

#创建性别和年龄列输入框
gender_label = tk.Label(root, text='Gender Column:')
gender_label.pack()
gender_entry = tk.Entry(root)
gender_entry.pack()

age_label = tk.Label(root, text='Age Column:')
age_label.pack()
age_entry = tk.Entry(root)
age_entry.pack()

# 创建生存分析方法选择下拉菜单
method_label = tk.Label(root, text='Analysis Method:')
method_label.pack()
analysis_method_var = tk.StringVar()
analysis_method_var.set('Kaplan-Meier')
method_dropdown = tk.OptionMenu(root, analysis_method_var, 'Risk Function', 'Kaplan-Meier')
method_dropdown.pack()

# 分组选择下拉菜单
group_by_var = tk.StringVar(root)
group_by_var.set('Age')  # 默认选择年龄分组
group_by_label = tk.Label(root, text='Group by:')
group_by_label.pack()
group_by_menu = tk.OptionMenu(root, group_by_var, 'Age', 'Gender')
group_by_menu.pack(pady=10)

# 创建属性选择输入框和按钮
attribute_label = tk.Label(root, text='Select Attribute:')
attribute_label.pack()
attribute_entry = tk.Entry(root)
attribute_entry.pack()

#绘图启动按钮
analyze_button = tk.Button(root, text='Perform Analysis')
analyze_button.pack()
analyze_button.bind('<Button-1>', data_import)

# 创建结果标签
result_label = tk.Label(root, text='')
result_label.pack()

# 创建执行按钮
perform_button = tk.Button(root, text='Perform Statistics', command=perform_statistics)
perform_button.pack()

# 运行 GUI 主循环
root.mainloop()