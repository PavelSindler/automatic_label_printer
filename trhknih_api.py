import smtplib #for sending warning emails in case prining label failed
import requests #for http requests (working with API)
import os #for working with files/saving IDs of printed addresses to txt file
import pprint
import socket
import subprocess
from enum import IntEnum
import config #definition of passwords, email addresses and other confidential data in separate file named config.py


class State(IntEnum):
    ORDERED = 2	
    PAID = 3
    SENT = 4
    RECEIVED = 5
    RETURNED = 6
    CANCELED = 7

FILENAME = 'printed_IDs.txt' #file which contains order IDs of labels that were successfuly printed

#-----------------------------Functions---------------------------------

#returns IDs of all orders as list of integers
def get_orders():
    token = get_token()
    headers = {'Authorization':'Bearer '+token}
    orders_url = 'https://api.trhknih.cz/v1/order/incoming'
    r_orders = requests.get(orders_url, headers = headers)
    return r_orders.json()

def get_token():
    token_url = 'https://api.trhknih.cz/v1/oauth2/token'
    body = {
        "clientId":config.client_id,
        "clientSecret":config.client_secret
    }
    r = requests.post(token_url, json = body)
    token = r.json()['token']    
    return token

#returns json data with details about order with particular ID
def get_order_details(ID):

    token = get_token()
    headers = {'Authorization':'Bearer '+token}
    order_url = 'https://api.trhknih.cz/v1/order/incoming/'+str(ID)
    r_order = requests.get(order_url, headers = headers)
    return r_order.json()

#creates text from dictionary
#
#dictionary example:
#{'city': 'Ostrava',
# 'name': 'Veronika',
# 'postcode': '70030',
# 'street': 'Jičínská 277/3',
# 'surname': 'Zlatušková'}
def prepare_text_to_print(addr_dict):
    text = addr_dict['name']+' '+addr_dict['surname']+'\n\n'
    text = text + addr_dict['street']+'\n\n'
    text = text + addr_dict['postcode']+'  '+addr_dict['city']
    return(text)

#finds max. no of charcters which will be in one row
def get_row_len(text): 
    rows = text.split('\n')
    max_len = 0
    for i in range (len(rows)):
        if len(rows[i])>max_len:
            max_len = len(rows[i])
    return max_len

#determines label size for number of characters to fit on label
def get_font_size (row_len):
    font_size = int(-3 * row_len + 120.5)
    return font_size       
    
#prints label using API
#returns True if successful
def print_addr(text, font_size):
    
    #localhost is 127.0.0.1 
    url = 'http://localhost:8080/api/print/text?text='+text+'&font_size='+str(font_size)+'&font_family=DejaVu%20Serif%20(Book)&align=left'
    #print(url)
    return_value = False
    try:
        r = requests.get(url)
        if r.json()['success']:
            return_value = True
            send_mail(config.my_email, 'Label Printer', 'Label printed successfuly')
            print('Label printed successfuly\n\r')
        else:
            send_mail(config.my_email,'Label Printer Error: priting failed', 'Printer turned off')
            print('Printer turned off\n\r')
    except:
        send_mail(config.my_email,'Label Printer Error: priting failed', 'Server could not be reached')
        print('Server could not be reached.\n\r')
    return return_value 

def print_label(addr_dict):
    text = prepare_text_to_print(addr_dict) #create text from dictionary values
    row_ln = get_row_len(text) #get max. no of characters on one line
    fnt_size = get_font_size(row_ln) #get font size for max. no of characters so it fits on label
    success = print_addr(text, fnt_size) #print using API
    return success #true if successful

#hardcoded for usage with gmail
def send_mail(recipient, subj, message):
    msg = 'Subject: '+subj+' \n\n'+message
    conn_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    conn_smtp.ehlo()
    conn_smtp.starttls()
    conn_smtp.login(config.my_email, config.my_google_app_pwd)
    conn_smtp.sendmail(config.my_email, recipient, msg.encode('utf-8'))
    conn_smtp.quit()

#appends one ID at the end of file
def file_write_ID(ID, filename):
    exists = os.path.exists(filename)
    file = open(filename, 'a')
    if exists:
        file.write('\n'+str(ID))
    else:
        file.write(str(ID))
    file.close()

#returns list of all IDs in file
def file_read_IDs(filename):
    exists = os.path.exists(filename)
    if exists:
        file = open(filename)
        text = file.read()
        file.close()
        IDs_list = text.split('\n')
        return(IDs_list)
    else:
        return None
    

def ID_was_printed(ID):
    IDs_printed = file_read_IDs(FILENAME)
    if IDs_printed is None:
        return False #no IDs in file yet
    for i in IDs_printed:
        if i == str(ID):
            return True #we found ID in local txt file with all IDs sucessfuly printed
    return False #this ID was not printed yet

#return 'title: subtitle' string for particular book
def get_full_title(issue_id):
    token = get_token()
    headers = {'Authorization':'Bearer '+token}
    url = 'https://api.trhknih.cz/v1/issue/'+str(issue_id)
    r_issue = requests.get(url, headers = headers).json()
    title = r_issue['name']
    subtitle = r_issue['subtitle']
    if subtitle is not None:
        title = title + ': ' + subtitle
    return title

    

#--------------------------------Main-------------------------------------

#get list of IDs of all orders ever made
orders = get_orders()

for order_ID in orders:
    #for each order first check if it was processed in past
    if ID_was_printed(order_ID) == False:
        print('processing '+str(order_ID))
        details = get_order_details(order_ID)

        #pprint.pprint(details)
        
        status = details['state']
              
        if status == State.ORDERED: #not payed yet, do nothing
            continue
        elif status == State.PAID: #lets process it
            if details['shipping']['type'] == 'handover': #local handover
                #we will send mail to customer with info about bought items and contact details 
                mail = details['buyer']['email']
                print('local handover, sending info to e-mail: '+mail)
                titles = []
                for item in details['items']:
                    titles.append(get_full_title(item['issue_id']))

                if len(titles) == 1:
                    c_mail_string = 'knihu ' + titles[0]
                    c_subj_string = 'knihy ' + titles[0]
                else:
                    c_mail_string = 'knihy ' + ', '.join(titles)
                    c_subj_string = 'knih ' + ', '.join(titles)
                    
                send_mail(mail, config.mail_subject.format(c_subj_string), config.mail_text.format(c_mail_string))
                file_write_ID(order_ID, FILENAME)

            else: #send using post
                #we will print necessary labels
                shipping_details = details['shipping']['address']
                pprint.pprint(shipping_details)
                success = print_label(shipping_details)
                if success:
                    pprint.pprint(config.my_address)
                    print_label(config.my_address) #print also sender address (return address in case of failed delivery)
                    #update local file with order IDs which were successfuly printed
                    file_write_ID(order_ID, FILENAME)
            
        elif (status > State.PAID) and (status <= State.CANCELED): #it was processed in the past so lets write it to file containing processed orders
            file_write_ID(order_ID, FILENAME)
        else:
            print('uknown status: '+str(status))
