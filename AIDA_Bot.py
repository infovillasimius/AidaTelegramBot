import copy
import json
import random
import urllib
import urllib.parse
import urllib.request

data_server_url = 'http://aidabot.ddns.net/api?pass=123abc&'

intents = {
    'cancel': ['bye', 'goodbye'],
    'help': ['help'],
    'count': ['count', 'how many'],
    'list': ['list'],
    'describe': ['describe', 'who is', 'who are', 'what about', 'what is', 'what are', 'what', 'who'],
    'hello': ['hello', 'hi'],
    'reset': ['cancel', 'stop']
}

combinations = {
    'authors': 'papers',
    'papers': 'papers',
    'conferences': 'conferences',
    'organizations': 'organizations',
    'citations': 'papers'
}

subject_categories = ['authors', 'papers', 'conferences', 'organizations', 'citations']
object_categories = ['topics', 'conferences', 'organizations', 'authors', 'papers']
list_subject_categories = ['authors', 'papers', 'conferences', 'organizations', 'topics']
tags_list = ['<b>', '</b>', '<i>', '</i>']
marks_list = ['.', '?', ';', ',']
orders = ['publications', 'citations', 'publications in the last 5 years', 'citations in the last 5 years']
homonyms_objects = ['topic', 'conference', 'organization', 'author', 'paper']
homonyms_list = [' affiliated with ', ' author of the paper: ', ', author with ', ' publications']
list_verbs = ['is', 'are']
list_order = ['publication', 'citation', 'publication in the last 5 years', 'citation in the last 5 years']
cancel_words = ['cancel', 'stop', 'enough', 'no', 'nothing']

templates = {
    'WELCOME_MSG': [
        '<b>Hello!</b> You can ask me to <b>describe</b>, <b>list</b>, or <b>count</b> any scholarly entity.',
        'Welcome, you can ask me to <b>describe</b>, <b>list</b>, or <b>count</b> any scholarly entity. What would '
        'you like to try?'],
    'HELLO_MSG': ['Hello! What can I do for you?', 'Hi! what could i do for you?'],
    'HELP_MSG': [
        'You can ask to <b>count</b> or <b>list</b> <i>authors</i>, <i>papers</i>, <i>conferences</i>, '
        '<i>organizations</i>, <i>topics</i> and <i>citations</i> or to <b>describe</b> <i>authors</i>, '
        '<i>conferences</i> or <i>organizations</i>. Start a query with <b>list</b>, <b>count</b> or <b>describe</b>.',
        'You can ask a query starting with <b>count</b>, <b>list</b>, or <b>describe</b>.'],
    'GOODBYE_MSG': ['Goodbye!', 'Bye!', 'See you later!'],

    'FALLBACK_MSG': 'Sorry, I don\'t know that. Please try again.',
    'ERROR_MSG': 'Sorry, there was an error. Please try again.',

    'HOMONYMS_MSG': 'I found different homonyms (list sorted by number of publications): ${msg} ',

    'SUBJECT_REQUEST_MSG': 'I can count <b>papers</b>, <b>authors</b>, <b>conferences</b>, <b>organizations</b> and '
                           '<b>citations</b>. What do you want me to count?',
    'SUBJECT_WRONG_MSG': "Sorry, I can\'t count <b>${sub}</b>. I can count <b>papers</b>, <b>authors</b>, "
                         "<b>conferences</b>, <b>organizations</b> and <b>citations</b>. What do you prefer?",
    'SUBJECT_REQUEST_REPROMPT_MSG': 'I can count <b>papers</b>, <b>authors</b>, <b>conferences</b>, '
                                    '<b>organizations</b> and <b>citations</b>. What do you prefer?',
    'INSTANCE_MSG': "what is the <b>name</b> of the ${list} whose <b>${sub}</b> I should count? You can say "
                    "<b>all</b> for the full list",
    'INSTANCE2_MSG': "what is the <b>name</b> of the ${list} whose <b>${sub}</b> I should count?",
    'ITEM_MSG': "Searching for <b>${ins}</b>, I got: ${msg}. To choose, say the number. Which one is correct?",
    'INTENT_CONFIRMATION_1_MSG': "Do you want to know how many <b>${sub}</b> ${prep} ${obj} are in the AIDA database?",
    'INTENT_CONFIRMATION_2_MSG': "Do you want to know how many <b>${sub}</b> ${prep} <b>${ins}</b> ${obj} are in the "
                                 "AIDA database?",
    'TOO_GENERIC_MSG': "Your search for <b>${ins}</b> got ${results}. You need to try again and to be more specific. "
                       "Could you tell me the exact name?",
    'NO_RESULT_MSG': "Your search for ${ins} got no result. You need to try again. What could I search for you?",
    'QUERY_1_MSG': "I found <b>${num}</b> ${sub} ${prep} <b>${ins}</b> ${obj}. You can ask to perform another "
                   "query on the data contained in the AIDA database or ask for Help. What would you like to try?",
    'QUERY_2_MSG': "I found <b>${num}</b> different ${sub} ${prep} ${obj}. You can ask to perform another query "
                   "on the data contained in the AIDA database or ask for Help. What would you like to try?",

    'REPROMPT_MSG': 'So, what would you like to ask?',
    'NO_QUERY_MSG': 'Sorry, you asked for a query that is not yet implemented. You can ask to perform another '
                    'query on the data contained in the AIDA database or ask for Help. What would you like to try?',

    'REPROMPT_END_MSG': 'You could ask me for another query or say stop to quit',
    'NO_SENSE_MSG': 'I\'m sorry but the query resulting from the chosen options doesn\'t make sense. Try again. '
                    'You can ask to perform another query on the data contained in the AIDA database or ask for '
                    'Help. What would you like to try?',

    'LIST_WRONG_NUMBER_MSG': 'The number ${num} , you should tell me a number higher than one and smaller than eleven.',
    'LIST_SUBJECT_REQUEST_MSG': 'I can list <b>papers</b>, <b>authors</b>, <b>conferences</b>, <b>organizations</b> '
                                'and <b>topics</b>. What do you want me to list?',
    'LIST_SUBJECT_WRONG_MSG': 'Sorry, I can\'t list <b>${sub}</b>. I can list <b>papers</b>, <b>authors</b>, '
                              '<b>conferences</b>, <b>organizations</b> and <b>topics</b>. What do you prefer?',
    'LIST_SUBJECT_REQUEST_REPROMPT_MSG': 'I can list <b>papers</b>, <b>authors</b>, <b>conferences</b>, '
                                         '<b>organizations</b> and <b>topics</b>. What do you prefer?',
    'LIST_ORDER_MSG': 'Which sorting option do you prefer between: (1) <b>publications</b>, (2) <b>citations</b>, '
                      '(3) <b>publications in the last 5 years</b> and (4) <b>citations in the last 5 years</b>?',
    'LIST_PAPERS_ORDER_MSG': 'Which sorting option do you prefer between: (1) <b>citations</b> and (2) <b>citations '
                             'in the last 5 years?</b>',

    'LIST_PAPERS_ORDER_WRONG_MSG': 'Sorry, I can\'t list <b>${sub}</b> sorted by <b>${order}</b>. I can sort them by '
                                   '(1)  <b>citations</b> and by (2) <b>citations in the last 5 years</b>. What do '
                                   'you prefer?',
    'LIST_ORDER_WRONG_MSG': 'Sorry, I can\'t list <b>${sub}</b> sorted by <b>${order}</b>. I can sort them by: (1) '
                            '<b>publications</b>, (2) <b>publications in the last 5 years</b>, (3) <b>citations</b>, '
                            '(4) <b>citations in the last 5 years</b>. What do you prefer?',
    'LIST_INSTANCE_MSG': 'what is the <b>name</b> of the ${list} for which <b>${sub}</b> should be in the top ${num}? '
                         'You can say <b>all</b> for the full list',
    'LIST_INTENT_CONFIRMATION_1_MSG': 'Do you want to know which are the top ${num} <b>${sub}</b> ${prep} ${obj}, '
                                      'by number of <b>${order}</b>, in the AIDA database?',
    'LIST_INTENT_CONFIRMATION_2_MSG': 'Do you want to know which are the top ${num} <b>${sub}</b>, by number of <b>${'
                                      'order}</b>, ${prep} <b>${ins}</b> ${obj} in the Aida database?',
    'LIST_QUERY_MSG': 'In the AIDA database, the top ${num} <b>${sub}</b> ${prep} <b>${ins}</b> ${obj} - by number of '
                      '<b>${order}</b> - ${verb}: ${lst} You can ask to perform another query on the data '
                      'contained in the AIDA database or ask for Help. What would you like to try?',
    'LIST_NO_RESULT_MSG': 'In the AIDA database, there are no <b>${sub}</b> ${prep} <b>${ins}</b> ${obj}. You '
                          'can ask to perform another query on the data contained in the AIDA database or ask for '
                          'Help. What would you like to try?',

    'DSC_TOO_GENERIC_MSG': 'Your search for <b>${ins}</b> got ${results}. You need to try again and to be more '
                           'specific. What is the <b>name</b> of the <b>author</b> or <b>conference</b> or '
                           '<b>organization</b> you want to know about?',
    'DSC_NO_RESULT_MSG': 'Your search for <b>${ins}</b> got no result. You need to try again. What is the name of the '
                         'author or conference you want to know about?',
    'DESCRIBE_INSTANCE_MSG': 'What is the <b>name</b> of the <b>author</b> or <b>conference</b> or '
                             '<b>organization</b> you want to know about?',
    'DESCRIBE_CONFIRM_MSG': 'Do you want to know something about ${ins}?'
}

templates2 = {
    'WELCOME_MSG': ['Hello! You can ask me to describe, list, or count any scholarly entity.',
                    'Welcome, you can ask me to describe, list, or count any scholarly entity. What would you like to '
                    'try?'],
    'HELLO_MSG': ['Hello! What can I do for you?', 'Hi! what could i do for you?'],
    'OK_MSG': 'Ok',
    'HELP_MSG': [
        'You can ask to count or list authors, papers, conferences, organizations, topics and citations or to '
        'describe authors, conferences and organizations. Start a query with list, count or describe.',
        'You can ask a query starting with count, list or describe.'],
    'GOODBYE_MSG': ['Goodbye!', 'Bye!', 'See you later!'],
    'REFLECTOR_MSG': 'You just triggered ${intent}',
    'FALLBACK_MSG': 'Sorry, I don\'t know that. Please try again.',
    'ERROR_MSG': 'Sorry, there was an error. Please try again.',

    'HOMONYMS_MSG': 'I found different homonyms: ${msg} ',

    'SUBJECT_REQUEST_MSG': 'I can count papers, authors, conferences, organizations and citations. What do you want '
                           'me to count?',
    'SUBJECT_WRONG_MSG': "Sorry, I can\'t count ${sub}. I can count papers, authors, conferences, organizations and "
                         "citations. What do you prefer?",
    'SUBJECT_REQUEST_REPROMPT_MSG': 'I can count papers, authors, conferences, organizations and citations. What do '
                                    'you prefer?',
    'INSTANCE_MSG': "what is the name of the ${list} whose ${sub} I should count? You can say all for the full list",
    'INSTANCE2_MSG': "what is the name of the ${list} whose ${sub} I should count?",
    'ITEM_MSG': "Searching for ${ins}, I got: ${msg}. To choose, say the number. Which one is correct?",
    'INTENT_CONFIRMATION_1_MSG': "Do you want to know how many ${sub} ${prep} ${obj} are in the AIDA database?",
    'INTENT_CONFIRMATION_2_MSG': "Do you want to know how many ${sub} ${prep} ${ins} ${obj} are in the AIDA database?",
    'TOO_GENERIC_MSG': "Your search for ${ins} got ${results}. You need to try again and to be more specific. Could "
                       "you tell me the exact name?",
    'NO_RESULT_MSG': "Your search for ${ins} got no result. You need to try again. What could I search for you?",
    'QUERY_1_MSG': "I found ${num} ${sub} ${prep} ${ins} ${obj}. You can ask to perform another query on the data "
                   "contained in the AIDA database or ask for Help. What would you like to try?",
    'QUERY_2_MSG': "I found ${num} different ${sub} ${prep} ${obj}. You can ask to perform another query on the data "
                   "contained in the AIDA database or ask for Help. What would you like to try?",

    'REPROMPT_MSG': 'So, what would you like to ask?',
    'NO_QUERY_MSG': 'Sorry, you asked for a query that is not yet implemented. You can ask to perform another query '
                    'on the data contained in the AIDA database or ask for Help. What would you like to try?',

    'REPROMPT_END_MSG': 'You could ask me for another query or say stop to quit',
    'NO_SENSE_MSG': 'I\'m sorry but the query resulting from the chosen options doesn\'t make sense. Try again. You '
                    'can ask to perform another query on the data contained in the AIDA database or ask for Help. '
                    'What would you like to try?',

    'LIST_WRONG_NUMBER_MSG': 'The number ${num} , you should tell me a number higher than one and smaller than eleven.',
    'LIST_SUBJECT_REQUEST_MSG': 'I can list papers, authors, conferences, organizations and topics. What do you want '
                                'me to list?',
    'LIST_SUBJECT_WRONG_MSG': 'Sorry, I can\'t list ${sub}. I can list papers, authors, conferences, organizations '
                              'and topics. What do you prefer?',
    'LIST_SUBJECT_REQUEST_REPROMPT_MSG': 'I can list papers, authors, conferences, organizations and topics. What do '
                                         'you prefer?',
    'LIST_ORDER_MSG': 'Which sorting option do you prefer between: (1) publications, (2) citations, '
                      '(3) publications in the last 5 years, (4) citations in the last 5 years?',
    'LIST_PAPERS_ORDER_MSG': 'Which sorting option do you prefer between: (1) citations and (2) citations in the last '
                             '5 years?',
    'LIST_PAPERS_ORDER_WRONG_MSG': 'Sorry, I can\'t list ${sub} sorted by ${order}. I can sort them by: (1) citations '
                                   'and (2) citations in the last 5 years. What do you prefer?',
    'LIST_ORDER_WRONG_MSG': 'Sorry, I can\'t list ${sub} sorted by ${order}. I can sort them by: (1) publications, '
                            '(2) publications in the last 5 years, (3) citations, (4) citations in the last 5 years. '
                            'What do you prefer?',
    'LIST_INSTANCE_MSG': 'what is the name of the ${list} for which ${sub} should be in the top ${num}? You can say '
                         'all for the full list',
    'LIST_INTENT_CONFIRMATION_1_MSG': 'Do you want to know which are the top ${num} ${sub} ${prep} ${obj}, by number '
                                      'of ${order}, in the AIDA database?',
    'LIST_INTENT_CONFIRMATION_2_MSG': 'Do you want to know which are the top ${num} ${sub}, by number of ${order}, '
                                      '${prep} ${ins} ${obj} in the Aida database?',
    'LIST_QUERY_MSG': 'In the AIDA database, the top ${num} ${sub} ${prep} ${ins} ${obj} - by number of ${order} - ${'
                      'verb}: ${lst} You can ask to perform another query on the data contained in the AIDA database '
                      'or ask for Help. What would you like to try?',
    'LIST_NO_RESULT_MSG': 'In the AIDA database, there are no ${sub} ${prep} ${ins} ${obj}. You can ask to perform '
                          'another query on the data contained in the AIDA database or ask for Help. What would you '
                          'like to try?',

    'DSC_TOO_GENERIC_MSG': 'Your search for ${ins} got ${results}. You need to try again and to be more specific. '
                           'What is the name of the author or conference you want to know about?',
    'DSC_NO_RESULT_MSG': 'Your search for ${ins} got no result. You need to try again. What is the name of the author '
                         'or conference you want to know about?',
    'DESCRIBE_INSTANCE_MSG': 'What is the name of the author or conference you want to know about?',
    'DESCRIBE_CONFIRM_MSG': 'Do you want to know something about ${ins}?'
}

count_dict = {
    'sub': {
        'authors': {
            'topics': 'authors',
            'conferences': 'authors',
            'organizations': 'authors',
            'authors': 'authors',
            'papers': 'authors'
        },
        'papers': {
            'topics': 'papers',
            'conferences': 'papers',
            'organizations': 'papers',
            'authors': 'papers',
            'papers': ''
        },
        'conferences': {
            'topics': 'conferences',
            'conferences': 'conferences',
            'organizations': 'conferences',
            'authors': 'conferences',
            'papers': ''
        },
        'organizations': {
            'topics': 'organizations',
            'conferences': 'organizations',
            'organizations': 'organizations',
            'authors': 'organizations',
            'papers': ''
        },
        'citations': {
            'topics': 'citations',
            'conferences': 'citations',
            'organizations': 'citations',
            'authors': 'citations',
            'papers': ''
        }
    },
    'prep': {
        'authors': {
            'topics': 'who have written papers on',
            'conferences': 'who have written papers for',
            'organizations': 'affiliated to the',
            'authors': '',
            'papers': ''
        },
        'papers': {
            'topics': 'on',
            'conferences': 'from',
            'organizations': 'from authors affiliated to the',
            'authors': 'written by the author',
            'papers': ''
        },
        'conferences': {
            'topics': 'with papers on',
            'conferences': '',
            'organizations': 'with papers by authors affiliated to the',
            'authors': 'with papers written by the author',
            'papers': ''
        },
        'organizations': {
            'topics': 'with papers on',
            'conferences': 'with papers at',
            'organizations': '',
            'authors': 'with',
            'papers': ''
        },
        'citations': {
            'topics': 'of papers on',
            'conferences': 'of papers from',
            'organizations': 'of papers written by authors affiliated to the',
            'authors': 'of papers written by the author',
            'papers': ''
        }
    },
    'obj': {
        'authors': {
            'topics': 'topic',
            'conferences': 'conferences',
            'organizations': '',
            'authors': '',
            'papers': ''
        },
        'papers': {
            'topics': 'topic',
            'conferences': 'conferences',
            'organizations': '',
            'authors': '',
            'papers': 'papers'
        },
        'conferences': {
            'topics': 'topic',
            'conferences': '',
            'organizations': '',
            'authors': '',
            'papers': ''
        },
        'organizations': {
            'topics': '',
            'conferences': 'conferences',
            'organizations': '',
            'authors': 'among their affiliated authors',
            'papers': ''
        },
        'citations': {
            'topics': 'topic',
            'conferences': 'conferences',
            'organizations': '',
            'authors': '',
            'papers': ''
        }
    }
}

count_legal_queries = {
    'authors': {
        'topics': [True, False],
        'conferences': [True, True],
        'organizations': [True, False],
        'authors': [False, False],
        'papers': [False, True],
    },
    'papers': {
        'topics': [True, False],
        'conferences': [True, True],
        'organizations': [True, False],
        'authors': [True, False],
        'papers': [False, True],
    },
    'conferences': {
        'topics': [True, False],
        'conferences': [False, True],
        'organizations': [True, False],
        'authors': [True, False],
        'papers': [False, False],
    },
    'organizations': {
        'topics': [True, False],
        'conferences': [True, False],
        'organizations': [False, True],
        'authors': [True, False],
        'papers': [False, False],
    },
    'citations': {
        'topics': [True, False],
        'conferences': [True, False],
        'organizations': [True, False],
        'authors': [True, False],
        'papers': [False, False],
    }
}

obj_cat = [
    ['authors', 'conference acronyms', 'conference names', 'organizations'],
    ['topics', 'conferences', 'organizations', 'authors', 'papers']
]

item_question_object = {
    'topics': '<b>topic</b> or ',
    'conferences': '<b>conference</b> or ',
    'organizations': '<b>organization</b> or ',
    'authors': '<b>author</b>'
}

numbers = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
    'nine', 'ten', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', 'first', 'second', 'third',
    'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth'
]

list_legal_queries = {
    'authors': {
        'topics': [True, True],
        'conferences': [True, True],
        'organizations': [True, True],
        'authors': [False, False],
        'all': [True, True],
    },
    'papers': {
        'topics': [False, True],
        'conferences': [False, True],
        'organizations': [False, True],
        'authors': [False, True],
        'all': [False, True],
    },
    'conferences': {
        'topics': [True, True],
        'conferences': [False, False],
        'organizations': [True, True],
        'authors': [True, True],
        'all': [True, True],
    },
    'organizations': {
        'topics': [True, True],
        'conferences': [True, True],
        'organizations': [False, False],
        'authors': [False, False],
        'all': [True, True],
    },
    'topics': {
        'topics': [False, False],
        'conferences': [True, True],
        'organizations': [True, True],
        'authors': [True, True],
        'all': [True, True],
    }
}

list_dict = {
    'publications': {
        'sub': {
            'authors': {
                'topics': 'authors',
                'conferences': 'authors',
                'organizations': 'authors',
                'authors': 'authors',
                'papers': 'authors'
            },
            'papers': {
                'topics': 'papers',
                'conferences': 'papers',
                'organizations': 'papers',
                'authors': 'papers',
                'papers': ''
            },
            'conferences': {
                'topics': 'conferences',
                'conferences': 'conferences',
                'organizations': 'conferences',
                'authors': 'conferences',
                'papers': ''
            },
            'organizations': {
                'topics': 'organizations',
                'conferences': 'organizations',
                'organizations': 'organizations',
                'authors': 'organizations',
                'papers': ''
            },
            'topics': {
                'topics': 'topics',
                'conferences': 'topics',
                'organizations': 'topics',
                'authors': 'topics',
                'papers': ''
            }
        },
        'prep': {
            'authors': {
                'topics': 'who have written papers on',
                'conferences': 'who have written papers for',
                'organizations': 'affiliated to the',
                'authors': '',
                'papers': ''
            },
            'papers': {
                'topics': 'on',
                'conferences': 'from',
                'organizations': 'from authors affiliated to the',
                'authors': 'written by the author',
                'papers': ''
            },
            'conferences': {
                'topics': 'with papers on',
                'conferences': '',
                'organizations': 'with papers by authors affiliated to the',
                'authors': 'with papers written by the author',
                'papers': ''
            },
            'organizations': {
                'topics': 'with papers on',
                'conferences': 'with papers at',
                'organizations': '',
                'authors': 'with',
                'papers': ''
            },
            'topics': {
                'topics': '',
                'conferences': 'of papers from',
                'organizations': 'of papers written by authors affiliated to the',
                'authors': 'of papers written by the author',
                'papers': ''
            }
        },
        'obj': {
            'authors': {
                'topics': 'topic',
                'conferences': 'conferences',
                'organizations': '',
                'authors': '',
                'papers': ''
            },
            'papers': {
                'topics': 'topic',
                'conferences': 'conferences',
                'organizations': '',
                'authors': '',
                'papers': 'papers'
            },
            'conferences': {
                'topics': 'topic',
                'conferences': '',
                'organizations': '',
                'authors': '',
                'papers': ''
            },
            'organizations': {
                'topics': '',
                'conferences': 'conferences',
                'organizations': '',
                'authors': 'among their affiliated authors',
                'papers': ''
            },
            'topics': {
                'topics': '',
                'conferences': 'conferences',
                'organizations': '',
                'authors': '',
                'papers': ''
            }
        }
    },
    'citations': {
        'sub': {
            'authors': {
                'topics': 'authors',
                'conferences': 'authors',
                'organizations': 'authors',
                'authors': 'authors',
                'papers': 'authors'
            },
            'papers': {
                'topics': 'papers',
                'conferences': 'papers',
                'organizations': 'papers',
                'authors': 'papers',
                'papers': ''
            },
            'conferences': {
                'topics': 'conferences',
                'conferences': 'conferences',
                'organizations': 'conferences',
                'authors': 'conferences',
                'papers': ''
            },
            'organizations': {
                'topics': 'organizations',
                'conferences': 'organizations',
                'organizations': 'organizations',
                'authors': 'organizations',
                'papers': ''
            },
            'topics': {
                'topics': 'topics',
                'conferences': 'topics',
                'organizations': 'topics',
                'authors': 'topics',
                'papers': ''
            }
        },
        'prep': {
            'authors': {
                'topics': 'who have written papers on',
                'conferences': 'who have written papers for',
                'organizations': 'affiliated to the',
                'authors': '',
                'papers': ''
            },
            'papers': {
                'topics': 'on',
                'conferences': 'from',
                'organizations': 'from authors affiliated to the',
                'authors': 'written by the author',
                'papers': ''
            },
            'conferences': {
                'topics': 'with papers on',
                'conferences': '',
                'organizations': 'with papers by authors affiliated to the',
                'authors': 'with papers written by the author',
                'papers': ''
            },
            'organizations': {
                'topics': 'with papers on',
                'conferences': 'with papers at',
                'organizations': '',
                'authors': 'with',
                'papers': ''
            },
            'topics': {
                'topics': '',
                'conferences': 'of papers from',
                'organizations': 'of papers written by authors affiliated to the',
                'authors': 'of papers written by the author',
                'papers': ''
            }
        },
        'obj': {
            'authors': {
                'topics': 'topics',
                'conferences': 'conferences',
                'organizations': '',
                'authors': '',
                'papers': ''
            },
            'papers': {
                'topics': 'topics',
                'conferences': 'conferences',
                'organizations': '',
                'authors': '',
                'papers': 'papers'
            },
            'conferences': {
                'topics': 'topics',
                'conferences': '',
                'organizations': '',
                'authors': '',
                'papers': ''
            },
            'organizations': {
                'topics': '',
                'conferences': 'conferences',
                'organizations': '',
                'authors': 'among their affiliated authors',
                'papers': ''
            },
            'topics': {
                'topics': '',
                'conferences': 'conferences',
                'organizations': '',
                'authors': '',
                'papers': ''
            }
        }
    }
}

dsc_list = [' is an author', ' affiliated to ', ' affiliated to the ', 'Author rating: ', 'Publications: ',
            'Citations: ', 'Total number of co-authors: ', 'The top topic in terms of publications is: ',
            'The top topics in terms of publications are: ', 'The top conference in terms of publications is: ',
            'The top conferences in terms of publications are: ', 'The top journal in terms of publications is: ',
            'The top journals in terms of publications are: ', ', acronym of ',
            ', is a conference whose focus areas are: ', 'The rankings are: ', 'Citations in the last 5 years: ',
            'Years of activity: from ', ' to ', 'Number of publications in the last year: ',
            'The top country in terms of publications is: ', 'The top countries in terms of publications are: ',
            'The top organization in education is: ', 'The top organizations in education are: ',
            'The top organization in industry is: ', 'The top organizations in industry are: ',
            'Publications in the last 5 years: ', 'Number of affiliated authors: ']

session = {'level': 0, 'intent': {'name': '', 'level': 0, 'slots': {}}, 'confirmation': True, 'answer': ''}


def set_session(new_session):
    global session
    session = new_session


def get_session():
    global session
    return session


def welcome():
    setMessage('WELCOME_MSG')


def get_data(cmd, ins):
    response = urllib.request.urlopen(data_server_url + cmd + urllib.parse.quote(str(ins)))
    data = json.load(response)
    # print data
    assert isinstance(data, dict)
    return data


def getIntent(msg):
    message = msg.lower().split(" ")
    for key in intents:
        for i in range(len(message)):
            for j in range(len(intents[key])):
                words = intents[key][j].split(' ')
                intent_length = len(words)
                for k in range(len(words)):
                    z = (+i) + (+k)
                    if z < len(message) and words[k] == message[z]:
                        intent_length -= 1
                if intent_length == 0:
                    return [key, intents[key][j]]
    return ['fallback', '']


def getUserDescribeQueryText(msg):
    query = msg
    idx = -1
    for i in range(len(intents['describe'])):
        if intents['describe'][i] in query:
            idx = query.index(intents['describe'][i])
        if idx >= 0:
            query = query[idx + len(intents['describe'][i]) + 1: len(query)]
            return query
    return query


def setMessage(msg, options=None):
    value = templates[msg]
    if isinstance(value, list):
        value = value[int(random.randint(0, len(value) - 1))]
    lst_ = []
    if options is not None and len(options) > 0:
        n = -1
        str0 = value
        while '$' in str0:
            n = str0.index('$', n + 1)
            n1 = str0.index("}", n) + 1
            str1 = str0[n: n1]
            lst_.append(str1)
            str0 = str0[0:n] + str0[n + 1: len(str0)]

        for i in options:
            if isinstance(options[i], list):
                value = value.replace('${' + i + '}', str(options[i][0]))
            else:
                value = value.replace('${' + i + '}', str(options[i]))
        for i in lst_:
            value = value.replace(i, '')
    while '  ' in value:
        value = value.replace('  ', ' ')

    value = value.replace(' . ', '. ')
    value = value.replace(' , ', ', ')
    appendMessage(value)


def appendMessage(value):
    session['answer'] = value


def item_question(subject):
    msg = ''
    sub = subject

    if count_legal_queries[sub]['topics'][0]:
        msg += item_question_object['topics']
    if count_legal_queries[sub]['conferences'][0]:
        msg += item_question_object['conferences']
    if count_legal_queries[sub]['organizations'][0]:
        msg += item_question_object['organizations']
    if count_legal_queries[sub]['authors'][0]:
        msg += item_question_object['authors']
    s = msg[len(msg) - 4: len(msg)]
    if s == ' or ':
        msg = msg[0: len(msg) - 3]
    return msg


def kk_message(speak, cmd):
    message = ''
    for j in range(len(speak['num'])):
        if speak['num'][j] > 0:
            message += str(speak['num'][j])
            message += (' hits' if speak['num'][j] > 1 else ' hit') + ' among the ' + obj_cat[cmd][j] + ', '
    message = message[0: len(message) - 2]
    return message


def choice_list(speak):
    message = ''
    n = 0
    cmd = 0 if speak.get('cmd') is not None else 1
    for i in range(len(speak['num'])):
        if speak['num'][i] > 0:
            for j in range(len(speak['keys'][i])):
                message += numbers[n] + ', <b>'
                item = speak['keys'][i][j]['name'] if cmd == 0 else speak['keys'][i][j]
                if (cmd == 1 and i == 3) or (cmd == 0 and i == 0):
                    item = upper_first(item)
                message += item + '</b>; '
                n += 1
            message += ' among the ' + obj_cat[cmd][i] + '. '
    message = message[0: len(message) - 2]
    return message


def homonyms(speak):
    msg = ''
    item = speak['item']
    for i in range(len(item)):
        num = 'say <b>' + numbers[i] + '</b> for <b>'
        name = item[i]['name']
        if speak.get('object') == 'authors':
            name = upper_first(name)
        msg += num + name + '</b>'
        if item[i].get('affiliation') is not None:
            msg += homonyms_list[0] + item[i]['affiliation'] + "; "
        elif item[i].get('country') is not None:
            msg += ' - ' + item[i]['country'] + "; "
        elif item[i].get('paper') is not None:
            msg += homonyms_list[1] + item[i]['paper'] + "; "
        elif item[i].get('publications') is not None:
            msg += homonyms_list[2] + str(item[i]['publications']) + homonyms_list[3] + "; "
        else:
            msg += "; "
        if i > 9:
            return msg
    return msg


def get_number(item):
    words = item.split(' ')
    for i in words:
        if i in numbers:
            return numbers.index(i) % 10
    return None


def get_choice(speak, num):
    for i in range(len(speak['num'])):
        n = num - speak['num'][i]
        if n < 0 or i == len(speak['num']) - 1:
            return speak['keys'][i][num]
        else:
            num = n


def list_item_question(subject):
    msg = ''
    sub = subject
    if list_legal_queries[sub]['topics'][1]:
        msg += item_question_object['topics']
    if list_legal_queries[sub]['conferences'][1]:
        msg += item_question_object['conferences']
    if list_legal_queries[sub]['organizations'][1]:
        msg += item_question_object['organizations']
    if list_legal_queries[sub]['authors'][1]:
        msg += item_question_object['authors']
    s = msg[len(msg) - 4: len(msg)]
    if s == ' or ':
        msg = msg[0: len(msg) - 3]
    return msg


def lst(result, order, sub):
    o = orders.index(order)
    msg = ''
    lst_ = result['lst']
    if o == 1 or o == 3:
        for i in lst_:
            author = ''
            if i.get('author') is not None and len(i['author']) > 0:
                author = ' by <b>' + upper_authors(i['author']) + '</b>'
            if i['citations'] == 1:
                i['citations'] = '1'
                ord_ = list_order[o]
            else:
                ord_ = order
            msg += '<b>' + (upper_first(i['name']) if sub == 'authors' else i['name'][0].upper() + i['name'][1:])
            msg += author + '</b> with <b>' + str(int(i['citations'])) + '</b> ' + ord_.split(' ')[0] + ', '
    else:
        for i in lst_:
            if i['papers'] == 1:
                i['papers'] = '1'
                ord_ = list_order[o]
            else:
                ord_ = order
            msg += '<b>' + (upper_first(i['name']) if sub == 'authors' else i['name'][0].upper() + i['name'][1:])
            msg += '</b> with <b>' + str(i['papers']) + '</b> ' + ord_.split(' ')[0] + ', '
    return msg[:-2] + '. '


def upper_authors(string):
    if ' et al.' in string:
        author = string.replace(' et al.', '')
        author = upper_first(author)
        return author + ' et al.'
    return upper_first(string)


def list_elements(lst1, element):
    blacklist = ['computer science', 'lecture notes in computer science', 'arxiv software engineering']
    lst_ = []
    if len(element) > 0:
        for i in lst1:
            if i[element] not in blacklist:
                lst_.append(i)
    else:
        for i in lst1:
            if i not in blacklist:
                lst_.append(i)

    i = len(lst_)
    if i > 3:
        i = 3
    msg = ''
    j = 0
    while j < i:
        if len(element) > 0:
            msg += '<b>"' + upper_first(lst_[j][element]) + '"</b>, '
        else:
            msg += '<b>"' + upper_first(lst_[j]) + '"</b>, '
        j += 1
    return msg[:-2] + '. '


def upper_first(str_):
    s = str_.split(' ')
    result = ''
    for i in range(len(s)):
        result += ' ' + s[i][0].upper() + s[i][1:]
    return result[1:]


def dsc(query):
    msg = ''
    item = query['item']
    if query['obj_id'] == 1:
        msg += '<b>' + upper_first(item['name']) + '</b>' + dsc_list[0]
        if item['last_affiliation'].get('affiliation_name') is not None:
            s = item['last_affiliation']['affiliation_name'].split(' ')
            msg += (dsc_list[1] if (s[0] == 'the' or s[0] == 'The') else dsc_list[2])
            msg += '<b>' + item['last_affiliation']['affiliation_name'] + '</b>'
            if item['last_affiliation'].get('affiliation_country') is not None:
                msg += ', ' + item['last_affiliation']['affiliation_country'] + '. '
        else:
            msg += '. '
        msg += dsc_list[3]
        if item.get('publications') is not None:
            msg += dsc_list[4] + '<b>' + str(item['publications']) + '</b>' + '. '
        if item.get('citations') is not None:
            msg += dsc_list[5] + '<b>' + str(item['citations']) + '</b>' + '. '
        if item.get('h-index') is not None:
            msg += 'h-index: ' + '<b>' + str(item['h-index']) + '</b>' + '. '
        if item.get('h5-index') is not None:
            msg += 'h5-index: ' + '<b>' + str(item['h5-index']) + '</b>' + '. '
        if item.get('co_authors') is not None and item['co_authors'] > 0:
            msg += dsc_list[6] + '<b>' + str(item['co_authors']) + '</b>' + '. '
        if item.get('top_pub_topics') is not None and len(item['top_pub_topics']) > 0:
            msg += dsc_list[7] if len(item['top_pub_topics']) == 1 else dsc_list[8]
            msg += list_elements(item['top_pub_topics'], 'topic')
        if item.get('top_pub_conf') is not None and len(item['top_pub_conf']) > 0:
            msg += dsc_list[9] if len(item['top_pub_conf']) == 1 else dsc_list[10]
            msg += list_elements(item['top_pub_conf'], 'name')
        if item.get('top_journals') is not None and len(item['top_journals']) > 0:
            msg += dsc_list[11] if len(item['top_journals']) == 1 else dsc_list[12]
            msg += list_elements(item['top_journals'], 'name')
    elif query['obj_id'] == 2 or query['obj_id'] == 3:
        msg += '<b>' + item['acronym'] + '</b>' + dsc_list[13] + '<b>' + item['name'] + '</b>' + dsc_list[14]
        msg += list_elements(item['topics'], '')
        msg += dsc_list[15]
        if item.get('h5_index') is not None:
            msg += 'h5-index: ' + '<b>' + str(item['h5_index']) + '</b>. '
        if item.get('citationcount_5') is not None:
            msg += dsc_list[16] + '<b>' + str(item['citationcount_5']) + '</b>. '
        if item.get('activity_years') is not None:
            msg += dsc_list[17] + '<b>' + str(item['activity_years']['from']) + '</b>'
            msg += dsc_list[18] + '<b>' + str(item['activity_years']['to']) + '</b>. '
        if item.get('last_year_publications') is not None and item['last_year_publications'] > 0:
            msg += dsc_list[19] + '<b>' + str(item['last_year_publications']) + '</b>. '
        if len(item['top_3_country']) > 0:
            msg += dsc_list[20] if len(item['top_3_country']) == 1 else dsc_list[21]
            msg += list_elements(item['top_3_country'], '')
        if len(item['top_3_edu']) > 0:
            msg += dsc_list[22] if len(item['top_3_edu']) == 1 else dsc_list[23]
            msg += list_elements(item['top_3_edu'], '')
        if len(item['top_3_company']) > 0:
            msg += dsc_list[24] if len(item['top_3_company']) == 1 else dsc_list[25]
            msg += list_elements(item['top_3_company'], '')
    elif query['obj_id'] == 4:
        msg += '<b>' + item['name'] + '</b>'
        msg += ((' -<b> ' + item['country'] + ' </b>-') if item.get('country') is not None else '')
        msg += ' is an organization'
        if item.get('type') is not None and (item['type'] == 'academia' or item['type'] == 'industry'):
            msg += ' in <b>' + ('Edu' if item['type'] == 'academia' else 'Industry') + '</b> sector. '
        else:
            msg += '. '

        msg += dsc_list[15]
        if item.get('h5-index') is not None:
            msg += 'h5-index: <b>' + str(item['h5-index']) + '</b>. '
        if item.get('publications_5') is not None:
            msg += dsc_list[26] + '<b>' + str(item['publications_5']) + '</b>. '
        if item.get('citations_5') is not None:
            msg += dsc_list[16] + '<b>' + str(item['citations_5']) + '</b>. '
        if item.get('authors_number') is not None:
            msg += dsc_list[27] + '<b>' + str(item['authors_number']) + '</b>. '
        if item.get('top_3_topics') is not None and len(item['top_3_topics']) > 0:
            msg += dsc_list[7] if len(item['top_3_topics']) == 1 else dsc_list[8]
            msg += list_elements(item['top_3_topics'], '')
        if item.get('top_3_conferences') is not None and len(item['top_3_conferences']) > 0:
            msg += dsc_list[9] if len(item['top_3_conferences']) == 1 else dsc_list[10]
            msg += list_elements(item['top_3_conferences'], '')
        if item.get('top_3_journals') is not None and len(item['top_3_journals']) > 0:
            msg += dsc_list[11] if len(item['top_3_journals']) == 1 else dsc_list[12]
            msg += list_elements(item['top_3_journals'], '')
        else:
            msg += 'Sorry, Query not yet implemented!'
            return msg
    msg += 'You can ask to perform another query on the data contained in the AIDA database or ask for Help. '
    return msg + 'What would you like to try?'


def session_reset():
    global session
    answer = session['answer']
    session = {'level': 0, 'intent': {'name': '', 'level': 0, 'slots': {}}, 'confirmation': True, 'answer': answer}


def intent_verify(msg):
    global session
    intent = getIntent(msg)
    msg = msg.replace(intent[1], intent[0])
    intent = intent[0]
    if intent == 'hello':
        setMessage('HELLO_MSG')
    elif intent == 'reset':
        setMessage('REPROMPT_MSG')
        session_reset()
    elif intent == 'help':
        setMessage('HELP_MSG')
    elif intent == 'cancel':
        setMessage('GOODBYE_MSG')
        session_reset()
    elif intent == 'count' or intent == 'list':
        session['level'] = 1
        setIntentSlots(get_data('cmd=parser&ins=', str(msg)))

    elif intent == 'describe':
        session['intent']['name'] = 'describe'
        session['level'] = 1
        query = getUserDescribeQueryText(msg)
        if len(query) > 0:
            session['intent']['slots']['ins'] = query
        describe_query('')
        return
    elif intent == 'fallback':
        setMessage('FALLBACK_MSG')
    return


# set intent name and slots with the results from the parser
def setIntentSlots(data):
    cmd = ''
    global session

    if data.get('cmd') is not None:
        cmd = data['cmd']['value']

    if cmd == 'count':
        session['intent']['name'] = 'count'
        if data.get('sub') is not None:
            session['intent']['slots']['sub'] = data['sub']['value']
        if data.get('ins') is not None:
            session['intent']['slots']['ins'] = data['ins']['value']
        if data.get('obj') is not None:
            session['intent']['slots']['obj'] = data['obj']['value']
        elif data.get('sub') is not None and data.get('ins') is not None and data['ins']['value'] == 'all':
            session['intent']['slots']['obj'] = combinations[data['sub']['value']]
        count_query('')

    if cmd == 'list':
        session['intent']['name'] = 'list'
        if data.get('num') is not None:
            session['intent']['slots']['num'] = data['num']['value']
        if data.get('sub') is not None:
            session['intent']['slots']['sub'] = data['sub']['value']
        if data.get('ins') is not None:
            session['intent']['slots']['ins'] = data['ins']['value']
        if data.get('obj') is not None:
            session['intent']['slots']['obj'] = data['obj']['value']
        elif data.get('sub') is not None and data.get('ins') is not None and data['ins']['value'] == 'all':
            session['intent']['slots']['obj'] = 'all'
        if data.get('order') is not None:
            session['intent']['slots']['order'] = data['order']['value']
        list_query('')


def is_list_legal(sub, obj, order=None):
    if sub is None or obj is None:
        return False
    if order is not None:
        return list_legal_queries[sub][obj][orders.index(order.split(' ')[0])]
    return list_legal_queries[sub][obj][0] or list_legal_queries[sub][obj][1]


def count_query(msg):
    global session
    slots = session['intent']['slots']
    sub = slots.get('sub')
    obj = slots.get('obj')
    ins = slots.get('ins')
    idx = slots.get('id')
    sub_id = (subject_categories.index(sub) + 1) if sub in subject_categories else 0
    obj_id = (object_categories.index(obj) + 1) if obj in object_categories else 0

    # no level - verifying slots
    if session['intent'].get('level') == 0:

        if msg in cancel_words:
            setMessage('REPROMPT_MSG')
            session_reset()
            return

        if sub is None and len(msg) == 0:
            session['confirmation'] = False
            setMessage('SUBJECT_REQUEST_MSG')
            return

        if sub is None and len(msg) > 0:
            if msg in subject_categories:
                sub_id = subject_categories.index(msg) + 1
                session['intent']['slots']['sub'] = msg
                sub = msg
                msg = ''

            else:
                setMessage('SUBJECT_WRONG_MSG', {'sub': msg})
                return

        if sub is not None and sub not in subject_categories:
            setMessage('SUBJECT_WRONG_MSG', {'sub': sub})
            del session['intent']['slots']['sub']
            return

        if ins is not None and ins != 'all':
            session['intent']['level'] = 1
            data = get_data('cmd=fnd&ins=', ins)
            count_query(data)
            return

        if ins is None and len(msg) == 0:
            session['confirmation'] = False
            message = 'INSTANCE_MSG'
            if sub_id == 5:
                message = 'INSTANCE2_MSG'
            setMessage(message, {'list': item_question(sub), 'sub': sub})
            return

        if ins is None and len(msg) > 0 and msg != 'all':
            session['intent']['slots']['ins'] = msg
            data = get_data('cmd=fnd&ins=', msg)
            session['intent']['level'] = 1
            count_query(data)
            return

        if (sub is not None and ins is not None and ins == 'all') or (sub is not None and ins is None and msg == 'all'):
            if not count_legal_queries[sub][combinations[sub]][1]:
                setMessage('NO_SENSE_MSG')
                session_reset()
                return
            obj = combinations[sub]
            session['intent']['slots']['obj'] = obj
            session['intent']['slots']['ins'] = 'no'
            session['intent']['level'] = 2
            if session['confirmation']:
                setMessage('INTENT_CONFIRMATION_1_MSG',
                           {'sub': count_dict['sub'][sub][obj],
                            'prep': count_dict['prep'][sub][obj],
                            'obj': count_dict['obj'][sub][obj]})
                return
            else:
                count_query('')
        return

    # verifying ins
    if session['intent']['level'] == 1:
        # case ok
        if msg['result'] == 'ok':
            ins = msg['item']
            session['intent']['slots']['ins'] = ins
            obj_id = msg['obj_id']
            obj = msg['object']
            session['intent']['slots']['obj'] = obj

            if obj_id == 2 or obj_id == 4:
                session['intent']['slots']['id'] = msg['id']

            if not count_legal_queries[sub][obj][0]:
                setMessage('NO_SENSE_MSG', {})
                session_reset()
                return

            if obj_id == 4:
                ins = upper_first(ins)

            session['intent']['level'] = 2

            if session['confirmation']:
                setMessage('INTENT_CONFIRMATION_2_MSG',
                           {'sub': count_dict['sub'][sub][obj],
                            'prep': count_dict['prep'][sub][obj],
                            'obj': count_dict['obj'][sub][obj],
                            'ins': ins})
                return
            else:
                count_query('')
            return

        # case kk (too many results fnd search)
        if msg['result'] == 'kk':
            message = kk_message(msg, 1)
            setMessage('TOO_GENERIC_MSG', {'ins': ins, 'results': message})
            session['intent']['level'] = 0
            del session['intent']['slots']['ins']
            return

        # case ko (no result fnd search)
        if msg['result'] == 'ko':
            setMessage('NO_RESULT_MSG', {'ins': ins})
            session['intent']['level'] = 0
            del session['intent']['slots']['ins']
            return

        # case k2 (multiple results fnd search)
        if msg['result'] == 'k2':

            num_res = 0
            for i in range(len(msg['num'])):
                obj = object_categories[i]
                if not count_legal_queries[sub][obj][0]:
                    msg['num'][i] = 0
                    msg['keys'][i] = []
                num_res += msg['num'][i]
            if num_res == 0:
                setMessage('NO_SENSE_MSG')
                session_reset()
                return
            elif num_res == 1:
                for i in range(len(msg['num'])):
                    if msg['num'][i] == 1:
                        session['intent']['slots']['ins'] = msg['keys'][i][0]
                        session['intent']['level'] = 0
                        count_query('')
                        return

            session['intent']['items_list'] = msg
            message = choice_list(msg)
            setMessage('ITEM_MSG', {'ins': ins, 'msg': message})
            session['intent']['level'] = 3
            return

        # case ka(homonyms fnd search)
        if msg['result'] == 'ka':
            obj = msg['object']
            if not count_legal_queries[sub][obj][0]:
                setMessage('NO_SENSE_MSG')
                session_reset()
                return

            session['intent']['homonyms_list'] = msg
            message = homonyms(msg)
            setMessage('HOMONYMS_MSG', {'msg': message, 'obj': homonyms_objects[msg['obj_id'] - 1]})
            session['intent']['level'] = 4
            return

    # check, confirm and display of results
    if session['intent']['level'] == 2:
        if msg in cancel_words:
            setMessage('REPROMPT_MSG', {})
            session_reset()
            return

        inst = ins
        if idx is not None:
            inst = idx

        data = get_data('cmd=how&sub=' + str(sub_id) + '&obj=' + str(obj_id) + '&ins=', inst)

        if data['result'] != 'ok':
            setMessage('NO_QUERY_MSG', {})
            session_reset()
            return

        if obj_id == 4:
            ins = upper_first(ins)

        message = 'QUERY_1_MSG'
        if ins == 'no':
            message = 'QUERY_2_MSG'
            setMessage(message, {'num': data['hits'], 'sub': count_dict['sub'][sub][obj],
                                 'obj': count_dict['obj'][sub][obj], 'prep': count_dict['prep'][sub][obj]})
        else:
            msg_sub = count_dict['sub'][sub][obj][0: len(sub) - 1] if data['hits'] == '1' else count_dict['sub'][sub][
                obj]
            setMessage(message, {'num': data['hits'], 'sub': msg_sub, 'obj': count_dict['obj'][sub][obj],
                                 'prep': count_dict['prep'][sub][obj], 'ins': ins})

        session_reset()
        return

    # multiple result list management
    if session['intent']['level'] == 3:
        if msg in cancel_words:
            setMessage('REPROMPT_MSG', {})
            session_reset()
            return

        num = get_number(msg)
        if num is not None and num <= sum(session['intent']['items_list']['num']):
            ins = get_choice(session['intent']['items_list'], num)
            session['intent']['slots']['ins'] = ins
            session['intent']['level'] = 0
            del session['intent']['items_list']
            count_query('')
            return
        else:
            session['intent']['level'] = 1
            msg = session['intent']['items_list']
            del session['intent']['items_list']
            count_query(msg)

    # homonyms list management
    if session['intent']['level'] == 4:
        if msg in cancel_words:
            setMessage('REPROMPT_MSG', {})
            session_reset()
            return

        num = get_number(msg)
        if num is not None and num <= (len(session['intent']['homonyms_list']['item']) - 1):
            if session['intent']['homonyms_list']['obj_id'] == 2:
                # noinspection PyTypeChecker
                ins = session['intent']['homonyms_list']['item'][num]['acronym']
            else:
                # noinspection PyTypeChecker
                ins = session['intent']['homonyms_list']['item'][num]['name']
            msg = copy.deepcopy(session['intent']['homonyms_list'])
            msg["result"] = "ok"
            # noinspection PyTypeChecker
            msg["id"] = session['intent']['homonyms_list']['item'][num]['id']
            msg["item"] = ins
        else:
            msg = session['intent']['homonyms_list']

        del session['intent']['homonyms_list']
        session['intent']['level'] = 1
        count_query(msg)
        return


def list_query(msg):
    slots = session['intent']['slots']
    sub = slots.get('sub')
    obj = slots.get('obj')
    ins = slots.get('ins')
    idx = slots.get('id')
    num = slots.get('num')
    order = slots.get('order')

    sub_id = (list_subject_categories.index(sub) + 1) if sub in list_subject_categories else 0
    obj_id = (object_categories.index(obj) + 1) if obj in object_categories else 0
    order_id = (orders.index(order) + 1) if order in orders else 0

    # level == 0 - verifying slots
    if session['intent'].get('level') == 0:

        if msg in cancel_words:
            setMessage('REPROMPT_MSG', {})
            session_reset()
            return

        if num is not None and (int(num) > 10 or int(num) < 2):
            if len(msg) == 0:
                session['confirmation'] = False
                msg_options = {'num': str(num) + (' is too big' if num > 10 else ' is too small')}
                setMessage('LIST_WRONG_NUMBER_MSG', msg_options)
                return
            elif 1 < int(msg) < 11:
                session['intent']['slots']['num'] = int(msg)
                num = session['intent']['slots']['num']
                msg = ''
            else:
                num = int(msg)
                msg_options = {'num': str(num) + (' is too big' if num > 10 else ' is too small')}
                setMessage('LIST_WRONG_NUMBER_MSG', msg_options)
                return

        if sub is None and len(msg) == 0:
            session['confirmation'] = False
            setMessage('LIST_SUBJECT_REQUEST_MSG', {})
            return

        if sub is None and len(msg) > 0:
            if msg in list_subject_categories:
                sub = msg
                session['intent']['slots']['sub'] = msg
                msg = ''
                sub_id = list_subject_categories.index(sub) + 1
            else:
                setMessage('LIST_SUBJECT_WRONG_MSG', {'sub': msg})
                return

        if sub is not None and sub not in list_subject_categories:
            session['confirmation'] = False
            setMessage('LIST_SUBJECT_WRONG_MSG', {'sub': sub})
            if session['intent']['slots'].get('sub') is not None:
                del session['intent']['slots']['sub']
            return

        if ins is not None and ins != 'all':
            session['intent']['level'] = 1
            data = get_data('cmd=fnd&ins=', ins)
            list_query(data)
            return

        if (ins is not None and ins == 'all') or (ins is None and msg == 'all'):
            session['intent']['level'] = 2
            session['intent']['slots']['obj'] = 'all'
            session['intent']['slots']['ins'] = 'all'
            list_query('')
            return

        if ins is None and len(msg) == 0:
            session['confirmation'] = False
            message = 'LIST_INSTANCE_MSG'
            setMessage(message, {'list': list_item_question(sub), 'sub': sub, 'num': num})
            return

        if ins is None and len(msg) > 0 and msg != 'all':
            session['intent']['slots']['ins'] = msg
            data = get_data('cmd=fnd&ins=', msg)
            session['intent']['level'] = 1
            list_query(data)
            return

    # verifica ins != 'all'
    if session['intent']['level'] == 1:
        assert isinstance(msg, dict)

        # ok case
        if msg['result'] == 'ok':
            # ins = msg['item']
            session['intent']['slots']['ins'] = msg['item']
            obj_id = msg['obj_id']
            obj = msg['object']
            session['intent']['slots']['obj'] = msg['object']

            if obj_id == 2 or obj_id == 4:
                session['intent']['slots']['id'] = msg['id']

            if sub is not None and obj is not None and not is_list_legal(sub, obj):
                setMessage('NO_SENSE_MSG')
                session_reset()
                return

            session['intent']['level'] = 2
            list_query('')
            return

        # kk case
        if msg['result'] == 'kk':
            message = kk_message(msg, 1)
            setMessage('TOO_GENERIC_MSG', {'ins': ins, 'results': message})
            if session['intent'].get('level') is not None:
                session['intent']['level'] = 0
            if session['intent']['slots'].get('ins') is not None:
                del session['intent']['slots']['ins']
            return

        # ko case
        if msg['result'] == 'ko':
            setMessage('NO_RESULT_MSG', {'ins': ins})
            if session['intent'].get('level') is not None:
                session['intent']['level'] = 0
            if session['intent']['slots'].get('ins') is not None:
                del session['intent']['slots']['ins']
            return

        # k2 case
        if msg['result'] == 'k2':

            num_res = 0
            for i in range(len(msg['num'])):
                obj = object_categories[i]
                if not count_legal_queries[sub][obj][0]:
                    msg['num'][i] = 0
                    msg['keys'][i] = []
                num_res += msg['num'][i]
            if num_res == 0:
                setMessage('NO_SENSE_MSG')
                session_reset()
                return
            elif num_res == 1:
                for i in range(len(msg['num'])):
                    if msg['num'][i] == 1:
                        session['intent']['slots']['ins'] = msg['keys'][i][0]
                        session['intent']['level'] = 0
                        count_query('')
                        return

            session['intent']['items_list'] = msg
            message = choice_list(msg)
            setMessage('ITEM_MSG', {'ins': ins, 'msg': message})
            session['intent']['level'] = 3
            return

        # ka case homonyms
        if msg['result'] == 'ka':
            session['intent']['homonyms_list'] = msg
            message = homonyms(msg)
            setMessage('HOMONYMS_MSG', {'msg': message, 'obj': homonyms_objects[msg['obj_id'] - 1]})
            session['intent']['level'] = 4
            return

    # slots verify part II
    if session['intent']['level'] == 2:

        if msg in cancel_words:
            setMessage('REPROMPT_MSG', {})
            session_reset()
            return

        if order is None and len(msg) == 0:
            session['confirmation'] = False
            message = 'LIST_ORDER_MSG'
            if sub is not None and list_subject_categories.index(sub) == 1:
                message = 'LIST_PAPERS_ORDER_MSG'
            setMessage(message, {'num': num, 'sub': sub})
            return

        if order is None and len(msg) > 0:
            n = get_number(msg)
            if n is not None:
                if sub is not None and list_subject_categories.index(sub) == 1:
                    if -1 < n < 2:
                        msg = orders[n * 2 + 1]
                else:
                    if -1 < n < 4:
                        msg = orders[n]

            if msg in orders:
                order = msg
                session['intent']['slots']['order'] = msg
                msg = ''
                order_id = orders.index(order) + 1
            else:
                message = 'LIST_ORDER_WRONG_MSG'
                if sub is not None and list_subject_categories.index(sub) == 1:
                    message = 'LIST_PAPERS_ORDER_WRONG_MSG'
                setMessage(message, {'sub': sub, 'order': msg})
                return

        if ins is not None and ins == 'all':
            if not is_list_legal(sub, obj, order):
                setMessage('NO_SENSE_MSG')
                session_reset()
                return

            session['intent']['level'] = 5

            if session['confirmation']:
                setMessage('LIST_INTENT_CONFIRMATION_1_MSG',
                           {'order': order, 'num': num, 'sub': (list_dict[order.split(' ')[0]]['sub'][sub][sub]),
                            'prep': list_dict[order.split(' ')[0]]['prep'][sub][sub],
                            'obj': list_dict[order.split(' ')[0]]['obj'][sub][sub]})
                return
            else:
                list_query('')
                return

        if ins is not None and ins != 'all':
            if not list_legal_queries[sub][obj][orders.index(order.split(' ')[0])]:
                setMessage('NO_SENSE_MSG')
                session_reset()
                return

            msg_ins = ins
            if obj_id == 4:
                msg_ins = upper_first(ins)

            session['intent']['level'] = 5

            if session['confirmation']:
                options = {'ins': msg_ins, 'order': order, 'num': num,
                           'sub': (list_dict[order.split(' ')[0]]['sub'][sub][obj]),
                           'prep': list_dict[order.split(' ')[0]]['prep'][sub][obj],
                           'obj': list_dict[order.split(' ')[0]]['obj'][sub][obj]}

                setMessage('LIST_INTENT_CONFIRMATION_2_MSG', options)
                return
            else:
                list_query('')
                return

    # multiple result list management
    if session['intent']['level'] == 3:
        if msg in cancel_words:
            setMessage('REPROMPT_MSG')
            session_reset()
            return

        choice = get_number(msg)
        if choice is not None and choice <= sum(session['intent']['items_list']['num']):
            ins = get_choice(session['intent']['items_list'], choice)
            session['intent']['slots']['ins'] = ins
            session['intent']['level'] = 0
            del session['intent']['items_list']
            list_query('')
            return
        else:
            session['intent']['level'] = 1
            msg = session['intent']['items_list']
            del session['intent']['items_list']
            list_query(msg)

    # homonyms list management
    if session['intent']['level'] == 4:
        if msg in cancel_words:
            setMessage('REPROMPT_MSG', {})
            session_reset()
            return

        choice = get_number(msg)
        if choice is not None and choice <= (len(session['intent']['homonyms_list']['item']) - 1):
            if session['intent']['homonyms_list']['obj_id'] == 2:
                # noinspection PyTypeChecker
                ins = session['intent']['homonyms_list']['item'][num]['acronym']
            else:
                # noinspection PyTypeChecker
                ins = session['intent']['homonyms_list']['item'][num]['name']
            msg = copy.deepcopy(session['intent']['homonyms_list'])
            msg["result"] = "ok"
            # noinspection PyTypeChecker
            msg["id"] = session['intent']['homonyms_list']['item'][num]['id']
            msg["item"] = ins
        else:
            msg = session['intent']['homonyms_list']

        del session['intent']['homonyms_list']
        session['intent']['level'] = 1
        list_query(msg)
        return

    # check, confirm and display of results
    if session['intent']['level'] == 5:
        if msg in cancel_words:
            setMessage('REPROMPT_MSG')
            session_reset()
            return

        inst = ins
        if idx is not None:
            inst = idx

        call = 'cmd=lst&sub=' + str(sub_id) + '&obj=' + str(obj_id) + '&ord='
        call += str(order_id) + '&num=' + str(num) + '&ins='
        data = get_data(call, inst)

        if obj == 'all':
            obj = sub
            ins = ''

        msg_ins = ins
        if obj_id == 4:
            msg_ins = upper_first(ins)

        ord_ = order.split(' ')[0]
        sub1 = list_dict[ord_]['sub'][sub][obj]
        obj1 = list_dict[ord_]['obj'][sub][obj]
        prep = list_dict[ord_]['prep'][sub][obj]

        if data['result'] == 'ok' and len(data['lst']) > 0:

            msg_num = '' if len(data['lst']) == 1 else num
            msg_sub = sub1[0: len(sub) - 1] if len(data['lst']) == 1 else sub1
            # noinspection PyTypeChecker
            options = {'order': order, 'num': msg_num, 'sub': msg_sub, 'obj': obj1, 'prep': prep, 'ins': msg_ins,
                       'verb': (list_verbs[0] if len(data['lst']) == 1 else list_verbs[1]),
                       'lst': lst(data, order, sub)}
            setMessage('LIST_QUERY_MSG', options)

        elif len(data['lst']) == 0:
            setMessage('LIST_NO_RESULT_MSG', {'sub': sub1, 'obj': obj1, 'ins': ins, 'prep': prep})

        else:
            setMessage('NO_QUERY_MSG')

        session_reset()
        return

    return


def describe_query(msg):
    slots = session['intent']['slots']
    ins = slots.get('ins')

    # level 0 slots verify
    if session['intent']['level'] == 0:

        if msg in cancel_words:
            setMessage('REPROMPT_MSG')
            session_reset()
            return

        if ins is None and len(msg) == 0:
            session['confirmation'] = False
            setMessage('DESCRIBE_INSTANCE_MSG')
            return

        if (ins is not None) or (ins is None and len(msg) > 0):
            if ins is None:
                session['intent']['slots']['ins'] = session['original_input']  # previously msg
            data = get_data('cmd=dsc&ins=', session['intent']['slots']['ins'])
            session['intent']['level'] = 1
            describe_query(data)
            return

    # ins verify
    if session['intent']['level'] == 1:

        # ok case
        if msg['result'] == 'ok':
            message_ins = ''
            session['intent']['slots']['results'] = msg
            session['intent']['level'] = 2

            if msg['obj_id'] == 1:
                message_ins += upper_first(msg['item']['name'])
            elif msg['obj_id'] == 4:
                message_ins += msg['item']['name']
            elif 1 < msg['obj_id'] < 4 and 'conference' in msg['item']['name'].lower():
                message_ins += msg['item']['name']
            else:
                message_ins += msg['item']['name'] + ' conference'

            if session['confirmation']:
                setMessage("DESCRIBE_CONFIRM_MSG", {'ins': message_ins})
                return
            else:
                describe_query('')
                return

        # kk case - too many results
        if msg['result'] == 'kk':
            session['confirmation'] = False
            message = kk_message(msg, 0)
            setMessage('DSC_TOO_GENERIC_MSG', {'ins': ins, 'results': message})
            session['intent']['level'] = 0
            del session['intent']['slots']['ins']
            return

        # ko case - no result
        if msg['result'] == 'ko':
            setMessage('DSC_NO_RESULT_MSG', {'ins': ins})
            session['intent']['level'] = 0
            del session['intent']['slots']['ins']
            return

        # k2 case multiple results
        if msg['result'] == 'k2':
            session['confirmation'] = False
            msg['cmd'] = 'dsc'
            session['intent']['items_list'] = msg
            message = choice_list(msg)
            setMessage('ITEM_MSG', {'ins': ins, 'msg': message})
            session['intent']['level'] = 3
            return

        # ka case homonyms
        if msg['result'] == 'ka':
            session['confirmation'] = False
            session['intent']['homonyms_list'] = msg
            message = homonyms(msg)
            setMessage('HOMONYMS_MSG', {'msg': message})
            session['intent']['level'] = 4
            return

    # check, confirm and display of results
    if session['intent']['level'] == 2:

        if msg in cancel_words:
            setMessage('REPROMPT_MSG')
            session_reset()
            return

        if session['intent']['slots'].get('results') is not None:
            message = dsc(session['intent']['slots']['results'])
            appendMessage(message)
            session_reset()
            return

        else:
            setMessage('NO_QUERY_MSG')
            session_reset()
            return

    # multiple result list management
    if session['intent']['level'] == 3:

        if msg in cancel_words:
            setMessage('REPROMPT_MSG')
            session_reset()
            return

        num = get_number(msg)
        if num is not None and num <= sum(session['intent']['items_list']['num']):
            ins = get_choice(session['intent']['items_list'], num)
            session['intent']['slots']['ins'] = ins['name']
            session['intent']['level'] = 0
            del session['intent']['items_list']
            describe_query('')
            return

        else:
            session['intent']['level'] = 1
            msg = session['intent']['items_list']
            del session['intent']['items_list']
            describe_query(msg)

    # homonyms list management
    if session['intent']['level'] == 4:

        if msg in cancel_words:
            setMessage('REPROMPT_MSG')
            session_reset()
            return

        num = get_number(msg)
        if num is not None and num <= len(session['intent']['homonyms_list']['item']) - 1:
            # noinspection PyTypeChecker
            idx = session['intent']['homonyms_list']['item'][num]['id']
            print(idx)
            if session['intent']['homonyms_list']['obj_id'] == 4:
                idx = '0000000000' + str(idx)
            del session['intent']['homonyms_list']
            data = get_data('cmd=dsc&ins=', idx)
            session['intent']['level'] = 1
            describe_query(data)
            return
        else:
            msg = session['intent']['homonyms_list']
            del session['intent']['homonyms_list']
            session['intent']['level'] = 1
            describe_query(msg)
            return


def cycle(user_input):
    if len(user_input) == 0:
        return
    msg = user_input
    for i in range(len(marks_list)):
        msg = msg.replace(marks_list[i], '')
    session['original_input'] = msg
    msg = msg.lower()
    # verification of intent
    if session['level'] == 0:
        intent_verify(msg)
        return
    # transfers control to complex intents depending on the intent name
    if session['level'] == 1:
        intent = getIntent(msg)[0]
        # print 'transfers control to complex intents depending on the intent name: ', intent, msg
        if intent != 'fallback':
            session['level'] = 0
            session['confirmation'] = True
            if session['intent'].get('level') is not None:
                session['intent']['level'] = 0
            if session['intent'].get('homonyms_list') is not None:
                del session['intent']['homonyms_list']
            if session['intent'].get('items_list') is not None:
                del session['intent']['items_list']
            intent_verify(msg)
            return
        if session['intent']['name'] == 'count':
            count_query(msg)
            return
        elif session['intent']['name'] == 'list':
            list_query(msg)
            return
        elif session['intent']['name'] == 'describe':
            describe_query(msg)
            return


def main():
    user_input = ''
    while user_input != 'bye':
        user_input = input('User... ')
        cycle(user_input)
        answer = session['answer']
        for i in range(len(tags_list)):
            answer = answer.replace(tags_list[i], '')
        print('AIDA-Bot... ' + answer)


if __name__ == '__main__':
    main()
