# spanish_bert_telebot
Telegram bot using pretrained spanish language BERT models for sentiment analysis and question answering

The models being used are:
* [pysentimiento/robertuito-sentiment-analysis](https://huggingface.co/pysentimiento/robertuito-sentiment-analysis) for sentiment analysis in spanish
* [mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es](https://huggingface.co/mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es) for question answering in spanish

To implement it first a Telegram bot needs to be created ([guide here](https://core.telegram.org/bots/features#creating-a-new-bot)) and a .env file with your bot token
![Screenshot 2023-11-19 182703](https://github.com/agustincosta/spanish_bert_telebot/assets/38562543/a6c81b93-fa72-4b90-bec7-75ac22dd27d1)

![Screenshot 2023-11-19 183230](https://github.com/agustincosta/spanish_bert_telebot/assets/38562543/a5f3dd8e-b3c9-4146-8ca2-b8e7330fc5b8)

