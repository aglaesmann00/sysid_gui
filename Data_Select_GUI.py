#%%
"""
Author: Adam Glaesmann
Date: 9/13/2022
"""

import pandas as pd
from tkinter import *
import MySQL_Functions as sql
from HR_Tag import common_text_tags
from tkinter import ttk
import gaps as gaps

#global variables
id_list = []


def selectItem():
    global id_list
    print(id_list)
    for ID in id_list:
        gaps.create_gaps_upload_file(ID)

def l1_callback1(variable_entry):

    '''This function takes the string enered in the yellow box above 
        the left listbox and uses it to search through database columns'''

    criteria1.delete(0,END)
    common_text = variable_entry.get()
    tag_list = common_text_tags(df,common_text)
    criteria1.insert(END, *tag_list)
    return

def l1_callback2(event = None):

    '''This function takes the selected row from the right listbox and 
        displays the item specific database id's in the table below'''

    string = criteria1.get(ANCHOR)

    row_filter.delete(0,END)
    row_filter.insert(0, str(string))

    list = df[string]
    list_no_duplicates = [*set(list)]

    if string == 'Unit':
        list_no_duplicates = sorted(list_no_duplicates)
    elif string == 'Commercial_Approval':
        list_no_duplicates = sorted(list_no_duplicates)
    list_no_duplicates = sorted(list_no_duplicates)
    
    criteria2.delete(0,END)
    criteria2.insert(END, *list_no_duplicates)

    return

def l2_callback1(event = None):
    '''The selected ID from the bottom table is followed up by the append
        button which builds a list of desired id's on the far right'''

    ID_list = df.loc[df[row_filter.get()] == criteria2.get(ANCHOR)]['id'].tolist()
    Unit_list = df.loc[df[row_filter.get()] == criteria2.get(ANCHOR)]['Unit'].tolist()
    Ops_mode_list = df.loc[df[row_filter.get()] == criteria2.get(ANCHOR)]['OPS_MODE'].tolist()
    length_test = len(ID_list)
    tree.delete(*tree.get_children())
    if length_test > 0:
        print('true')
        for index in range(len(ID_list)):
            tree.insert('', 'end', values=([ID_list[index], Unit_list[index], Ops_mode_list[index]]))
    return

def list_append():

    '''This function takes the column tag selected in the left listbox and 
        displays the contents of the rows in the listbox to the right'''

    global id_list
    curItem = tree.focus()
    selected_row = tree.item(curItem)
    if len(selected_row['values']) > 0:
        ID = selected_row['values'][0]
        id_list.append(ID)
        id_LSTBX.delete(0, END)
        for item in id_list:
            id_LSTBX.insert('end', item)

def region_table_change(event = None):

    '''This function uses the option menue to to the left above the bottom 
        table and the selection region will filter the right listbox and the table'''

    global df
    region_selection = table_change.get()
    if region_selection != 'All':
        df = sql.get_curves_by_region(region_selection)
    else:
        df = sql.get_curves_df()
    l1_callback2()
    tree.delete(*tree.get_children())
    return

def remove_var():
    global id_list
    variable = id_LSTBX.get(ANCHOR)
    id_list.remove(variable)
    #delete & rewrite listbox
    id_LSTBX.delete(0, END)
    for item in id_list:
       id_LSTBX.insert('end', item)

root = Tk() #Makes the window
root.wm_title("CurveData Export GUI") #Makes the title that will appear in the top left
root.config(background = "#FFFFFF")
#Left Frame2
top_frame = Frame(root, width=300, height = 250)
top_frame.grid(row=0, column=0, padx=5)

bottom_frame = Frame(root, width=300, height = 200)
bottom_frame.grid(row=1, column=0, padx=5)

right_frame = Frame(root, width = 80, height = 430)
right_frame.grid(row=0, column=1, padx=5, pady=5, rowspan = 2)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=3)

#---------------gui object variables---------------#
variable_entry1 = StringVar()
variable_entry1.trace("w", lambda name, index,mode,var=variable_entry1: l1_callback1(variable_entry1))
variable_entry2 = StringVar()
table_change = StringVar()
#variable_entry2.trace("w", lambda name, index,mode,var=variable_entry1: l2_callback1(variable_entry2))

'''-------------------------------------------------------------------------------'''
'''-----------------------------------TOP FRAME-----------------------------------'''
'''-------------------------------------------------------------------------------'''
column_search=Entry(top_frame, textvariable = variable_entry1)
column_search["bg"] ='#fff6c5'
column_search.pack()
column_search.place(x=15,y=20,width=130,height=25)

row_filter=Entry(top_frame, textvariable = variable_entry2)
row_filter["bg"] ='#fff6c5'
row_filter.pack()
row_filter.place(x=155,y=20,width=130,height=25)

criteria1=Listbox(top_frame)
criteria1.place(x=15,y=45,width=130,height=150)
criteria1.bind("<<ListboxSelect>>", l1_callback2)

criteria2=Listbox(top_frame)
criteria2.place(x=155,y=45,width=130,height=150)
criteria2.bind("<<ListboxSelect>>", l2_callback1)

region_header=Label(top_frame, text = "Region :")
region_header.place(x=0, y=225, width=75, height=25)

region_options = ['ERCOT GAS','PJM GAS','ISO-NE','CAISO','MISO','All']
region_menu = OptionMenu(top_frame, table_change , *region_options, command = region_table_change)
region_menu.place(x=65, y=225, width=100, height=25)
table_change.set('All')

append = Button(top_frame, text = 'Append', command = list_append)
append['bg'] = 'green'
append.place(x=225, y=225, width=75, height=25)


'''-------------------------------------------------------------------------------'''
'''---------------------------------BOTTOM FRAME----------------------------------'''
'''-------------------------------------------------------------------------------'''
# df_view=Button(leftFrame_3, text = 'Add Variable', command = function)
# df_view["bg"] = "#ffff64"
# df_view['wraplength']=60
# df_view.place(x=0,y=0,width=75,height=50)

tree = ttk.Treeview(bottom_frame, column=("c1", "c2", "c3"), show='headings', selectmode='browse', height=8)

vsb = ttk.Scrollbar(bottom_frame, orient="vertical", command=tree.yview)
vsb.place(x=1, y=25, height=160)

tree.configure(yscrollcommand=vsb.set)
#tree.bind('<ButtonRelease-1>', selectItem)

tree.column("# 1", anchor=CENTER, width = 100)
tree.heading("# 1", text="ID")
tree.column("# 2", anchor=CENTER, width = 100)
tree.heading("# 2", text="Unit")
tree.column("# 3", anchor=CENTER, width = 100)
tree.heading("# 3", text="Ops Mode")

tree.columnconfigure(0, weight=3) # column with treeview
tree.rowconfigure(2, weight=1) # row with treeview  
tree.pack(side = 'bottom')

'''-------------------------------------------------------------------------------'''
'''----------------------------------RIGHT FRAME----------------------------------'''
'''-------------------------------------------------------------------------------'''
id_list_header=Label(right_frame, text = "ID's :")
id_list_header.place(x=0,y=0,width=80,height=25)

id_LSTBX=Listbox(right_frame)
id_LSTBX.place(x=2.5,y=30,width=75,height=330)

export = Button(right_frame, text = 'Export', command = selectItem)
export['bg'] = 'green'
export.place(x=5, y=400, width=70, height=25)

remove = Button(right_frame, text = 'Remove', command = remove_var)
remove['bg'] = 'red'
remove.place(x=5, y=370, width=70, height=25)


#automatically defining dataframe and showing columns in list before any action from user is made
global df
df = sql.get_curves_df()
common_text = variable_entry1.get()
tag_list = common_text_tags(df,common_text)
criteria1.insert(END, *tag_list)

root.mainloop()
# %%