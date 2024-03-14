import pandas as pd
import PySimpleGUI as sg

sg.theme('DarkTeal3')  # sets the theme


def selection_sort(arrayToBeSorted):
    unSorted = tuple(arrayToBeSorted)

    num = len(arrayToBeSorted)
    for i in range(num - 1):
        min_index = i  # assume the first element is the smallest
        for j in range(i + 1, num):
            if arrayToBeSorted[j]['Rating'] < arrayToBeSorted[min_index]['Rating']:  # if the number is smaller
                min_index = j  # make the new number the smallest found number

        # Swap the smallest element with the element
        arrayToBeSorted[i], arrayToBeSorted[min_index] = arrayToBeSorted[min_index], arrayToBeSorted[i]

    return arrayToBeSorted, unSorted


class DataFrame:
    def __init__(self, filePath):
        self.filePath = filePath
        self.df = pd.read_csv(filePath, encoding='unicode_escape')
        self.listBoxData = self.ConvertAllDataTo2dList()
        self.validateData = self.GetValidateData()

    def ConvertAllDataTo2dList(self):
        lData = []
        for index, row in self.df.iterrows():  # will run through the entire dataframe and get its row and index
            lData.append("{:32} {:18} {:20} {:14} {:20} {:15} {:5}".format(
                f'{row["Textbook"]}', f'{row["Subject"]}', f'{row["Seller"]}',
                f'{row["Purchase price"]}', f'{row["Purchaser"]}', f'{row["Sale price"]}',
                f'{row["Rating"]}'))
        return lData

    def GetValidateData(self):
        vData = {}
        for index, row in self.df.iterrows():  # will run through the entire dataframe and get its row and index
            tb = row['Textbook'].lower().strip()
            p = f"{row['Purchaser']}".lower().strip()
            vData[f"{tb}, {p}"] = [index, row]
        return vData

    def ValidatePurchaser(self, textBook: str, purchaser: str) -> bool:
        textBook = textBook.lower().strip()  # makes it case-insensitive by making it all lowercase values
        purchaser = purchaser.lower().strip()
        if f"{textBook}, {purchaser}" in self.validateData:
            return True
        return False

    def GetRow(self, textBook: str, purchaser: str) -> list:
        textBook = textBook.lower().strip()
        purchaser = purchaser.lower().strip()
        return self.validateData[f"{textBook}, {purchaser}"]

    def toListBoxFormat(self, row):
        return "{:32} {:18} {:20} {:14} {:22} {:15} {:4}".format(
            f'{row["Textbook"]}', f'{row["Subject"]}', f'{row["Seller"]}',
            f'{row["Purchase price"]}', f'{row["Purchaser"]}', f'{row["Sale price"]}',
            f'{row["Rating"]}')

    def ChangeValueByIndex(self, index, column, newValue):  # changes the value in dataframe by index, column
        self.df.loc[index, column] = newValue
        self.listBoxData = self.ConvertAllDataTo2dList()
        self.validateData = self.GetValidateData()

    def SaveToFile(self, filePath='NEW.csv'):  # saves the dataframe to a csv
        self.df.to_csv(filePath)

    def FilterByColumn(self, column, filterWord):
        dummyList = []
        for index, row in self.df.iterrows():
            if filterWord.lower() in row[column].lower():
                dummyList.append(self.toListBoxFormat(row))

        return dummyList

    def SortByRating(self):
        dummyList = []
        for index, row in self.df.iterrows():
            try:
                row['Rating'] = int(row['Rating'])
            except:
                row['Rating'] = 0
            finally:
                dummyList.append(row)
        dummyList = selection_sort(dummyList)[0]
        listr = []
        for row in dummyList:
            listr.append(self.toListBoxFormat(row))
        return listr


df = DataFrame('data.csv')
layout = [[sg.Column(
    [
        [sg.Text("{:32} {:18} {:20} {:14} {:20} {:14} {:4}".format('Textbook', "Subject", "Seller",  # column headings
                                                                   "Purchase price", 'Purchaser', 'Sale price',
                                                                   'Rating'), size=(150, 1))],
        [sg.Listbox(df.listBoxData, size=(130, 20), key='LB')],
        [sg.Button('Display All')],
        [sg.Text('Rate a textbook:                                         '), sg.Text("Filter and sort:")],
        [sg.Text('TextBook: '), sg.Input(key='Textbook'), sg.Text("Filter By:"),
         sg.Combo(df.df.columns.tolist(), 'Textbook', key='COMBO')],
        [sg.Text('Purchaser:'), sg.Input(key='Purchaser'), sg.Text('Enter filter keyword:'),
         sg.Input(key='YEP', enable_events=True)],
        [sg.Button('Search'), sg.Text('                                                  Search:'),
         sg.Button('RateSort')],
        [sg.Text('Rating:   '), sg.Input(key='Rating')],
        [sg.Button('Save')],
        [sg.Button('Exit')]
    ]
)]]

# create the window
window = sg.Window('Profit calculator', layout, size=(970, 520), font=("Courier", 11))

while True:
    event, values = window.read()
    if event in (None, "Exit"):
        df.SaveToFile()
        break
    if event == 'RateSort':
        sortedList = df.SortByRating()
        window['LB'].update(sortedList)
    if event == 'YEP':
        key = event

        if values[key].strip() == '':
            window['LB'].update(df.listBoxData)
        else:
            filterWord = values[key].strip()
            filtered = df.FilterByColumn(values['COMBO'], filterWord)
            if len(filtered) == 0:
                filtered = [f'No entries found with {values["COMBO"]}.']

            window['LB'].update(filtered)

    if event == "Display All":
        window['LB'].update(df.listBoxData)
    if event == 'Search':
        valid = df.ValidatePurchaser(values['Textbook'], values['Purchaser'])
        if valid:
            row = df.GetRow(values['Textbook'], values['Purchaser'])[1]
            window['LB'].update([df.toListBoxFormat(row)])
        else:
            window['LB'].update(['Sorry, there was no match. Let\'s try again.'])
    if event == "Save":
        valid = df.ValidatePurchaser(values['Textbook'], values['Purchaser'])
        if valid:
            index = df.GetRow(values['Textbook'], values['Purchaser'])[0]
            df.ChangeValueByIndex(index, 'Rating', values['Rating'])  # change the value of rating
            row = df.GetRow(values['Textbook'], values['Purchaser'])[1]
            window['LB'].update([df.toListBoxFormat(row)])
        else:
            window['LB'].update(['Sorry, there was no match. Let\'s try again.'])
window.close()
