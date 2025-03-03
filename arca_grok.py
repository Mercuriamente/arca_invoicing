# %% [markdown]
# LIBRARIES

# %%
pip install mysql-connector-python
pip install helium

# %%
import os
import time
import pprint
import helium
import locale
import selenium
import calendar
import pandas as pd
import mysql.connector
from helium import write
from helium import Config
from datetime import datetime, timedelta
from helium import get_driver
from helium import kill_browser
from helium import start_chrome, get_driver
from helium import CheckBox, find_all, click
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from helium import find_all, S, write, click, press

# %% [markdown]
# HAY QUE MODIFICAR FLORIDA CON DOBLE TEXTO Y AGRAGAR LOS EMAILS AL CSV BASE!!!!!

# %% [markdown]
# DATAFRAMES

# %%
# Read the CSV file into a DataFrame
df = pd.read_csv('Data/datos_mant_bna.csv')

# Crea copia del df original para trabajar sin riesgo de modificar data original
df_sucursales = df.copy()

# Crea diccionario de zonales
dic_zonales = {}

# Agrupa las filas por Zonales
zonales = df_sucursales.groupby(df_sucursales.columns[4])

for name, group in zonales:
    dic_zonales[f'df_{name.replace(" ","_")}'] = group.copy()
    

# %%
# CODIGO DE VERIFICACIÓN DE CONFECCION DE DF GENERAL Y PARCIALES - SOLO USAR CUANDO HAY MODIFICACIONES EN LAS ZONALES DEL DF ORIGINAL


# Ordena las keys del dic_zonales por los índices de la columna 4 del df original
indices_columna_4 = df_sucursales[df_sucursales.columns[4]].unique()
nombres_ordenados = sorted(dic_zonales.keys(), key=lambda x: indices_columna_4.tolist().index(x.replace('df_', '').replace('_', ' ')))

# Muestra índices y nombres de las columnas 
print("\nColumnas e índices:")
for index, column in enumerate(df_sucursales.columns):
    print(f'{index}:{column}')    

# Mostrar la forma del DataFrame con datos totales de mantenimiento
df_sucursales_shape = df.shape
print("\nShape del df_sucursales:")
print(df_sucursales_shape)
print()

# Imprime keys del diccionario de zonales
print(f"Zonales en el diccionario")
print(list(dic_zonales.keys()))

# Muestra dfs parciales por zonal, ordenados por columna índice 4 
print(f"\nDataframes de zonales:")
for name in nombres_ordenados:
    df = dic_zonales[name]
    print(f'\n{name}:')
    print(f'Rango de índices: {df.index.min()} - {df.index.max()}')


# %%
# CODIGO EN CASO DE NECESITAR EXCLUIR UNA SUCURSAL EN PARTICULAR

"""df = DF DE SUCURSAL DE LA QUE EXCLUIR
df = df.drop()"""

# %% [markdown]
# VARIABLES

# %%
# Datos del emisor
razon_social = 'RUIZ JORGE MARIO'
cuit = '20164787363'
clave_fiscal = 
cbu ="0110054930005401289251"

# Datos del cliente
cuit_cliente = '30500010912'

# Variables ARCA
valor_max_fca = '1121884.29'
valor_min_fcea = '1121884.30'

# Establecer la configuración regional a español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Periodo de facturación
hoy = datetime.today()
mes_facturado = (hoy.replace(day=1) - timedelta(days=1)).strftime("%B %Y") # Indica fecha presente para referencia
comienzo_ciclo = (hoy.replace(day=1) - timedelta(days=hoy.day)).replace(day=1).strftime("%d/%m/%Y") # Indica primer día del mes anterior al presente
fin_ciclo = (hoy.replace(day=1) - timedelta(days=1)).strftime("%d/%m/%Y") # Indica primer último del mes anterior al presente
vencimiento_pago = (hoy + timedelta(days=60)).strftime("%d/%m/%Y") # Indica 60 días del la fecha presente
fecha_emision = datetime.today().date().strftime('%d-%m-%Y') # Establece fecha de emsión como día presente

# %%
# CODIGO PARA VERIFICACION DE VARIABLES, NO ES NECESARIO USARLO A NO SER QUE HAYA MODIFICACIONES

"""
print(f"Razón social del emisor: {razon_social}")
print(f"CUIT emisor: {cuit}")
print(f"Clave fiscal del emisor: {clave_fiscal}")
print(f"CBU del emisor: {cbu}")
print(f"CUIT cliente: {cuit_cliente}")
print(f"Fecha actual: {hoy}")
print(f"Mes facturado: {mes_facturado}")
print(f"Comienzo de ciclo: {comienzo_ciclo}")
print(f"Fin de ciclo: {fin_ciclo}")
print(f"Fecha de vencimiento del pago: {vencimiento_pago}")
print(f"Fecha de emsión de factura: {fecha_emision}")"""

# %% [markdown]
# INVOICE AUTOMATION - FACTURAS DE CREDITO ELECTRÓNICAS A (FCEA)

# %%
# Resets response time (default = 10 seg)
Config.implicit_wait_secs = 15

# Abre pagina de la AFIP en Chrome
start_chrome("https://auth.afip.gob.ar/contribuyente_/login.xhtml")

# Get the Selenium WebDriver from Helium
driver = get_driver()

# Ingresa CUIT
write(cuit, into='CUIT/CUIL')
click('Siguiente')

# Ingresa contraseña
write(clave_fiscal, into='TU CLAVE')
click('Ingresar')

# Selecciona "Comprobantes en línea"
try:
    click('Comprobantes en línea')

except Exception:
    click('Ver todos')
    time.sleep(5)
    try:
        click('Comprobantes en línea')
    except LookupError:
        pass
    
# Espera un momento para que la nueva pestaña se abra
time.sleep(5)
    
# Switches to the new tab
# Get a list of all windows
windows = get_driver().window_handles

# Switch to the second window (index 1)
get_driver().switch_to.window(windows[1])

# Selecciona empresa a representar
click(razon_social)

# Seleccionar acción a ejecurtar dentro del RCEL
click('Generar Comprobantes')

# Selects "Punto de Venta"
# Find the dropdown menu by its CSS selector
dropdown_elements = find_all(S('#puntodeventa'))

# Create a Select object
# As this client has only one point of sale selects only option
dropdown = dropdown_elements[0]
select = Select(dropdown.web_element)

# Select the option by index
select.select_by_index(1)  # Index starts from 0

# Espera un momento para que la nueva pestaña se abra
time.sleep(2)

# Selects "Tipo de Comprobante"
# Find the dropdown menu by its CSS selector
dropdown_elements = find_all(S('#universocomprobante')) 

# Create a Select object
dropdown = dropdown_elements[0]
select = Select(dropdown.web_element)

# Select the option by index Factura de Crédito Electreónica A (FcE A)
select.select_by_index(11)  # Index starts from 0

click('Continuar')

# Datos de emisión (Paso 1 de 4)

# Selects "Conceptos a incluir"

# Find the dropdown menu by its CSS selector
dropdown_elements = find_all(S('#idconcepto'))

# Create a Select object
dropdown = dropdown_elements[0]
select = Select(dropdown.web_element)

# Select the option by index - Chooses "Productos y Servicios"
select.select_by_index(3)  

write(cbu, into='CBU del Emisor')

# Selects "Opción de transferencia"

# Find the dropdown menu by its CSS selector
dropdown_elements = find_all(S('#opcionTransferencia'))

# Create a Select object
dropdown = dropdown_elements[0]
select = Select(dropdown.web_element)

# Select the option by index - Chooses " Sistema de circulación abierta"
select.select_by_index(2)  

# Selects dates for "Periodo facturado"

# Find the date input fields by their CSS selectors
date_input_elements1 = find_all(S('#fsd'))
date_input_elements2 = find_all(S('#fsh'))
date_input_elements3 = find_all(S('#vencimientopago'))

# Enter the date in the first date input field ("Desde")
click(date_input_elements1[0])
for _ in range(10):  # Adjust the range as needed
    press(Keys.BACKSPACE)
write(comienzo_ciclo)

# Enter the date in the second date input field ("Hasta")
click(date_input_elements2[0])
for _ in range(10):  # Adjust the range as needed
    press(Keys.BACKSPACE)
write(fin_ciclo)

# Enter the date in the third date input field ("Vto. para el Pago")
click(date_input_elements3[0])
for _ in range(10):  # Adjust the range as needed
    press(Keys.BACKSPACE)
write(vencimiento_pago)

click('Continuar')

# DATOS DEL RECEPTOR (PASO 2 DE 4)

# Selects "Condición frente al IVA"

# Find the dropdown menu by its CSS selector
dropdown_elements = find_all(S('#idivareceptor'))

# Create a Select object
dropdown = dropdown_elements[0]
select = Select(dropdown.web_element)

# Select the option by index ("Responsable Inscripto")
select.select_by_index(1)  

write(cuit_cliente, into='CUIT')
# Press Enter para polupar automaticamente los dos campos de abajo
press(Keys.ENTER)

click('Continuar')

#DATOS DE LA OPERACIÓN (PASO 3 DE 4)

# IMPORTANT!  - FACTURAS DE CREDITO ELECTRONICAS A - GENERATES INVOICES FOR PRECIOS UNITARIOS > 451.848.75 
# Generates invoices, dowloads them and iterates over the df

# Get from df
suc = [df.iloc[:,8] > valor_min_fcea]

# Iterate over the rows of the DataFrame
for index, row in suc.iterrows():
    
    # Get the values you need
    sucursal_id_ = str(row['sucursal_id']).zfill(4)
    sucursal_nombre_ = row['sucursal_nombre']
    
    # Construct the text of invoice detail
    prod_serv = f'Servicio de mantenimiento termomecánico mensual correspondiente al mes de {mes_facturado} de la Suc. {sucursal_nombre_} ({sucursal_id_}) '
    
    # Write the text of invoice detail into text area
    write(prod_serv, into='Producto/Servicio')
    
    # Get the values you need for prices 
    precio_sin_iva_ = row['precio_sin_iva']
    
    # Construct the text for prices
    prec_unitario = str(precio_sin_iva_)
    
    # Write the text for the price
    write(prec_unitario, into='Prec. Unitario')
    
    # Find the dropdown menu by its CSS selector for "U. Medida"
    dropdown_elements = find_all(S('#detalle_medida1'))

    # Create a Select object
    dropdown = dropdown_elements[0]
    select = Select(dropdown.web_element)

    # Select the option by index "Otras unidades"
    select.select_by_index(45)  
    
    click('Continuar')

    # Confirms invoice generation
    click('Confirmar Datos...')

    # Wait for the alert to appear
    Alert(get_driver()).accept()
    
    # Downloads invoice
    click('Imprimir...')
    
    # Navigate back to the previous page
    get_driver().back()
    
    # Sleep for 5 seconds
    time.sleep(5)
    
    # Borra los datos habían quedado almacenados

    # Construct the text
    prod_serv_del = f''
    
    # Write the text
    write(prod_serv_del, into='Producto/Servicio')
        
    # Construct the text
    prec_unitario_del = f''
    
    # Write the text
    write(prec_unitario_del, into='Prec. Unitario')

# Close the browser
kill_browser()  

# %% [markdown]
# INVOICE AUTOMATION - FACTURAS A (FCA)

# %%
# Resets response time (default = 10 seg)
Config.implicit_wait_secs = 15

# Abre pagina de la AFIP en Chrome
start_chrome("https://auth.afip.gob.ar/contribuyente_/login.xhtml")

# Get the Selenium WebDriver from Helium
driver = get_driver()

# Ingresa CUIT
write(cuit, into='CUIT/CUIL')
click('Siguiente')

# Ingresa contraseña
write(clave_fiscal, into='TU CLAVE')
click('Ingresar')

# Selecciona "Comprobantes en línea"
try:
    click('Comprobantes en línea')

except Exception:
    click('Ver todos')
    time.sleep(5)
    try:
        click('Comprobantes en línea')
    except LookupError:
        pass
    
# Espera un momento para que la nueva pestaña se abra
time.sleep(5)
    
# Switches to the new tab
# Get a list of all windows
windows = get_driver().window_handles

# Switch to the second window (index 1)
get_driver().switch_to.window(windows[1])

# Selecciona empresa a representar
click(razon_social)

# Seleccionar acción a ejecurtar dentro del RCEL
click('Generar Comprobantes')

# Selects "Punto de Venta"
# Find the dropdown menu by its CSS selector
dropdown_elements = find_all(S('#puntodeventa'))

# Create a Select object
# As this client has only one point of sale selects only option
dropdown = dropdown_elements[0]
select = Select(dropdown.web_element)

# Select the option by index
select.select_by_index(1)  # Index starts from 0

# Espera un momento para que la nueva pestaña se abra
time.sleep(2)

# Selects "Tipo de Comprobante"
# Find the dropdown menu by its CSS selector
dropdown_elements = find_all(S('#universocomprobante')) 

# Create a Select object
dropdown = dropdown_elements[0]
select = Select(dropdown.web_element)

# Select the option by index Factura A (Fc A)
select.select_by_index(0)  # Index starts from 0

click('Continuar')

# Datos de emisión (Paso 1 de 4)

# Selects "Conceptos a incluir"

# Find the dropdown menu by its CSS selector
dropdown_elements = find_all(S('#idconcepto'))

# Create a Select object
dropdown = dropdown_elements[0]
select = Select(dropdown.web_element)

# Select the option by index "Productos y Servicios"
select.select_by_index(3)  

# Selects dates for "Periodo facturado"

# Find the date input fields by their CSS selectors
date_input_elements1 = find_all(S('#fsd'))
date_input_elements2 = find_all(S('#fsh'))
date_input_elements3 = find_all(S('#vencimientopago'))

# Enter the date in the first date input field ("Desde")
click(date_input_elements1[0])
for _ in range(10):  # Adjust the range as needed
    press(Keys.BACKSPACE)
write(comienzo_ciclo)

# Enter the date in the second date input field ("Hasta")
click(date_input_elements2[0])
for _ in range(10):  # Adjust the range as needed
    press(Keys.BACKSPACE)
write(fin_ciclo)

# Enter the date in the third date input field ("Vto. para el Pago")
click(date_input_elements3[0])
for _ in range(10):  # Adjust the range as needed
    press(Keys.BACKSPACE)
write(vencimiento_pago)

click('Continuar')

# DATOS DEL RECEPTOR (PASO 2 DE 4)

# Selects "Condición frente al IVA"

# Find the dropdown menu by its CSS selector
dropdown_elements = find_all(S('#idivareceptor'))

# Create a Select object
dropdown = dropdown_elements[0]
select = Select(dropdown.web_element)

# Select the option by index "Responsable Inscripto"
select.select_by_index(1)  

# Writes CUIT
write(cuit_cliente, into='CUIT')
# Press Enter para populpar automaticamente los dos campos de abajo
press(Keys.ENTER)

# Condiciones de venta 
# Find all checkboxes on the page
checkboxes = find_all(CheckBox())

# Click the last checkbox "Otra"
click(checkboxes[-2])

click('Continuar')

# DATOS DE LA OPERACIÓN (PASO 3 DE 4)

# IMPORTANT!  - FACTURAS A - GENERATES INVOICES FOR PREICOS UNITARIOS <= 451.848.75 WHICH IS THA MAX ALLOWED BY ARCA
# Generates invoices, dowloads them and iterates over the df

# Get from df
suc = [df.iloc[:,8] <= valor_max_fca]

# Iterate over the rows of the DataFrame
for index, row in suc.iterrows():
    
    # Get the values you need
    sucursal_id_ = str(row['sucursal_id']).zfill(4)
    sucursal_nombre_ = row['sucursal_nombre']

    # Construct the text of invoice detail
    prod_serv = f'Servicio de mantenimiento termomecánico mensual correspondiente al mes de {mes_facturado} de la Suc. {sucursal_nombre_} ({sucursal_id_}) '
    
    # Write the text of invoice detail into text area
    write(prod_serv, into='Producto/Servicio')
    
    # Get the values you need for prices 
    precio_sin_iva_ = row['precio_sin_iva']
    
    # Construct the text for prices
    prec_unitario = str(precio_sin_iva_)
    
    # Write the text for the price
    write(prec_unitario, into='Prec. Unitario')
    
    # Find the dropdown menu by its CSS selector for "U. Medida"
    dropdown_elements = find_all(S('#detalle_medida1'))

    # Create a Select object
    dropdown = dropdown_elements[0]
    select = Select(dropdown.web_element)

    # Select the option by index "Otras unidades"
    select.select_by_index(45)  
    
    click('Continuar')

    # Confirms invoice generation
    click('Confirmar Datos...')

    # Wait for the alert to appear
    Alert(get_driver()).accept()
    
    # Downloads invoice
    click('Imprimir...')
    
    # Navigate back to the previous page
    get_driver().back()
    
    # Sleep for 5 seconds
    time.sleep(5)
    
    # Borra los datos habían quedado almacenados

    # Construct the text
    prod_serv_del = f''
    
    # Write the text
    write(prod_serv_del, into='Producto/Servicio')
        
    # Construct the text
    prec_unitario_del = f''
    
    # Write the text
    write(prec_unitario_del, into='Prec. Unitario')
    
# Close the browser
kill_browser()    
      

# %% [markdown]
# PDFs HANDLING & MONTHLY INVOICE DF CREATION 

# %%
SAVED PDFs - FACTURAS A

# %%
# Fetches Facturas A file name, directory path and creation date

# Specify the download directory
carpeta_facturas_credito_electronicas_a_mes = rf'C:\Users\j-m-r\OneDrive\Escritorio\hack_a_boss\Personal Projects\Instalclima\Finanzas\fact_mant_enero_2025\facturas_credito_electronicas_a'

# Initialize lists for absolute paths and creation dates
absolute_paths_fcea = []
creation_dates_fcea = []

# Get a list of files in the download directory
facturas_credito_electronicas_a_mes = os.listdir(carpeta_facturas_credito_electronicas_a_mes)

# Print the absolute path for each file
for factura in facturas_credito_electronicas_a_mes:
    absolute_path_fcea = os.path.join(carpeta_facturas_credito_electronicas_a_mes, factura)
    creation_time_fcea = os.path.getctime(absolute_path_fcea)
    creation_date_fcea = datetime.fromtimestamp(creation_time_fcea).strftime('%d-%m-%Y')
        
    # Append the values to the lists
    absolute_paths_fcea.append(absolute_path_fcea)
    creation_dates_fcea.append(creation_date_fcea)

# Print the list of downloaded files
print(facturas_credito_electronicas_a_mes)
print(absolute_paths_fcea)

# %%
# Saves Facturas A file name and directory path to DF

df_facturas_credito_electronicas_a_mes = pd.DataFrame({"Factura Nro.": facturas_credito_electronicas_a_mes, "Ubicacion Archivo": absolute_paths_fcea, "Fecha Emisión": creation_date_fcea})


# %%
# CREATES MASK TO JOIN ORIGINAL DF WITH FACTURAS A DATA

mask_fac_credito_electronicas_a_df = df.iloc[0:68][df.iloc[:,8] > 1121884.30]
mask_fac_credito_electronicas_a_df["sucursal_id"] = mask_fac_credito_electronicas_a_df["sucursal_id"].fillna("0").astype(float).astype(int).astype(str).str.zfill(4)

# %%
mask_fac_credito_electronicas_a_df

# %%
concatenated_df_fcea = pd.concat([mask_fac_credito_electronicas_a_df.reset_index(drop=True), df_facturas_credito_electronicas_a_mes.reset_index(drop=True)], axis=1)
concatenated_df_fcea

# %%
concatenated_df_fcea.to_csv('Data/concatenated_df_fcea.csv', index=False)

# %% [markdown]
# SAVED PDFs - FACTURAS A

# %% [markdown]
# HERE I NEED AN INTERMEDIATE STEP, TO BE SET UP IN NEXT SPRINT
# WHERE IT AUTOMATICALLY FETCHES THE PDFS DROM DOWLOADS AND MOVED IT TO AN INDIVIDUAL FOLDER

# %%
# Fetches Facturas A file name, directory path and creation date

# Specify the download directory
carpeta_facturas_a_mes = rf'C:\Users\j-m-r\OneDrive\Escritorio\hack_a_boss\Personal Projects\Instalclima\Finanzas\fact_mant_enero_2025\facturas_a'

# Initialize lists for absolute paths and creation dates
absolute_paths_fca = []
creation_dates_fca = []

# Get a list of files in the download directory
facturas_a_mes = os.listdir(carpeta_facturas_a_mes)

# Print the absolute path for each file
for factura in facturas_a_mes:
    absolute_path_fca = os.path.join(carpeta_facturas_a_mes, factura)
    creation_time_fca = os.path.getctime(absolute_path_fca)
    creation_date_fca = datetime.fromtimestamp(creation_time_fca).strftime('%d-%m-%Y')
       
    # Append the values to the lists
    absolute_paths_fca.append(absolute_path_fca)
    creation_dates_fca.append(creation_date_fca)

# Print the list of downloaded files
print(facturas_a_mes)
print(absolute_paths_fca)

# %%
# Saves Facturas A file name and directory path to DF

df_facturas_a_mes = pd.DataFrame({"Factura Nro.": facturas_a_mes, "Ubicacion Archivo": absolute_paths_fca, "Fecha Emisión": creation_date_fca})


# %%
df_facturas_a_mes.head(11)

# %%
"""SIN USO POR EL MOMENTO - IGNORAR 

# Read the CSV file into a DataFrame
df_mant_febrero_2024 = pd.read_csv('Data/datos_mant_bna_febrero_2024.csv')"""

# %%
"""SIN USO POR EL MOMENTO - IGNORAR 

# FORMATS THE MONTHS DF, SHOULD BE DONE AUTOMATICALLY IN THE FUTURE 

df_mant_febrero_2024["sucursal_id"] = df_mant_febrero_2024["sucursal_id"].fillna("0").astype(float).astype(int).astype(str).str.zfill(4)
df_mant_febrero_2024 = df_mant_febrero_2024.iloc[:76, :10]
df_mant_febrero_2024.head(5)"""

# %%
# CREATES MASK TO JOIN ORIGINAL DF WITH FACTURAS A DATA

mask_fac_a_df = df.iloc[0:78][df.iloc[:,8] <= 1121884.30]
mask_fac_a_df["sucursal_id"] = mask_fac_a_df["sucursal_id"].fillna("0").astype(float).astype(int).astype(str).str.zfill(4)

# %%
mask_fac_a_df

# %%
mask_fac_a_df.shape

# %%
concatenated_df_fca = pd.concat([mask_fac_a_df.reset_index(drop=True), df_facturas_a_mes.reset_index(drop=True)], axis=1)
concatenated_df_fca

# %%
# Used only temporary to save partial invoicing 
#concatenated_df_fca.to_csv('Data/datos_mant_bna_enero_2025.csv', index=False)

# %%
concatenated_df_fca.to_csv('Data/concatenated_df_fca.csv', index=False)

# %%
# CONCATENATES CONCATENATED DF OF FCA & FCEA

concatenated_all = pd.concat([concatenated_df_fcea.reset_index(drop=True), concatenated_df_fca.reset_index(drop=True)], axis=0)
concatenated_all.reset_index(drop=True, inplace=True)
concatenated_all

# %%
concatenated_all.head(50)

# %%
concatenated_all.to_csv('Data/datos_mant_bna_enero_2025.csv', index=False)

# %%
df_mes = pd.read_csv('Data/datos_mant_bna_enero_2025.csv')
df_mes.head()

# %%
# Crea DF para trabajar con el listado para control impreso
mant_ene_2025 = 'Data/datos_mant_bna_enero_2025.csv'
df_mant_ene_2025 = pd.read_csv(mant_ene_2025)

# Remueve columnas extra
df_mant_ene_2025 = df_mant_ene_2025.drop(df_mant_ene_2025.columns[[0,1,5,6,7,8,9,10,12,13]], axis=1)

# Formatea el numero de factura a modo mas legible
df_mant_ene_2025.iloc[:,3] = df_mant_ene_2025.iloc[:,3].apply(lambda x: x[16:-4] if len(x) > 20 else '')

#Guarda cvs bajo nombre separado
ubicacion = r'C:\Users\j-m-r\OneDrive\Escritorio\hack_a_boss\Personal Projects\Instalclima\Finanzas\Data\control_manual_pagos\ene_2025.csv'
df_mant_ene_2025.to_csv(ubicacion, index=False)


# %% [markdown]
# SQL

# %%
# Tablas de la Database

query = """SHOW TABLES"""

def execute_query(query, database = "registro_financiero", host = "localhost", user = "root", password = "LearN2024!"):
    
    db = mysql.connector.connect(host     = host,
                                 user     = user,
                                 password = password,
                                 database = database)

    cursor = db.cursor()
    cursor.execute(query) # Ejecutamos la query

    # Guardamos los datos de las tablas del database
    tables = cursor.fetchall()

    # Imprimimos el resultado
    for table in tables:
        print(table)
        
    cursor.fetchall() # Vaciamos el cursor
    cursor.close()
    db.close()
    
# Call the function with the query
execute_query(query)

# %%
# Columnas de FACTURAS ENVIADAS

query = """SHOW COLUMNS FROM fact_mant_bna_enviadas"""

def execute_query(query, database = "registro_financiero", host = "localhost", user = "root", password = "LearN2024!"):
    
    db = mysql.connector.connect(host     = host,
                                 user     = user,
                                 password = password,
                                 database = database)

    cursor = db.cursor()
    cursor.execute(query) # Ejecutamos la query

    # Guardamos los datos de las columnas de la tabla
    columns = cursor.fetchall()
    column_names = cursor.column_names # Nombre de las columnas de la tabla

    # Imprimimos el resultado
    for column in columns:
        print(column[0])
        
    cursor.fetchall() # Vaciamos el cursor
    cursor.close()
    db.close()
    
# Call the function with the query
execute_query(query)

# %%
column

# %%
# Nombres de columnas de FACTURAS ENVIADAS

query = """SELECT * FROM fact_mant_bna_enviadas"""

def execute_query(query, database = "registro_financiero", host = "localhost", user = "root", password = "LearN2024!"):
    
    db = mysql.connector.connect(host     = host,
                                 user     = user,
                                 password = password,
                                 database = database)

    cursor = db.cursor()
    cursor.execute(query) # Ejecutamos la query

    
    column_names = cursor.column_names # Nombre de las columnas de la tabla

        
    cursor.fetchall() # Vaciamos el cursor
    cursor.close()
    db.close()
    
    return column_names
    
# Call the function with the query
column_names = execute_query(query)
print(column_names)

# %%
column_names

# %%
# Datos de columnas de FACTURAS ENVIADAS

query = """SELECT * FROM fact_mant_bna_enviadas;"""

def execute_query(query, database = "registro_financiero", host = "localhost", user = "root", password = "LearN2024!"):
    
    db = mysql.connector.connect(host     = host,
                                 user     = user,
                                 password = password,
                                 database = database)

    cursor = db.cursor()
    cursor.execute(query) # Ejecutamos la query

    # Guardamos los datos de las columnas de la tabla
    data = cursor.fetchall()

    # Imprimimos el resultado
    for all in data:
        print(all)
        
    cursor.fetchall() # Vaciamos el cursor
    cursor.close()
    db.close()
    
# Call the function with the query
execute_query(query)

# %%
print(data)

# %%
# Con ambas variables podemos crear un DataFrame
# En este ejemplo el DataFrame estará vacío

pd.DataFrame(data = data, columns = column_names)

# %%
df_mant_febrero_2024.head()


