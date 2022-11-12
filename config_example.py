#this is just example of configuration file
#this file has to be saved as config.py after editing (or change import line in main script)

client_id = "sjkhakjhssasq7"
client_secret = "asdjldakljdahdkajdhksdhkahdkadhkahdkahsdkjhdskjhsd"

my_email = 'myemail@gmail.com'
my_google_app_pwd = 'my_google_app_pwd'

#Text and subject of mail (in Czech language) which will be authomaticaly sent in case of local handover
#Curly brackets {} will be replaced by purchased item name(s)
mail_text = ('Dobrý den,\nzakoupili jste si u mě {}. '
        'Osobní převzetí je možné na adrese MojeAdresa 1234 ideálně ve všední dny později večer (okolo 20 hodin).\n'
        'Prosím, kontaktujte mě na tomto mailu, případně volejte na +420123456789. Děkuji.\r\n\nS pozdravem, \r\n\nŠindler')

mail_subject = 'Koupě {} na trhknih.cz'


#sender address (used to print label for return address)
my_address = {
  'city': 'Praha',
  'name': 'Pavel',
  'surname': 'Šindler',
  'street': 'MyAddress 1234',
  'postcode': '18000'
}
