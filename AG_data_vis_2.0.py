# %%
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 15:11:27 2022

@author: Adam Glaesmann
"""
import copy
from tkinter import *
import threading
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import tkinter.font as tkFont
from tkcalendar import DateEntry
from tkinter.filedialog import asksaveasfile

import data_vis_support as DVS



#global definitions
filename = ''
filename_memory = []
stack = []
data_filtered = []
var_list = []
fac_list = []
zoom = FALSE
starting_date = "2020-01-01 00:00:00"


#_____________________________________THREADS_____________________________________
def thread_select_file():
    threading.Thread(target=select_file).start()
def thread_export():
    threading.Thread(target=save).start()
def thread_plot_all():
    filter_BTTN['state'] = DISABLED
    threading.Thread(target=plot_all).start()
    filter_BTTN['state'] = NORMAL
def thread_contrast():
    filter_BTTN['state'] = DISABLED
    threading.Thread(target=contrast).start()
    filter_BTTN['state'] = NORMAL
def thread_corr_plot():
    threading.Thread(target=correlate).start()
def thread_regress():
    threading.Thread(target=regress).start()
def thread_drop():
    threading.Thread(target=drop).start()

#_____________________________________SUPPORT DEPENDANT FUNCTIONS_____________________________________
def select_file():
    global filename
    global data_filtered
    global stack
    global filename_memory
    stack = []
    data_filtered = []
    filetypes = (('data files', '*.csv'),('All files', '*.*'))
    filename = fd.askopenfilename(title='Open a file',initialdir='/',filetypes=filetypes)
    showinfo(title='Selected File', message=filename)
    if filename == '' and len(filename_memory) == 0:
        print('no file chosen')
    elif filename == '' and len(filename_memory) != 0:
        filename = filename_memory[-1]
        print('no file chosen')
    elif filename != '' and len(filename_memory) == 0:
        filename_memory.append(filename)
    else:
        filename_memory.remove(filename_memory[0])
        filename_memory.append(filename)
    if filename:
        #create df and filter NA
        df = DVS.read_to_df(filename)
        #add TimeConverted Column
        #df['TimeConverted'] = df['Time'].apply(DVS.df_add_timeconverted)
        #add HRSG Efficiency
        #df['HRSG2_Eta'] = DVS.df_add_HRSG_Eta(df)
        #updating GUI and notifying user
        file_split = filename.split('/')
        file_LBL['text'] = file_split[-1]
        #Stack_LBL['text'] = 'Stack = %s' %(len(stack))
        stack.append(df)
        print('You Are Ready To Begin')

def reset():
    global stack
    global data_filtered
    if len(stack) == 1 or len(stack) == 0:
        print('no data file detected')
    else:
        stack = []
        data_filtered = []
        #create df and filter NA
        df = DVS.read_to_df(filename)
        #add TimeConverted Column
        df['TimeConverted'] = df.apply(lambda x: DVS.timeToFloat(x['TimeStamp'],starting_date))
        #updating GUI and notifying user
        file_split = filename.split('/')
        file_LBL['text'] = file_split[-1]
        Stack_LBL['text'] = 'Stack = %s' %(len(stack))
        filter_list_LBL['text'] = ''
        stack.append(df)
        print('You Are Ready To Begin')

def info():
    global stack
    global var_list
    if len(stack) == 0:
        print('no data file detected')
    else:
        #collect relevant objects
        df = stack[-1]
        #create dataframe for review
        database = DVS.to_database(df,var_list)
        #print dataframe info
        DVS.print_info(database,filename)
        print('done')

def plot():
    global stack
    if len(stack) == 0:
        print('no data file detected')
    else:
        df = stack[-1]        
        x_axis = x_entry.get()
        y_axis = y_entry.get()
        DVS.xy_plot(df,x_axis,y_axis)
        print('plot complete')

def plot_all():
    global stack
    global var_list
    if len(stack) == 0:
        print('no data file detected')
    else:
        df = stack[-1]
        #scatter plot
        DVS.scatter_plot(df,var_list)
        print('plotting complete')

def drop():
    global stack
    global data_filtered
    
    if len(stack) == 0:
        print('no data file detected')
    else:
        #collect relevant objects
        min_val_str = min_entry.get()
        max_val_str = max_entry.get()
        column = select_var_entry.get()
        df = stack[-1]
        #filtering (min and max arguments as strings)
        if min_val_str != '':
            if min_val_str == '0':
                min_val = 0
            else:
                min_val = float(min_val_str)
            #try:
            #except:
        else:
            if min_val_str == '':
                min_val = False
            print('invalid filter')

        if max_val_str != '':
            if max_val_str == '0':
                max_val = 0
            else:
                max_val = float(max_val_str)
        else:
            if max_val_str == '':
                max_val = False
            print('invalid filter')
        
        df_new, data_filtered = DVS.filter(df,column,min_val,max_val,data_filtered)
        #updating GUI and notifying user
        stack.append(df_new)
        Stack_LBL['text'] = 'Stack = %s' %(len(stack))
        filter_list_LBL['text'] = ''
        for n_filter in data_filtered:
             filter_list_LBL['text'] += '\n%s' %(n_filter)

def contrast():
    global stack
    global var_list
    if len(stack) == 0:
        print('no data file detected')
    else:
        #collect relevant objects
        df = stack[-1]
        column = select_var_entry.get()
        
        min_val_str = min_entry.get()
        max_val_str = max_entry.get() 
        #contrast plot
        DVS.contrast_plot(df,column,var_list,min_val_str,max_val_str)
        print('contrast plotting complete')

def correlate():
    global stack
    global fac_list
    if len(stack) == 0:
        print('no data file detected')
    else:
        #collect relevant objects
        df = stack[-1]
        product = product_entry.get()
        #corrolation plot
        DVS.corrolation_plot(df,fac_list,product)
        print('heatmap complete')

def regress():
    global stack
    global fac_list
    if len(stack) == 0:
        print('no data file detected')
    else:
        df = stack[-1]
        product_str = product_entry.get()
        reg_choice = regress_list.get(ANCHOR)
        results = DVS.create_model(df,fac_list,product_str,reg_choice)
        print('task complete')

#_____________________________________GUI INDEPENDENT FUNCTIONS_____________________________________
def zoom():
    global zoom
    zoom = TRUE
    try:
        drop()
        plot()
        undo()
    except:
        print('error: no plot to zoom')
        undo()
    zoom = FALSE

def undo():
    global stack
    global data_filtered
    if len(stack) == 1 or len(stack) == 0:
        print('there is nothing to undo')
    else:
        if len(stack) > 1:
            stack.pop()
            if data_filtered != []:
                data_filtered.pop()
                
        filter_list_LBL['text'] = ''
        for n_filter in data_filtered:
                filter_list_LBL['text'] += '\n%s' %(n_filter)
        Stack_LBL['text'] = 'Stack = %s' %(len(stack))

def save():
    global stack
    if len(stack) == 0:
        print('no data file detected')
    else:
        df = stack[-1]
        files = [('All Files', '*.*'), 
                 ('Python Files', '*.py'),
                 ('Text Document', '*.csv')]
        file = asksaveasfile(filetypes = files, defaultextension = files)
        if file:
            df.to_csv(file, index=False, line_terminator='\n')
            print('export complete')
        else:
            print('error')
        filter_list_LBL['text'] = ''

def to_var_list():
    global var_list
    variable = search_LSTBX.get(ANCHOR)
    variable_LSTBX.delete(0, END)
    if variable in var_list:
        print('duplicate tag')
    else:
        var_list.append(variable)
    for item in var_list:
       variable_LSTBX.insert('end', item)

def to_fac_list():
    global fac_list
    variable = search_LSTBX.get(ANCHOR)
    factor_LSTBX.delete(0, END)
    if variable in fac_list:
        print('duplicate tag')
    else:
        fac_list.append(variable)
    for item in fac_list:
       factor_LSTBX.insert('end', item)

def to_x_entry():
    variable = search_LSTBX.get(ANCHOR)
    x_axis.delete(0,END)
    x_axis.insert(0, str(variable))

def to_y_entry():
    variable = search_LSTBX.get(ANCHOR)
    y_axis.delete(0,END)
    y_axis.insert(0, str(variable))

def clear_plotting():
    global var_list
    var_list = []
    variable_LSTBX.delete(0, END)
    x_axis.delete(0,END)
    y_axis.delete(0,END)

def clear_modeling():
    global fact_list
    fac_list = []
    factor_LSTBX.delete(0, END)
    product.delete(0,END)

def remove_var():
    global var_list
    variable = variable_LSTBX.get(ANCHOR)
    var_list.remove(variable)
    #delete & rewrite listbox
    variable_LSTBX.delete(0, END)
    for item in var_list:
       variable_LSTBX.insert('end', item)

def remove_fac():
    global fac_list
    variable = factor_LSTBX.get(ANCHOR)
    fac_list.remove(variable)
    #delete & rewrite listbox
    factor_LSTBX.delete(0, END)
    for item in fac_list:
       factor_LSTBX.insert('end', item)

def copy_var():
    global var_list
    global fac_list
    fac_list = copy.copy(var_list)
    factor_LSTBX.delete(0, END)
    for item in var_list:
       factor_LSTBX.insert('end', item)

#_____________________________________AUTOMATIC EVENT FUNCTIONS_____________________________________
def callback1(variable_entry):
    global stack
    if len(stack)!=0:
        df = stack[-1]
        search_LSTBX.delete(0,END)
        common_text = variable_entry.get()
        tag_list = DVS.common_text_tags(df,common_text)
        search_LSTBX.insert(END, *tag_list)
    return

def callback2(event = None):
    variable = search_LSTBX.get(ANCHOR)
    select_var.delete(0,END)
    select_var.insert(0, str(variable))
    return


#_____________________________________GUI STRUCTURE_____________________________________
root = Tk() #Makes the window
root.wm_title("Data Visualization Tool") #Makes the title that will appear in the top left
root.config(background = "#FFFFFF")

#Left Frame2
leftFrame_1 = Frame(root, width=350, height = 50)
leftFrame_1.grid(row=0, column=0, padx=5, pady=5, columnspan = 3)

leftFrame_2 = Frame(root, width=130, height = 220)
leftFrame_2.grid(row=1, column=0, padx=5, pady=5)

leftFrame_3 = Frame(root, width=200, height = 220)
leftFrame_3.grid(row=1, column=1, padx=5, pady=5)

leftFrame_4 = Frame(root, width=350, height = 70)
leftFrame_4.grid(row=3, column=0, padx=5, pady=5, columnspan = 2)

leftFrame_5 = Frame(root, width=350, height = 220)
leftFrame_5.grid(row=4, column=0, padx=5, pady=5, columnspan = 2)

rightFrame_1 = Frame(root, width=200, height = 50)
rightFrame_1.grid(row=0, column=3, padx=10, pady=10)

rightFrame_2 = Frame(root, width=200, height = 220)
rightFrame_2.grid(row=1, column=3, padx=10, pady=10)


#_____________________________________USER VARIABLES_____________________________________
variable_entry = StringVar()
variablelist_entry = StringVar()
variable_entry.trace("w", lambda name, index,mode,var=variable_entry: callback1(variable_entry))
x_entry = StringVar()
y_entry = StringVar()
min_entry = StringVar()
select_var_entry = StringVar()
max_entry = StringVar()
factors_entry = StringVar()
product_entry = StringVar()

# #_____________________________________INTRO_____________________________________

open_BTTN = Button(leftFrame_1,text='Open a File',command=thread_select_file)
open_BTTN.place(x=0,y=0,width=200,height=25)

date_LBL=Label(leftFrame_1, text = 'Start Date :')                                 
date_LBL.place(x=200,y=0,width=75,height=25)

start_date = DateEntry(leftFrame_1, selectmode = 'day', year = 2019, month = 1, day = 1)
start_date.place(x=275,y=0,width=75,height=25)

file_LBL=Label(leftFrame_1, text = '',  anchor='w')                                 
file_LBL.place(x=0,y=25,width=350,height=25)

#_____________________________________SEARCH_____________________________________
search_LBL=Label(leftFrame_2, text = 'Search', font='bold')
search_LBL["bg"] = "yellow"                                 
search_LBL.place(x=0,y=0,width=130,height=20)

variable=Entry(leftFrame_2, textvariable = variable_entry)
variable["bg"] ='#fff6c5'
variable.pack()
variable.place(x=0,y=20,width=130,height=25)

search_LSTBX=Listbox(leftFrame_2)
search_LSTBX.place(x=0,y=45,width=130,height=100)
search_LSTBX.bind("<<ListboxSelect>>", callback2)

add_x_BTTN=Button(leftFrame_2, text = 'x', command = to_x_entry)
add_x_BTTN["bg"] = "#e0e05b"
add_x_BTTN.place(x=0,y=145,width=65,height=25)

add_y_BTTN=Button(leftFrame_2, text = 'y', command = to_y_entry)
add_y_BTTN["bg"] = "#e0e05b"
add_y_BTTN.place(x=65,y=145,width=65,height=25)

add_var_BTTN=Button(leftFrame_2, text = 'Add Variable', command = to_var_list)
add_var_BTTN["bg"] = "#ffff64"
add_var_BTTN['wraplength']=60
add_var_BTTN.place(x=0,y=170,width=65,height=50)

add_fac_BTTN=Button(leftFrame_2, text = 'Add Factor', command = to_fac_list)
add_fac_BTTN["bg"] = "#ffff64"
add_fac_BTTN['wraplength']=50
add_fac_BTTN.place(x=65,y=170,width=65,height=50)

#_____________________________________PLOT_____________________________________
Plotting_LBL=Label(leftFrame_3, text = 'Plotting', font='bold')
Plotting_LBL["bg"] = "#05e323"                                 
Plotting_LBL.place(x=0,y=0,width=200,height=20)

variables_LBL=Label(leftFrame_3, text = 'Variables :')
variables_LBL["bg"] = "#43ab4a"                                 
variables_LBL.place(x=0,y=20,width=120,height=25)

variable_LSTBX=Listbox(leftFrame_3)
variable_LSTBX.place(x=0,y=45,width=120,height=100)
#variable_list.bind("<<ListboxSelect>>", callback2)

remove_BTTN=Button(leftFrame_3, text = 'Remove', command = remove_var)
remove_BTTN["bg"] = "#3aed46"
remove_BTTN.place(x=0,y=145,width=120,height=25)

clear1_BTTN=Button(leftFrame_3, text = 'clear', command = clear_plotting)
clear1_BTTN["bg"] = "#3aed46"
clear1_BTTN.place(x=120,y=20,width=80,height=50)

plot_all_BTTN=Button(leftFrame_3, text = 'Plot All', command = thread_plot_all)
plot_all_BTTN["bg"] = "#3aed46"
plot_all_BTTN.place(x=120,y=70,width=80,height=50)

plot_BTTN=Button(leftFrame_3, text = 'X/Y Plot', command = plot)
plot_BTTN["bg"] = "#3aed46"
plot_BTTN.place(x=120,y=120,width=80,height=50)

x_LBL=Label(leftFrame_3, text = 'X :')
x_LBL["bg"] = "#43ab4a"                                 
x_LBL.place(x=0,y=170,width=60,height=25)

x_axis=Entry(leftFrame_3, textvariable = x_entry)
x_axis["bg"] = '#90e495'
x_axis.place(x=60,y=170,width=140,height=25)

y_LBL=Label(leftFrame_3, text = 'Y :')
y_LBL["bg"] = "#43ab4a"                                 
y_LBL.place(x=0,y=195,width=60,height=25)

y_axis=Entry(leftFrame_3, textvariable = y_entry)
y_axis["bg"] = '#90e495'
y_axis.place(x=60,y=195,width=140,height=25)

# #_____________________________________DATA MANIPULATION_____________________________________
filter_LBL=Label(leftFrame_4, text = 'Data Manipulation', font='bold')                    
filter_LBL["bg"] = "blue"                     
filter_LBL["fg"] = "#ffffff"            
filter_LBL.place(x=0,y=0,width=350,height=20)

minn=Entry(leftFrame_4, textvariable = min_entry)
minn["bg"] = '#b7caff'                               
minn.place(x=0,y=20,width=70,height=25)

character1_LBL=Label(leftFrame_4, text = '<')
character1_LBL["bg"] = '#447ef2'                                 
character1_LBL.place(x=70,y=20,width=43.75,height=25)

select_var=Entry(leftFrame_4, textvariable = select_var_entry)   
select_var["bg"] = '#b7caff'                            
select_var.place(x=113.75,y=20,width=122.5,height=25)

character2_LBL=Label(leftFrame_4, text = '<')   
character2_LBL["bg"] = '#447ef2'                              
character2_LBL.place(x=236.25,y=20,width=43.75,height=25)

maxx=Entry(leftFrame_4, textvariable = max_entry)
maxx["bg"] = '#b7caff'                               
maxx.place(x=280,y=20,width=70,height=25)

filter_BTTN=Button(leftFrame_4, text = 'Filter', command = thread_drop)
filter_BTTN["bg"] = "#3b3bfe"
filter_BTTN["fg"] = "#ffffff"
filter_BTTN.place(x=0,y=45,width=87.5,height=25)

zoom_BTTN=Button(leftFrame_4, text = 'Zoom', command = zoom)
zoom_BTTN["bg"] = "#3b3bfe"
zoom_BTTN["fg"] = "#ffffff"
zoom_BTTN.place(x=87.5,y=45,width=87.5,height=25)

contrast_BTTN=Button(leftFrame_4, text = 'Contrast', command = thread_contrast)
contrast_BTTN["bg"] = "#3b3bfe"
contrast_BTTN["fg"] = "#ffffff"
contrast_BTTN.place(x=175,y=45,width=87.5,height=25)

undo_BTTN=Button(leftFrame_4, text = 'Undo', command = undo)
undo_BTTN["bg"] = "#3b3bfe"
undo_BTTN["fg"] = "#ffffff"
undo_BTTN.place(x=262.5,y=45,width=87.5,height=25)

# #_____________________________________MODELING_____________________________________
modeling_LBL=Label(leftFrame_5, text = 'Modeling',font='bold')
modeling_LBL["bg"] = "red"  
modeling_LBL["fg"] = "#ffffff"              
modeling_LBL.place(x=0,y=0,width=350,height=20)

factors_LBL=Label(leftFrame_5, text = 'Factors :')
factors_LBL["bg"] = "#cf5b5b"                                 
factors_LBL.place(x=0,y=20,width=120,height=25)

factor_LSTBX=Listbox(leftFrame_5)
factor_LSTBX.place(x=0,y=45,width=120,height=100)

remove2_BTTN=Button(leftFrame_5, text = 'Remove', command = remove_fac)
remove2_BTTN["bg"] = "#fc4949"
remove2_BTTN.place(x=0,y=145,width=120,height=25)

product_LBL=Label(leftFrame_5, text = 'Product :')
product_LBL["bg"] = "#cf5b5b"                                 
product_LBL.place(x=120,y=20,width=120,height=25)

product=Entry(leftFrame_5, textvariable = product_entry)
product["bg"] = '#f8aaaa'
product.place(x=120,y=45,width=120,height=25)

clear2_BTTN=Button(leftFrame_5, text = 'Clear', command = clear_modeling)
clear2_BTTN["bg"] = "#fc4949"
clear2_BTTN.place(x=120,y=70,width=120,height=25)

copy_BTTN=Button(leftFrame_5, text = 'Copy Variables', command = copy_var)
copy_BTTN["bg"] = "#fc4949"
copy_BTTN.place(x=120,y=95,width=120,height=25)

correlate_BTTN=Button(leftFrame_5, text = 'Corrolate', command = thread_corr_plot)
correlate_BTTN["bg"] = "#fc4949"
correlate_BTTN.place(x=120,y=120,width=120,height=25)

regress_BTTN=Button(leftFrame_5, text = 'Regress', command = thread_regress)
regress_BTTN["bg"] = "#fc4949"
regress_BTTN.place(x=120,y=145,width=120,height=25)

model_info_LBL=Label(leftFrame_5, text = 'Model Info :')
model_info_LBL["bg"] = "#cf5b5b"                                 
model_info_LBL.place(x=240,y=20,width=110,height=25)

model_info_box_LBL=Label(leftFrame_5, text = '')
model_info_box_LBL["bg"] = "#cf5b5b"                                 
model_info_box_LBL.place(x=240,y=20,width=110,height=25)

regress_list=Listbox(leftFrame_5)
regress_list.insert(1, "LinearRegression")
regress_list.insert(2, "GradientBoostingRegressor")
regress_list.insert(3, "MLPRegressor")
regress_list.place(x=0,y=170,width=240,height=75)

model_info_LBL=Label(leftFrame_5, text = '')
model_info_LBL["bg"] = "#f8aaaa"                                 
model_info_LBL.place(x=240,y=170,width=110,height=75)

# #_____________________________________END_____________________________________
reset_BTTN=Button(rightFrame_1, text = 'Reset', command = reset)
reset_BTTN.place(x=0,y=0,width=60,height=25)

info_BTTN=Button(rightFrame_1, text = 'More Info', command = info)
info_BTTN.place(x=60,y=0,width=60,height=25)

save_BTTN = Button(rightFrame_1, text = 'Export', command = lambda : thread_export())
save_BTTN.place(x=120,y=0,width=80,height=25)

# add_info_LBL=Label(rightFrame_1, text = 'Additional Info', font='bold')                              
# add_info_LBL.place(x=0,y=25,width=200,height=25)

# #_____________________________________ADDITIONAL INFO_____________________________________
filter_LBL=Label(rightFrame_2, text = 'Data Filters : ', font='bold')                              
filter_LBL.place(x=0,y=0,width=200,height=25)

filter_list_LBL=Label(rightFrame_2, text = '', anchor = 'n')
filter_list_LBL["bg"] = "#ffffff"                                 
filter_list_LBL.place(x=5,y=25,width=190,height=150)

Stack_LBL=Label(rightFrame_2, text = 'Stack =', anchor = 'w')
Stack_LBL["bg"] = "#ffffff"                                 
Stack_LBL.place(x=5,y=195,width=190,height=20)

root.mainloop()

# %%
