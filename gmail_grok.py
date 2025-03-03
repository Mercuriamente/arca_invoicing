# %%
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib


# %%
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import googleapiclient.discovery
from collections import defaultdict
import os.path
import pandas as pd
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import locale
import textwrap
import base64
import csv
import json
import os


# %%
import os
print(os.getcwd())

# %%
# Authenticates JSON token for Gmail API

# # If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# %%
# Copia de respaldo mant dic antes de modificar con emails
import shutil

arch_mant_dicimebre_2024 = 'Data/datos_mant_bna_diciembre_2024.csv'
arch_mant_diciembre_2024_original = 'Data/datos_mant_bna_diciembre_2024_original.csv'

shutil.copy(arch_mant_dicimebre_2024, arch_mant_diciembre_2024_original)

# %%
# Crea nueva columna con los email de las sucursales, estoy hay que hacerlo en el csv de mant general del codigo de afip

#Define el archivo
csv_file = 'Data/datos_mant_bna_diciembre_2024.csv'

#Lee archivo
with open(csv_file, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames
    
# Verifica que fieldnames no sea None
if fieldnames is None:
    raise ValueError("El archivo CSV no tiene encabezados.")

# Agrega la columna 'emails' si no existe
if 'emails' not in fieldnames:
    fieldnames.append('emails')

# Construye direcciones de email
for row in rows:
    sucursal_id = row['sucursal_id']
    email_ger = f'{sucursal_id}ger@bna.com.ar'
    email_pop = f'{sucursal_id}pop@bna.com.ar'
    row['emails'] = f'{email_ger},{email_pop}'
    
# Guarda cambios en CSV
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    
    


# %%
# WITH ABSOLUTE PATHS - Creates and sends emails - Stores messages ids into a dictionary

#Define el mes del servicio 
def mes_servicio():
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') #Setea a Español
    today = datetime.today()
    month = today.month
    year = today.year
    
    if month == 1:
        previous_month = 12
        year -= 1 
    else:
        previous_month = month -1
        
    fecha_servicio = datetime(year, previous_month,1)
    return fecha_servicio.strftime("%B %Y")

# Creates formated date for CVS file name 
def mes_csv():
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') #Setea a Español
    today = datetime.today()
    month = today.month
    year = today.year
    
    if month == 1:
        previous_month = 12
        year -= 1 
    else:
        previous_month = month -1
        
    fecha_servicio = datetime(year, previous_month,1)
    return fecha_servicio.strftime("%B_%Y")

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')

def create_message_with_attachment(sender, to, subject, message_text, file_paths):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # Add the body of the email
    message.attach(MIMEText(message_text, 'html'))

    # Allows to add multiple atachements to an email
    for file_path in file_paths:
        msg = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as f:
            msg.set_payload(f.read())
        encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
        message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

# Build the service
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('gmail', 'v1', credentials=creds)

# Create an empty dictionary to store the message ids
message_ids = {}

# Call month of service function 
fecha = mes_servicio()

# Call Csv file date function
fecha_csv = mes_csv()

                
sucursales = defaultdict(list)
with open(f'Data/datos_mant_bna_{fecha_csv}.csv','r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['sucursal_id'] =='9209':
            sucursales[f"{row['sucursal_id']}_{row['Ubicacion Archivo']}"].append(row)    
        else:
            sucursales[row['sucursal_id']].append(row)

# Sends emails
for sucursal_id, rows in sucursales.items():
    recipients = rows[0]['emails']
    subject = f'FE DE ERRATAS: Factura/s electrónica/s - Mantenimiento termomecánico - {fecha}'
    # Fixes how the body of the messages looks in the end
    body = textwrap.dedent(f"""  
    <p>Estimados:</p>
    <br>
    <p>Se adjunta/n la/s factura/s electrónica/s correspondiente/s al mantenimiento termomecánico - periodo {fecha}.</p>
    <p><u><b>Solicitamos se envíen los certificados de retenciones correspondientes a cada factura por esta misma vía al momento de realizar en pago de las mismas</u>.</b></p>
    <p><u><b>NOTA IMPORTANTE</u>:</b> FAVOR DE NO INCLUIR RETENCIONES POR IIBB QUE NO CORREPONDAN A PROV. DE BS. AS. O C.A.B.A., DADO QUE SON LAS UNICAS JURISDICCIONES EN LAS QUE TRIBUTAMOS, TAL COMO FUE INFORMADO A LA ZONAL, RESPALDADO CON LA CORRESPONDIENTE DOCUMENTACION.</p>    
    <p>Desde ya muchas gracias.</p>     
    <p>Atentamente,</p>
    <br>
    <p style="line-height: 1;">Bárbara</p>
    <p style="line-height: 1;"><b>Instalclima</b></p>""")
    
    # Fetchs attachment locations 
    file_paths = [row['Ubicacion Archivo'] for row in rows]
    
    # Creates and sends message
    message = create_message_with_attachment('me', recipients, subject, body, file_paths)
    result = send_message(service, 'me', message)

    # Add the message id to the dictionary
    # Use the recipients as the key
    message_ids[recipients] = result['id']

# %%
print(message_ids)

# %%
# Convert the dictionary to a DataFrame
df = pd.DataFrame(list(message_ids.items()), columns=['Recipients', 'Message ID'])

# Save the DataFrame as a CSV file
df.to_csv('message_ids_enero_2025.csv', index=False)

# %%
"""Something is not working here. 
Maybe I need to review how to save the messages_ids or clean the dict I'm getting"""

print(message_ids)
for key, value in message_ids.items():
    print(f"Key: {key}")
    print(f"Value: {value}")


# %%
len(message_ids) 
# NO COINCIDEN BIEN EL NUMERO DE PDFS CON LOS MENSAJES ENVIADOS. 
# CHEQUEAR CON PDFS DEFINITIVOS PERO CON EMAILS FALSOS Y TEST EMAIL

# %%
# Saves dictionary to JSON in the data folder for later 

# Assuming 'message_ids' is your dictionary
message_ids = {"key1": "value1", "key2": "value2"}

# Specify the new name in the file path
with open('data/test_message_ids.json', 'w') as f:
    json.dump(message_ids, f)

# %% [markdown]
# --TILL HERE IT WORKS--

# %%
"""To retrive the messages, I think
   No estaría funcionando
   Hipótesis, el dictionario de los message_ids esta guardando con los emails incluidos, 
   eso tendria que limpiarlo y volver a probar. De todas maneras, concuerdan los pdfs, 
   los correos electronicos y los ids de mensaje, asi que después puedo organizar mejor esta data
   Tambien podria ser que le estoy pasando mal o no pasando parámetros"""
# message = service.users().messages().get(userId='me', id=message_ids).execute()

# %% [markdown]
# Delete emails from invoice
# 
# It's not working, creo que algo de como cambian las credenciales. 
# 
# Ver despues

# %%
# Intento I
def delete_emails_by_subject(service, user_id, subject):
    # Search for all emails with the given subject in the inbox
    response = service.users().messages().list(userId=user_id, q=f'subject:{subject} in:inbox').execute()
    messages = response.get('messages', [])

    # Delete each email
    for message in messages:
        service.users().messages().delete(userId=user_id, id=message['id']).execute()

# %%
delete_emails_by_subject(service, 'me', 'Factura/s electrónica/s - Mantenimiento termomecánico - Enero 2024 (Factura/s electrónica/s - Mantenimiento termomecánico - Enero 2024)')

# %%
# Intento II
def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

def delete_emails_by_subject(service, user_id, subject):
    # Search for all emails with the given subject in the inbox
    response = service.users().messages().list(userId=user_id, q=f'subject:{subject} in:inbox').execute()
    messages = response.get('messages', [])

    # Delete each email
    for message in messages:
        service.users().messages().delete(userId=user_id, id=message['id']).execute()

# Now you can use the service object to call Gmail API methods
service = get_service()
delete_emails_by_subject(service, 'me', 'Factura/s electrónica/s - Mantenimiento termomecánico - Enero 2024 (Factura/s electrónica/s - Mantenimiento termomecánico - Enero 2024)')

# %%
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def main():
    creds = None
    # Load the credentials from the 'token.pickle' file
    if os.path.exists('token.json'):
        with open('token.json', 'rb') as token:
            creds = json.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Invalid credentials")
            return

    service = build('gmail', 'v1', credentials=creds)
    
    date = "2021/07/31"  # replace with your date
    query = f'after:{date} (from:@bpba.com.ar OR to:@bpba.com.ar)'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        print(msg['snippet'])

if __name__ == '__main__':
    main()

# %%
date = "2021/07/31"  # replace with your date
query = f'after:{date} (from:@bpba.com.ar OR to:@bpba.com.ar)'
results = service.users().messages().list(userId='me', q=query).execute()
messages = results.get('messages', [])

for message in messages:
    msg = service.users().messages().get(userId='me', id=message['id']).execute()
    print(msg['snippet'])

if __name__ == '__main__':
    main()

# %%
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import json

def main():
    creds = None
    # Load the credentials from the 'token.json' file
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token:
            creds = json.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Invalid credentials")
            return

    service = build('gmail', 'v1', credentials=creds)

    date = "2021/07/31"  # replace with your date
    query = f'after:{date} (from:@bpba.com.ar OR to:@bpba.com.ar)'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        print(msg['snippet'])

if __name__ == '__main__':
    main()


