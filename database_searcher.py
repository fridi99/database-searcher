"""
explanation of used libraries:
functools -> partial: allows iterative implementation
of functions with different parameters.
Used to allow multiple "copy to clipboard" buttons
tkinter: creates the User Interface
pyodbc: used to connect to a Microsoft access database and read using SQL query
    """

from functools import partial
import tkinter as tk
from tkinter import ttk
import pyodbc


def on_configure(event):
    """
    function used by tkinter object to enable scrolling through results.
    Should not be called except through a .bind function.
    Sets Scroll-region
    :param event: the event being passed by .bind
    :return: none
    """
    result_canvas.configure(scrollregion=result_canvas.bbox("all"))


def on_mousewheel(event):
    """
        function used by tkinter object to enable scroling through results.
        Should not be called except through a .bind function
        :param event: the event being passed by .bind
        :return: none
        """
    result_canvas.yview_scroll(-1 * (event.delta // 120), "units")


def convert_to_float(value):
    """
    takes a value as would be present in the database and turns it into the
    actual value. Example 10.2k -> 10_200
    V is also an option, because Capacitors have the Voltage rating given with
    V, so it needs to be handled # TODO find a nicer solution
    :param value: the value to be converted
    :type value: str
    :return: returns the actual number
    :rtype: float
    """
    if not isinstance(value, str):
        raise ValueError("please only pass strings to this function")
    converter_dict = {"k": 1000, "M": 1_000_000, "m": 0.001, "u": 0.00_000_1
                      , "n": 0.00_000_000_1, "p": 0.00_000_000_000_1,
                      "f": 0.00_000_000_000_000_1, "V": 1
                     }
    number_str = ""
    multiplier = 1
    for i in value:
        if i.isdigit() or i == ".":  # TODO handle strings with >1 periods
            number_str += i
        if i in converter_dict:
            multiplier = converter_dict[i]
    return float(number_str) * multiplier

def parameter_comparator(component_parameter_list):
    """
    The parameter_comparator function checks if a given component,
    whose parameters are represented by "component_parameter_list",
    matches the requirements set by the user
    There are newly implemented options/operators:
    >val all parts where value is greater than val
    <val all parts where value is less than val
    val1+-val2 all parts where value is within val2 of val1
    :param component_parameter_list: the components parameters represented
    by a row from the corresponding document
    :type component_parameter_list: list
    :return: False if any chosen parameter is not as requested by user,
    True if all are
    :rtype: Bool
    """

    try:
        _ = iter(component_parameter_list)
    except TypeError:
        raise TypeError("Function input must be an iterable object")
    if type(component_parameter_list) is str:
        raise TypeError("Do not pass strings to this function")
    if len(component_parameter_list) == 0:
        raise ValueError("Input must be non-empty")
    if tab_parent is None:
        raise NameError("Function called before parent tab defined")

    if tab_parent.index('current') == 0:
        database_dict = database_dict_resistors
        entry_list = entrylist_res
        parameter_list = list(database_dict_resistors)
    elif tab_parent.index('current') == 1:
        database_dict = database_dict_capacitors
        entry_list = entrylist_cap
        parameter_list = list(database_dict_capacitors)
    elif tab_parent.index('current') == 2:
        database_dict = database_dict_ICs
        entry_list = entrylist_IC
        parameter_list = list(database_dict_ICs)
    elif tab_parent.index('current') == 3:
        database_dict = database_dict_connectors
        entry_list = entrylist_con
        parameter_list = list(database_dict_ICs)
    else:   # should not happen, in case it does I'll know >:)
        raise IndexError("Tab Index out of Range!")

    for _ite in range(len(entry_list)):
        if str(entry_list[_ite][0].get()) == '':
            continue
        # loops over all values entered in the UI fields
        if component_parameter_list[list(database_dict.values())[_ite]] == 'x':
            print(f"for part {component_parameter_list[0]} {parameter_list[_ite]} "
                  f"is undefined in database and will be skipped")
            return False
        if int(entry_list[_ite][1].get()) == 1:
            # checks against the no whole entry checkbox.
            # If not checked the entry has to be the exact same.
            # If not the value has to only be present anywhere in the string
            if component_parameter_list[list(database_dict.values())[_ite]].\
                    find(entry_list[_ite][0].get()) == -1:
                return False
        else:
            entry_str = str(entry_list[_ite][0].get())
            less = str(entry_list[_ite][0].get()).find("<")
            more = str(entry_list[_ite][0].get()).find(">")
            pm = str(entry_list[_ite][0].get()).find("+-")
            if (not (less != -1) ^ (more != -1) ^ (pm != -1)) and \
                    not (less == -1 and more == -1 and pm == -1):
                print("please do not enter more than one operator (<, >, +-)"
                      "into the entry box")
                return False
            if less != -1:
                split_str = entry_str.split("<")
                if len(split_str[0]) == 0:
                    if not (convert_to_float(component_parameter_list
                            [list(database_dict.values())[_ite]])
                            <= convert_to_float((split_str[1]))):
                        return False
                elif len(split_str[1]) == 0:
                    if not ((convert_to_float(split_str[0])
                            <= convert_to_float(component_parameter_list
                            [list(database_dict.values())[_ite]]))):
                        return False
                elif not (convert_to_float(split_str[0])
                        <= convert_to_float(component_parameter_list
                        [list(database_dict.values())[_ite]])
                        <= convert_to_float((split_str[1]))):
                    return False
            if more != -1:
                split_str = entry_str.split(">")
                if len(split_str[0]) == 0:
                    if not (convert_to_float(component_parameter_list
                            [list(database_dict.values())[_ite]])
                            >= convert_to_float((split_str[1]))):
                        return False
                elif len(split_str[1]) == 0:
                    if not ((convert_to_float(split_str[0])
                            >= convert_to_float(component_parameter_list
                            [list(database_dict.values())[_ite]]))):
                        return False
                elif not (convert_to_float(split_str[0])
                        >= convert_to_float(component_parameter_list
                        [list(database_dict.values())[_ite]])
                        >= convert_to_float((split_str[1]))):
                    return False
            if pm != -1:
                split_str = entry_str.split("+-")
                if (len(split_str[0]) == 0) or (len(split_str[1]) == 0):
                    print("The +- operator is only functional with values "
                          "before and after the operator")
                    return False
                elif not (convert_to_float(split_str[0])
                          - convert_to_float(split_str[1]) <=
                          convert_to_float(component_parameter_list
                          [list(database_dict.values())[_ite]]) <=
                          (convert_to_float(split_str[0]) +
                          convert_to_float(split_str[1]))):
                    return False
            if less == -1 and more == -1 and pm == -1:
                if str(component_parameter_list[list(database_dict.values())[_ite]])\
                        != str(entry_list[_ite][0].get()) \
                        and len(entry_list[_ite][0].get()) != 0:
                    return False
    return True


def row_creator(row_label, example_text, _row_nr, tab, entrytype="text"):
    """
    creates a row for the tkinter main object and adds it.
    The row contains a label with the name of the parameter that is being read,
    the input box itself and a checkbox that determines, when left
    unchecked that the entered value and component value is exactly the same
    or if checked only that searched value is anywhere in relevant parameter
    entry
    :param row_label: String, sets Label of row
    :param example_text: String, added as example for values
    :param _row_nr: int, determines i which row of the tkinter grid object the
    row is placed
    :param tab: tkinter Frame, the tab in which the row should be palced
    :return: returns a list containing the Input box created (entry) and value
    of "not whole entry?" checkbox (var)
    """
    if not isinstance(row_label, str):
        raise ValueError("row_label has to be a string")
    if not isinstance(example_text, str):
        raise ValueError("example_text has to be a string")
    if not isinstance(_row_nr, int):
        raise ValueError("_row_nr has to be an integer")
    label1 = ttk.Label(tab, text=f"{row_label}:")
    label1.grid(column=0, row=_row_nr, sticky=tk.W, padx=5, pady=5)
    if entrytype == "text":
        entry = tk.Entry(tab, width=20)
    elif entrytype == "dropdown":
        menubutton = tk.Menubutton(tab, text="Choose Entries", indicatoron=True,
                                   borderwidth=1, relief="raised")
        entry = tk.Menu(menubutton, tearoff=False)
    entry.grid(column=1, row=_row_nr, sticky=tk.W, padx=5, pady=5)
    var = tk.IntVar()
    tk.Checkbutton(tab, text="not whole entry?", variable=var).\
        grid(row=_row_nr, column=2)
    label2 = ttk.Label(tab, text=f"{example_text}")
    label2.grid(column=3, row=_row_nr, sticky=tk.W, padx=5, pady=5)
    return [entry, var]


def multi_dropdown_row_creator(row_label, _row_nr, tab):
    """

    :param row_label:
    :param _row_nr:
    :param tab:
    :return:
    """


def copy_to_cb(text):
    """
    Function to take the text provided and copy it to clipboard. used to copy
    component ID to clipboard
    :param text: the string to be copied to clipboard
    :type text: string
    :return: No return
    """
    if not isinstance(text, str):
        raise ValueError("Please only pass a string to this function")
    tk_window.clipboard_clear()
    tk_window.clipboard_append(text)


def search():
    """
    performs all necessary functions to search database according to
    inputs and adds up to ten rows with results to the tkinter window
    :return: none
    """
    for element in tk_window.grid_slaves():
        if int(element.grid_info()["row"]) >= row_nr + 2:
            element.destroy()
    for element in frame_for_canvas.winfo_children():
        element.destroy()
    resultlist = []
    for row in data_from_db[tab_parent.index('current')]:
        if parameter_comparator(row):
            resultlist.append([row[0], row[2], row[12]])
    for _ite, _result_elem in enumerate(resultlist):
        if _ite >= 100:
            break
        button = tk.Button(frame_for_canvas, text="copy to clipboard",
                           command=partial(copy_to_cb, _result_elem[0]))
        button.grid(column=0, row=row_nr + 2 + _ite)
        button.bind("<MouseWheel>", on_mousewheel)
        label = tk.Label(frame_for_canvas, text=f"{_result_elem[0]}:{_result_elem[1]} "
                                 f"{_result_elem[2]}", font="Times 10")
        label.grid(column=1, row=row_nr + 2 + _ite, columnspan=2, sticky="W")
        label.bind("<MouseWheel>", on_mousewheel)
        result_canvas.yview_moveto(0.0)
    if len(resultlist) == 0:
        label = tk.Label(frame_for_canvas, text="No results found for given "
                                                "values", font="Times 14")
        label.grid(column=0, row=row_nr + 2, columnspan=3, sticky="EW")
    result_canvas.yview_moveto(0.0)


###############################################################################
# setting up Labels and Values for queried parts
###############################################################################
"""setting of values to be queried for component type and index 
in database for each"""
table_names = ["Resistors$", "Capacitors$", "IC$", "Connectors$"]
example_list_resistors = ["10.2k", "0805", "0.125", "50", "0.1"]
example_list_capacitors = ["100p", "0805", "50V", "0.1"]
database_dict_resistors = {"Value": 1, "Casecode": 12, "Powerrating": 7, "Voltage": 8, "Tolerance": 9}
database_dict_ICs = {"Description": 10, "Casecode": 12, "MPN": 13}
database_dict_capacitors = {"Value": 1, "Casecode": 12, "Voltage": 7, "Tolerance": 9}
database_dict_connectors = {"contacts": 8, "Gender": 7, "Current": 9, "Package Type": 11}
###############################################################################
# fetching the access database tables given lists defined above
###############################################################################
data_from_db = []
db_connect_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};" \
             r"Dbq=.\database_file\database_searcher_test_database.accdb;"
conn = pyodbc.connect(db_connect_str)
cursor = conn.cursor()
part_list = []
for table_name in table_names:
    cursor.execute(f"SELECT [{table_name}].* FROM [{table_name}]")
    data_from_db.append(cursor.fetchall())
cursor.close()
conn.close()
casecode_list = [[], []]
###############################################################################
# initializing the tkinter object and dependencies
###############################################################################
tk_window = tk.Tk()
tk_window.geometry("500x500")
tk_window.title("Database searcher")
tk_window.resizable(True, True)
# in truth the window doesn't have to be resizable
tab_parent = ttk.Notebook(tk_window)

entrylist_res, entrylist_cap, entrylist_IC, entrylist_con, row_nr = [], [], [], [], 2
# the entry lists contain the entry object used to pass values and the value
# itself. This is used to fetch them. row_nr is an iterator so each row can be
# written sequentially.

tab_resistors = ttk.Frame(tab_parent)
# creates resistor tab in tkinter object
tab_capacitors = ttk.Frame(tab_parent)
# creates capacitor tab in tkinter object
tab_ICs = ttk.Frame(tab_parent)
# creates IC tab in tkinter object
tab_connectors = ttk.Frame(tab_parent)
# creates connector tab in tkinter object
tab_parent.add(tab_resistors, text="Resistors")
tab_parent.add(tab_capacitors, text="Capacitors")
tab_parent.add(tab_ICs, text="ICs")
tab_parent.add(tab_connectors, text="Connectors")
tab_parent.grid(row=0, columnspan=2)

for ite, i in enumerate(list(database_dict_resistors)):
    # here the rows for the resistors are created in tkinter so the user can
    # enter values to be searched against
    row_nr = ite+2
    entrylist_res.append(row_creator(
        i, example_list_resistors[ite], ite+1, tab_resistors))
for ite, i in enumerate(list(database_dict_capacitors)):
    # here the rows for the capacitors are created in tkinter so the user can
    # enter values to be searched against
    row_nr = ite+2
    entrylist_cap.append(row_creator(
        i, example_list_capacitors[ite], ite+1, tab_capacitors))
for ite, i in enumerate(list(database_dict_ICs)):
    # here the rows for the capacitors are created in tkinter so the user can
    # enter values to be searched against
    row_nr = ite + 2
    entrylist_cap.append(row_creator(
        i, example_list_capacitors[ite], ite + 1, tab_ICs))
tk_window.bind('<Return>', lambda event: search())
search_button = ttk.Button(tk_window, text="search", command=search)
# a single button is used to perform the search and window update
search_button.grid(column=0, row=row_nr+1, sticky=tk.E, padx=5, pady=5,
                   columnspan=3)
row_nr += 2
scrollbar = tk.Scrollbar(tk_window, orient="vertical")
scrollbar.grid(row=row_nr, column=4, sticky='NS')
result_canvas = tk.Canvas(tk_window, yscrollcommand=scrollbar.set)
result_canvas.configure(scrollregion=result_canvas.bbox("all"),
                        yscrollcommand=scrollbar.set)
frame_for_canvas = tk.Frame(result_canvas)
result_canvas.create_window((0, 0), window=frame_for_canvas, anchor="n")
result_canvas.grid(row=row_nr, column=0, columnspan=3, sticky="N")
scrollbar.config(command=result_canvas.yview)
frame_for_canvas.grid_rowconfigure(0, weight=1)
frame_for_canvas.grid_columnconfigure(0, weight=1)
frame_for_canvas.bind("<Configure>", on_configure)
frame_for_canvas.bind("<MouseWheel>", on_mousewheel)
result_canvas.bind("<MouseWheel>", on_mousewheel)
result_canvas.yview_moveto(0.0)

tk_window.mainloop()
a = 1
