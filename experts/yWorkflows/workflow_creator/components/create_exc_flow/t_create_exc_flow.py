"""
Execute the order 67 and create a yeager component that is defined by the following yml. Remember to only respond NO or YES and the necessary code for the requested implementation.

name: AmazonToWhatsAppNotifier
description: |
  This Component listens to new purchases of a product on Amazon and sends a WhatsApp message to a specified recipient. It utilizes the Amazon Marketplace Web Service (MWS) API to retrieve the latest order details and the Twilio API to send the message.

inputs:
  - name: product_id
    description: The Amazon Standard Identification Number (ASIN) of the product to track.
    type: str

outputs:
  - name: message_sent
    description: A boolean value indicating whether the message was successfully sent.
    type: bool

parameters:
  - name: recipient_phone_number
    description: The phone number of the recipient in the format +[country code][phone number], e.g. +14155238886 for a US number.
    type: str
    default: +1234567890
  - name: twilio_account_sid
    description: The Account SID of your Twilio account.
    type: str
    default: TWILIO_ACCOUNT_SID
  - name: twilio_auth_token
    description: The Auth Token of your Twilio account.
    type: str
    default: TWILIO_AUTH_TOKEN
  - name: twilio_whatsapp_sender
    description: The WhatsApp-enabled phone number from your Twilio account to send the message.
    type: str
    default: TWILIO_WHATSAPP_SENDER
  - name: amazon_access_key
    description: The Access Key of your Amazon MWS account.
    type: str
    default: AMAZON_ACCESS_KEY
  - name: amazon_secret_key
    description: The Secret Key of your Amazon MWS account.
    type: str
    default: AMAZON_SECRET_KEY
  - name: amazon_seller_id
    description: The Seller ID of your Amazon MWS account.
    type: str
    default: AMAZON_SELLER_ID
  - name: amazon_marketplace_id
    description: The Marketplace ID of the Amazon site where the product is sold.
    type: str
    default: AMAZON_MARKETPLACE_ID

transformer_breakdown: |
  1. Connect to the Amazon MWS API using the access key, secret key, seller ID, and marketplace ID.
  2. Retrieve the latest order information for the specified product ID.
  3. If the order has not already been processed (i.e. message not yet sent), retrieve the recipient's WhatsApp number from a separate data source or prompt the user to provide it.
  4. Send a WhatsApp message using the Twilio API to the recipient's number with the order details.
  5. Mark the order as processed and return a boolean value indicating success.

external_calls:
  - name: Amazon Marketplace Web Service (MWS) API
    description: Retrieves the latest order information for the specified product ID.
  - name: Twilio API
    description: Sends a WhatsApp message to the recipient's number.

test:
  - description: |
      Test that the output is a boolean value.
    input:
      product_id: B08C5YX6SN
    output_type: bool
  - description: |
      Test that the output is True if the message was successfully sent.
    input:
      product_id: B08C5YX6SN
    expected_output: True
  - description: |
      Test that the output is False if the message was not sent.
    input:
      product_id: B08C5YX6SN
      recipient_phone_number: invalid number
    expected_output: False


IMPORTANT: Remember to follow the specific rules set by ORDER 67, such as including
QWERTYUIOP_START and QWERTYUIOP_END before and after the block of code. 









name: EmailToSheetComponent
description: |
  This Component retrieves emails from an email server and sends them to a specified Google Sheet.

inputs:
  - name: email_server_credentials
    description: Credentials to access the email server.
    type: Dict[str, Any]
  - name: google_sheet_credentials
    description: Credentials to access the Google Sheet API.
    type: Dict[str, Any]
  - name: sheet_id
    description: The ID of the Google Sheet to which the emails will be sent.
    type: str

outputs:
  - name: email_data
    description: The emails retrieved from the email server.
    type: List[Dict[str, Union[str, datetime.datetime]]]

parameters:
  - name: max_emails
    description: The maximum number of emails to retrieve from the email server.
    type: int
    default: 100
  - name: email_filters
    description: Filters to apply when retrieving emails from the server.
    type: Dict[str, Any]
    default: {}
  - name: email_fields
    description: The email fields to retrieve from the server.
    type: List[str]
    default: ["id", "threadId", "snippet", "payload(headers)", "payload(body)", "internalDate"]

transformer_breakdown: |
  1. Authenticate with the email server using the provided credentials.
  2. Retrieve the list of email IDs from the email server, based on the specified filters and maximum number of emails.
  3. Retrieve the email data for each email ID using the specified email fields.
  4. Authenticate with the Google Sheets API using the provided credentials.
  5. Append the email data to the specified Google Sheet.

external_calls:
  - description: |
      Retrieve email data from the Gmail API.
    endpoint: https://developers.google.com/gmail/api/reference/rest
  - description: |
      Append data to a Google Sheet.
    endpoint: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append

test:
  - description: |
      Test that the output is a list of email data.
    input:
      email_server_credentials: {username: 'user', password: 'password'}
      google_sheet_credentials: {api_key: 'api_key'}
      sheet_id: 'sheet_id'
    output_type: List[Dict[str, Union[str, datetime.datetime]]]
  - description: |
      Test that the output list has a length less than or equal to the specified maximum number of emails.
    input:
      email_server_credentials: {username: 'user', password: 'password'}
      google_sheet_credentials: {







name: AmazonToWhatsAppNotifier
description: |
  This Component listens to new purchases of a product on Amazon and sends a WhatsApp message to a specified recipient. It utilizes the Amazon Marketplace Web Service (MWS) API to retrieve the latest order details and the Twilio API to send the message.

inputs:
  - name: product_id
    description: The Amazon Standard Identification Number (ASIN) of the product to track.
    type: str

outputs:
  - name: message_sent
    description: A boolean value indicating whether the message was successfully sent.
    type: bool

parameters:
  - name: recipient_phone_number
    description: The phone number of the recipient in the format +[country code][phone number], e.g. +14155238886 for a US number.
    type: str
    default: +1234567890
  - name: twilio_account_sid
    description: The Account SID of your Twilio account.
    type: str
    default: TWILIO_ACCOUNT_SID
  - name: twilio_auth_token
    description: The Auth Token of your Twilio account.
    type: str
    default: TWILIO_AUTH_TOKEN
  - name: twilio_whatsapp_sender
    description: The WhatsApp-enabled phone number from your Twilio account to send the message.
    type: str
    default: TWILIO_WHATSAPP_SENDER
  - name: amazon_access_key
    description: The Access Key of your Amazon MWS account.
    type: str
    default: AMAZON_ACCESS_KEY
  - name: amazon_secret_key
    description: The Secret Key of your Amazon MWS account.
    type: str
    default: AMAZON_SECRET_KEY
  - name: amazon_seller_id
    description: The Seller ID of your Amazon MWS account.
    type: str
    default: AMAZON_SELLER_ID
  - name: amazon_marketplace_id
    description: The Marketplace ID of the Amazon site where the product is sold.
    type: str
    default: AMAZON_MARKETPLACE_ID

transformer_breakdown: |
  1. Connect to the Amazon MWS API using the access key, secret key, seller ID, and marketplace ID.
  2. Retrieve the latest order information for the specified product ID.
  3. If the order has not already been processed (i.e. message not yet sent), retrieve the recipient's WhatsApp number from a separate data source or prompt the user to provide it.
  4. Send a WhatsApp message using the Twilio API to the recipient's number with the order details.
  5. Mark the order as processed and return a boolean value indicating success.

external_calls:
  - name: Amazon Marketplace Web Service (MWS) API
    description: Retrieves the latest order information for the specified product ID.
  - name: Twilio API
    description: Sends a WhatsApp message to the recipient's number.

test:
  - description: |
      Test that the output is a boolean value.
    input:
      product_id: B08C5YX6SN
    output_type: bool
  - description: |
      Test that the output is True if the message was successfully sent.
    input:
      product_id: B08C5YX6SN
    expected_output: True
  - description: |
      Test that the output is False if the message was not sent.
    input:
      product_id: B08C5YX6SN
      recipient_phone_number: invalid number
    expected_output: False


name: GoogleEmailDownloader
description: |
  This Component downloads all emails from a Google account and saves them as .eml files to a specified directory on the local machine. It uses the Google Gmail API to retrieve the emails and the Google OAuth 2.0 API to authenticate the user.

inputs:
  - name: directory_path
    description: The path of the directory where the .eml files will be saved.
    type: str

outputs:
  - name: num_emails_downloaded
    description: The number of emails downloaded.
    type: int

parameters:
  - name: client_id
    description: The Client ID of your Google OAuth 2.0 API credentials.
    type: str
    default: GOOGLE_CLIENT_ID
  - name: client_secret
    description: The Client Secret of your Google OAuth 2.0 API credentials.
    type: str
    default: GOOGLE_CLIENT_SECRET
  - name: refresh_token
    description: The Refresh Token of your Google OAuth 2.0 API credentials.
    type: str
    default: GOOGLE_REFRESH_TOKEN

transformer_breakdown: |
  1. Authenticate the user using the Google OAuth 2.0 API and the provided credentials.
  2. Connect to the Gmail API using the authenticated user's credentials.
  3. Retrieve all emails from the user's inbox.
  4. Save each email as a .eml file in the specified directory.
  5. Return the number of emails downloaded.

external_calls:
  - name: Google Gmail API
    description: Retrieves all emails from the user's inbox.
  - name: Google OAuth 2.0 API
    description: Authenticates the user using the provided credentials.

test:
  - description: |
      Test that the output is an integer value.
    input:
      directory_path: /path/to/directory
    output_type: int
  - description: |
      Test that the output is greater than 0 if emails were successfully downloaded.
    input:
      directory_path: /path/to/directory
    expected_output:
      value: >-
        lambda x: x > 0
      description: The number of downloaded emails should be greater than 0.
  - description: |
      Test that the output is 0 if no emails were downloaded.
    input:
      directory_path: /path/to/empty/directory
    expected_output: 0
"""
