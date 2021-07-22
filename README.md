# AidaTelegramBot

Telegram bot to Explore AIDA Knowledge Graph 

It is part of the project AIDA-Bot Chat (https://github.com/infovillasimius/aidaBot)  and relies on the same data server. 
It uses Telegram API at https://api.telegram.org/ to retrieve new messages and to reply. 
The system is currently only able to process text messages.

In order to use the application you have to create a bot on telegram and get the bot unique identification code, that is used in API requestes.
Then you have to start a chat with your bot and get your chat unique ID via Telegram API (url = 'https://api.telegram.org/' + bot_id + '/getUpdates').
The bot ID and chat ID have to be set in the application code (bot_id = 'your bot id' and owner_chat_id = 'your chat id').

The application checks every ten minutes if the server is working and if not, it sends you a telegram message.

The database can be queried about authors, papers, conferences, organizations, citations and topics. It is possible to further filter the queries by specifying the name of a particular topic, conference, organization or author. The results can be sorted according to one of the following four options: publications, citations, publications in the last 5 years, citations in the last 5 years There are three types of queries:
Describe (e.g .: "describe ISWC")
Count (e.g .: "count the papers on machine learning")
List (e.g .: "list the top 5 conferences with papers on rdf graph sorted by publications").
You can enter a query all at once in natural language or through a wizard by entering one of the three activation words: describe, count or list.
