import copy
import json
import random
import urllib
import urllib.parse
import urllib.request


class AidaBot:
    def __init__(self, url='http://aidabot.ddns.net/api?pass=123abc&'):
        self.data_server_url = url

        self.intents = {
            'cancel': ['bye', 'goodbye'],
            'help': ['help'],
            'count': ['count', 'how many'],
            'list': ['list'],
            'describe': ['describe'],  # 'who is', 'who are', 'what about', 'what is', 'what are', 'what', 'who'],
            'hello': ['hello', 'hi'],
            'reset': ['cancel', 'stop'],
            'compare': ['compare', 'equate', 'match', 'relate']
        }

        self.combinations = {
            'authors': 'papers',
            'papers': 'papers',
            'conferences': 'conferences',
            'organizations': 'organizations',
            'citations': 'papers'
        }

        self.subject_categories = ['authors', 'papers', 'conferences', 'organizations', 'citations']
        self.object_categories = ['topics', 'conferences', 'organizations', 'authors', 'papers']
        self.list_subject_categories = ['authors', 'papers', 'conferences', 'organizations', 'topics']
        self.compare_categories = ['author', 'conference', 'conference', 'organization']
        self.tags_list = ['<b>', '</b>', '<i>', '</i>', '<br/>']
        self.marks_list = ['.', '?', ';', ',']
        self.orders = ['publications', 'citations', 'publications in the last 5 years', 'citations in the last 5 years']
        self.homonyms_objects = ['topic', 'conference', 'organization', 'author', 'paper']
        self.homonyms_list = [' affiliated with ', ' author of the paper: ', ', author with ', ' publications']
        self.list_verbs = ['is', 'are']
        self.list_order = ['publication', 'citation', 'publication in the last 5 years', 'citation in the last 5 years']
        self.cancel_words = ['cancel', 'stop', 'enough', 'no', 'nothing']

        self.templates = {
            'WELCOME_MSG': [
                '<b>Hello!</b> You can ask me to <b>describe</b>, <b>compare</b>, <b>list</b>, or <b>count</b> any '
                'scholarly entity.',
                'Welcome, you can ask me to <b>describe</b>, <b>compare</b>, <b>list</b>, or <b>count</b> any '
                'scholarly entity. What would you like to try?'],
            'HELLO_MSG': ['Hello! What can I do for you?', 'Hi! what could i do for you?'],
            'HELP_MSG': [
                'You can ask to <b>count</b> or <b>list</b> <i>authors</i>, <i>papers</i>, <i>conferences</i>, '
                '<i>organizations</i>, <i>topics</i> and <i>citations</i> or to <b>describe</b> or <b>compare</b> '
                '<i>authors</i>, <i>conferences</i> or <i>organizations</i>. Start a query with <b>list</b>, '
                '<b>count</b>, <b>describe</b> or <b>compare</b>.', 'You can ask a query starting with <b>count</b>, '
                                                                    '<b>list</b>, or <b>describe</b>.'],
            'GOODBYE_MSG': ['Goodbye!', 'Bye!', 'See you later!'],

            'FALLBACK_MSG': 'Sorry, I don\'t know that. Please try again.',
            'ERROR_MSG': 'Sorry, there was an error. Please try again.',

            'HOMONYMS_MSG': 'I found different homonyms (list sorted by number of publications): ${msg} ',

            'SUBJECT_REQUEST_MSG': 'I can count <b>papers</b>, <b>authors</b>, <b>conferences</b>, '
                                   '<b>organizations</b> and <b>citations</b>. What do you want me to count?',
            'SUBJECT_WRONG_MSG': "Sorry, I can\'t count <b>${sub}</b>. I can count <b>papers</b>, <b>authors</b>, "
                                 "<b>conferences</b>, <b>organizations</b> and <b>citations</b>. What do you prefer?",
            'SUBJECT_REQUEST_REPROMPT_MSG': 'I can count <b>papers</b>, <b>authors</b>, <b>conferences</b>, '
                                            '<b>organizations</b> and <b>citations</b>. What do you prefer?',
            'INSTANCE_MSG': "what is the <b>name</b> of the ${list} whose <b>${sub}</b> I should count? You can say "
                            "<b>all</b> for the full list",
            'INSTANCE2_MSG': "what is the <b>name</b> of the ${list} whose <b>${sub}</b> I should count?",
            'ITEM_MSG': "Searching for <b>${ins}</b>, I got: ${msg}. To choose, say the number. Which one is correct?",
            'INTENT_CONFIRMATION_1_MSG': "Do you want to know how many <b>${sub}</b> ${prep} ${obj} are in the AIDA "
                                         "database?",
            'INTENT_CONFIRMATION_2_MSG': "Do you want to know how many <b>${sub}</b> ${prep} <b>${ins}</b> ${obj} are "
                                         "in the AIDA database?",
            'TOO_GENERIC_MSG': "Your search for <b>${ins}</b> got ${results}. You need to try again and to be more "
                               "specific. Could you tell me the exact name?",
            'NO_RESULT_MSG': "Your search for ${ins} got no result. You need to try again. What could I search for"
                             "you?",
            'QUERY_1_MSG': "I found <b>${num}</b> ${sub} ${prep} <b>${ins}</b> ${obj}. You can ask to perform another "
                           "query on the data contained in the AIDA database or ask for Help. What would you like to "
                           "try?",
            'QUERY_2_MSG': "I found <b>${num}</b> different ${sub} ${prep} ${obj}. You can ask to perform another "
                           "query on the data contained in the AIDA database or ask for Help. What would you like to "
                           "try?",

            'REPROMPT_MSG': 'So, what would you like to ask?',
            'NO_QUERY_MSG': 'Sorry, you asked for a query that is not yet implemented. You can ask to perform another '
                            'query on the data contained in the AIDA database or ask for Help. What would you like to '
                            'try?',

            'REPROMPT_END_MSG': 'You could ask me for another query or say stop to quit',
            'NO_SENSE_MSG': 'I\'m sorry but the query resulting from the chosen options doesn\'t make sense. Try '
                            'again. You can ask to perform another query on the data contained in the AIDA database '
                            'or ask for help. What would you like to try?',

            'LIST_WRONG_NUMBER_MSG': 'The number ${num} , you should tell me a number higher than one and smaller '
                                     'than eleven.',
            'LIST_SUBJECT_REQUEST_MSG': 'I can list <b>papers</b>, <b>authors</b>, <b>conferences</b>, '
                                        '<b>organizations</b> and <b>topics</b>. What do you want me to list?',
            'LIST_SUBJECT_WRONG_MSG': 'Sorry, I can\'t list <b>${sub}</b>. I can list <b>papers</b>, <b>authors</b>, '
                                      '<b>conferences</b>, <b>organizations</b> and <b>topics</b>. What do you prefer?',
            'LIST_SUBJECT_REQUEST_REPROMPT_MSG': 'I can list <b>papers</b>, <b>authors</b>, <b>conferences</b>, '
                                                 '<b>organizations</b> and <b>topics</b>. What do you prefer?',
            'LIST_ORDER_MSG': 'Which sorting option do you prefer between: (1) <b>publications</b>, '
                              '(2) <b>citations</b>, (3) <b>publications in the last 5 years</b> and (4) <b>citations '
                              'in the last 5 years</b>?',
            'LIST_PAPERS_ORDER_MSG': 'Which sorting option do you prefer between: (1) <b>citations</b> and (2) '
                                     '<b>citations in the last 5 years?</b>',

            'LIST_PAPERS_ORDER_WRONG_MSG': 'Sorry, I can\'t list <b>${sub}</b> sorted by <b>${order}</b>. I can sort '
                                           'them by (1)  <b>citations</b> and by (2) <b>citations in the last 5 '
                                           'years</b>. What do you prefer?',
            'LIST_ORDER_WRONG_MSG': 'Sorry, I can\'t list <b>${sub}</b> sorted by <b>${order}</b>. I can sort them '
                                    'by: (1) <b>publications</b>, (2) <b>publications in the last 5 years</b>, '
                                    '(3) <b>citations</b>, (4) <b>citations in the last 5 years</b>. What do you '
                                    'prefer?',
            'LIST_INSTANCE_MSG': 'what is the <b>name</b> of the ${list} for which <b>${sub}</b> should be in the top '
                                 '${num}? You can say <b>all</b> for the full list',
            'LIST_INTENT_CONFIRMATION_1_MSG': 'Do you want to know which are the top ${num} <b>${sub}</b> ${prep} ${'
                                              'obj}, by number of <b>${order}</b>, in the AIDA database?',
            'LIST_INTENT_CONFIRMATION_2_MSG': 'Do you want to know which are the top ${num} <b>${sub}</b>, by number '
                                              'of <b>${order}</b>, ${prep} <b>${ins}</b> ${obj} in the Aida database?',
            'LIST_QUERY_MSG': 'In the AIDA database, the top ${num} <b>${sub}</b> ${prep} <b>${ins}</b> ${obj} - by '
                              'number of <b>${order}</b> - ${verb}: ${lst} You can ask to perform another query on '
                              'the data contained in the AIDA database or ask for Help. What would you like to try?',
            'LIST_NO_RESULT_MSG': 'In the AIDA database, there are no <b>${sub}</b> ${prep} <b>${ins}</b> ${obj}. You '
                                  'can ask to perform another query on the data contained in the AIDA database or ask '
                                  'for Help. What would you like to try?',
            'DSC_TOO_GENERIC_MSG': 'Your search for <b>${ins}</b> got ${results}. You need to try again and to be more '
                                   'specific. What is the <b>name</b> of the <b>author</b> or <b>conference</b> or '
                                   '<b>organization</b> you want to know about?',
            'DSC_NO_RESULT_MSG': 'Your search for <b>${ins}</b> got no result. You need to try again. What is the '
                                 'name of the author or conference you want to know about?',
            'DESCRIBE_INSTANCE_MSG': 'What is the <b>name</b> of the <b>author</b> or <b>conference</b> or '
                                     '<b>organization</b> you want to know about?',
            'DESCRIBE_CONFIRM_MSG': 'Do you want to know something about ${ins}?',

            'COMPARE_FIRST_INSTANCE': 'What is the <b> name </b> of the <b> author </b> or <b> conference </b> or <b> '
                                      'organization </b> that you want to use as the first term for the comparison?',
            'COMPARE_SECOND_INSTANCE': [
                'What is the <b> name </b> of the <b> ${obj} </b> that you want to use as the second term for the '
                'comparison?',
                'What is the <b> name </b> of the <b> ${obj} </b> that you want to compare to ${ins}?'],
            'COMPARE_CONFIRM_MSG': 'Do you want to compare ${ins} to ${ins2}?',
            'COMPARE_TOO_GENERIC_FIRST_MSG': 'Your search for <b>${ins}</b> got ${results}. You need to try again and '
                                             'to be more specific. What is the <b> name </b> of the <b> author </b> '
                                             'or <b> conference </b> or <b> organization </b> that you want to use as '
                                             'the first term for the comparison? <br/>(for organizations you can '
                                             'enter the grid id)',
            'COMPARE_TOO_GENERIC_SECOND_MSG': 'Your search for <b>${ins}</b> got ${results}. You need to try again '
                                              'and to be more specific. What is the <b> name </b> of the <b> ${obj} '
                                              '</b> that you want to use as the second term for the comparison? '
                                              '<br/>(for organizations you can enter the grid id)',
            'COMPARE_NO_RESULT_FIRST_MSG': 'Your search for <b>${ins}</b> got no result. You need to try again. What '
                                           'is the <b> name </b> of the <b> author </b> or <b> conference </b> or <b> '
                                           'organization </b> that you want to use as the first term for the '
                                           'comparison? <br/>(for organizations you can enter the grid id)',
            'COMPARE_NO_RESULT_SECOND_MSG': 'Your search for <b>${ins}</b> got no result. You need to try again. What '
                                            'is the <b> name </b> of the <b> ${obj} </b> that you want to use as the '
                                            'second term for the comparison? <br/>(for organizations you can enter the '
                                            'grid id)',
            'COMPARE_SAME_OBJ_MSG': "Hey, it's the same <b>${obj1}</b>! You can try two different ones or ask for "
                                    "Help. <br/>What would you like to try?",
            'COMPARE_WRONG_PAIR_MSG': "Hey, I can't compare <b>${obj1}</b> to <b>${obj2}</b>! You can try two "
                                      "entities of the same type or ask for Help. <br/>What would you like to try?",
            'COMPARE_AUTHORS_MSG': "<b>${author1}</b> has ${publications}, ${citations} and ${h_index} <b>${"
                                   "author2}</b>. ${topics}<br/>You can ask to perform another query on the data "
                                   "contained in the AIDA database or ask for Help. <br/>What would you like to try?",
            'COMPARE_CONFERENCE_MSG': "${conf1} started ${years} ${conf2} and has ${citations} citations in the last "
                                      "5 years. ${name1} also has ${h5_index} ${name2}. ${topics}<br/>You can ask to "
                                      "perform another query on the data contained in the AIDA database or ask for "
                                      "Help. <br/>What would you like to try?",
            'COMPARE_ORGANIZATIONS_MESSAGE': "${org1} has ${publications} and ${citations} in the last 5 years. It "
                                             "also has ${h5_index} ${org2}. ${topics}<br/>You can ask to perform "
                                             "another query on the data contained in the AIDA database or ask for "
                                             "Help. <br/>What would you like to try?",

            'FREE': '${msg}'
        }

        self.count_dict = {
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

        self.count_legal_queries = {
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

        self.obj_cat = [
            ['authors', 'conference acronyms', 'conference names', 'organizations'],
            ['topics', 'conferences', 'organizations', 'authors', 'papers']
        ]

        self.item_question_object = {
            'topics': '<b>topic</b> or ',
            'conferences': '<b>conference</b> or ',
            'organizations': '<b>organization</b> or ',
            'authors': '<b>author</b>'
        }

        self.numbers = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
            'eight',
            'nine', 'ten', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', 'first', 'second',
            'third',
            'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth'
        ]

        self.list_legal_queries = {
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

        self.list_dict = {
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
            }
        }

        self.dsc_list = [' is an author', ' affiliated to ', ' affiliated to the ', 'Author rating: ', 'Publications: ',
                         'Citations: ',
                         'Total number of co-authors: ', 'The top topic in terms of publications is: ',
                         'The top topics in terms of publications are: ',
                         'The top conference in terms of publications is: ',
                         'The top conferences in terms of publications are: ',
                         'The top journal in terms of publications is: ',
                         'The top journals in terms of publications are: ', ', acronym of ', ', is a conference',
                         'The rankings are: ',
                         'citations in the last 5 years: ', 'Years of activity: from ', ' to ',
                         'Number of publications in the last year: ',
                         'The top country in terms of publications is: ',
                         'The top countries in terms of publications are: ',
                         'The top organization in education is: ', 'The top organizations in education are: ',
                         'The top organization in industry is: ', 'The top organizations in industry are: ',
                         'publications in the last 5 years: ', 'number of affiliated authors: ', ', active between ',
                         ' whose main topics are: ']

        self.compare_preps = [' to ', ' with ', ' vs ', ' against ', ' and ']

        self.compare_valid_combinations = ['1-1', '2-2', '2-3', '3-2', '3-3', '4-4']

        self.session = {'level': 0, 'intent': {'name': '', 'level': 0, 'slots': {}}, 'confirmation': True, 'answer': ''}

    def set_session(self, new_session):
        self.session = new_session

    def get_session(self):
        return self.session

    def welcome(self):
        self.set_message('WELCOME_MSG')

    def get_data(self, cmd, ins):
        try:
            response = urllib.request.urlopen(self.data_server_url + cmd + urllib.parse.quote(str(ins)))
            data = json.load(response)
            assert isinstance(data, dict)
            return data
        except OSError:
            self.session_reset()
            self.set_message('ERROR_MSG')
            return {}

    def get_intent(self, msg):
        message = msg.lower().split(" ")
        for key in self.intents:
            for i in range(len(message)):
                for j in range(len(self.intents[key])):
                    words = self.intents[key][j].split(' ')
                    intent_length = len(words)
                    for k in range(len(words)):
                        z = (+i) + (+k)
                        if z < len(message) and words[k] == message[z]:
                            intent_length -= 1
                    if intent_length == 0:
                        return [key, self.intents[key][j]]
        return ['fallback', 'fallback']

    def get_user_describe_query_text(self, msg):
        query = msg
        idx = -1
        for i in range(len(self.intents['describe'])):
            if self.intents['describe'][i] in query:
                idx = query.index(self.intents['describe'][i])
            if idx >= 0:
                query = query[idx + len(self.intents['describe'][i]) + 1: len(query)]
                return query
        return query

    def set_message(self, msg, options=None):
        value = self.templates[msg]
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
        self.append_message(value)

    def append_message(self, value):
        self.session['answer'] = value

    def item_question(self, subject):
        msg = ''
        sub = subject

        if self.count_legal_queries[sub]['topics'][0]:
            msg += self.item_question_object['topics']
        if self.count_legal_queries[sub]['conferences'][0]:
            msg += self.item_question_object['conferences']
        if self.count_legal_queries[sub]['organizations'][0]:
            msg += self.item_question_object['organizations']
        if self.count_legal_queries[sub]['authors'][0]:
            msg += self.item_question_object['authors']
        s = msg[len(msg) - 4: len(msg)]
        if s == ' or ':
            msg = msg[0: len(msg) - 3]
        return msg

    def kk_message(self, speak, cmd):
        message = ''
        for j in range(len(speak['num'])):
            if speak['num'][j] > 0:
                message += str(speak['num'][j])
                message += (' hits' if speak['num'][j] > 1 else ' hit') + ' among the ' + self.obj_cat[cmd][j] + ', '
        message = message[0: len(message) - 2]
        return message

    def choice_list(self, speak):
        message = ''
        n = 0
        cmd = 0 if speak.get('cmd') is not None else 1
        for i in range(len(speak['num'])):
            if speak['num'][i] > 0:
                for j in range(len(speak['keys'][i])):
                    message += self.numbers[n] + ', <b>'
                    item = speak['keys'][i][j]['name'] if cmd == 0 else speak['keys'][i][j]
                    if (cmd == 1 and i == 3) or (cmd == 0 and i == 0):
                        item = self.upper_first(item)
                    message += item + '</b>; '
                    n += 1
                message += ' among the ' + self.obj_cat[cmd][i] + '. '
        message = message[0: len(message) - 2]
        return message

    def homonyms(self, speak):
        msg = ''
        item = speak['item']
        for i in range(len(item)):
            num = 'say <b>' + self.numbers[i] + '</b> for <b>'
            name = item[i]['name']
            if speak.get('object') == 'authors':
                name = self.upper_first(name)
            msg += num + name + '</b>'
            if item[i].get('affiliation') is not None:
                msg += self.homonyms_list[0] + item[i]['affiliation'] + "; "
            elif item[i].get('country') is not None:
                msg += ' - ' + item[i]['country'] + "; "
            elif item[i].get('paper') is not None:
                msg += self.homonyms_list[1] + item[i]['paper'] + "; "
            elif item[i].get('publications') is not None:
                msg += self.homonyms_list[2] + str(item[i]['publications']) + self.homonyms_list[3] + "; "
            else:
                msg += "; "
            if i > 9:
                return msg
        return msg

    def get_number(self, item):
        words = item.split(' ')
        for i in words:
            if i in self.numbers:
                return self.numbers.index(i) % 10
        return None

    def get_choice(self, speak, num):
        for i in range(len(speak['num'])):
            n = num - speak['num'][i]
            if n < 0 or i == len(speak['num']) - 1:
                return speak['keys'][i][num]
            else:
                num = n

    def list_item_question(self, subject):
        msg = ''
        sub = subject
        if self.list_legal_queries[sub]['topics'][1]:
            msg += self.item_question_object['topics']
        if self.list_legal_queries[sub]['conferences'][1]:
            msg += self.item_question_object['conferences']
        if self.list_legal_queries[sub]['organizations'][1]:
            msg += self.item_question_object['organizations']
        if self.list_legal_queries[sub]['authors'][1]:
            msg += self.item_question_object['authors']
        s = msg[len(msg) - 4: len(msg)]
        if s == ' or ':
            msg = msg[0: len(msg) - 3]
        return msg

    def lst(self, result, order, sub):
        o = self.orders.index(order)
        msg = ''
        lst_ = result['lst']
        if o == 1 or o == 3:
            for i in lst_:
                author = ''
                if i.get('author') is not None and len(i['author']) > 0:
                    author = ' by <b>' + self.upper_authors(i['author']) + '</b>'
                if i['citations'] == 1:
                    i['citations'] = '1'
                    ord_ = self.list_order[o]
                else:
                    ord_ = order
                msg += '<b>'
                msg += self.upper_first(i['name']) if sub == 'authors' else i['name'][0].upper() + i['name'][1:]
                msg += author + '</b> with <b>' + str(int(i['citations'])) + '</b> ' + ord_.split(' ')[0] + ', '
        else:
            for i in lst_:
                if i['papers'] == 1:
                    i['papers'] = '1'
                    ord_ = self.list_order[o]
                else:
                    ord_ = order
                msg += '<b>'
                msg += self.upper_first(i['name']) if sub == 'authors' else i['name'][0].upper() + i['name'][1:]
                msg += '</b> with <b>' + str(i['papers']) + '</b> ' + ord_.split(' ')[0] + ', '
        return msg[:-2] + '. '

    def upper_authors(self, string):
        if ' et al.' in string:
            author = string.replace(' et al.', '')
            author = self.upper_first(author)
            return author + ' et al.'
        return self.upper_first(string)

    def list_elements(self, lst1, element):
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
                msg += '<b>"' + self.upper_first(lst_[j][element]) + '"</b>, '
            else:
                msg += '<b>"' + self.upper_first(lst_[j]) + '"</b>, '
            j += 1
        return msg[:-2] + '. '

    def upper_first(self, str_):
        s = str_.split(' ')
        result = ''
        for i in range(len(s)):
            result += ' ' + s[i][0].upper() + s[i][1:]
        return result[1:]

    def dsc(self, query):
        msg = ''
        item = query['item']
        if query['obj_id'] == 1:
            msg += '<b>' + self.upper_first(item['name']) + '</b>' + self.dsc_list[0]
            if item['last_affiliation'].get('affiliation_name') is not None:
                s = item['last_affiliation']['affiliation_name'].split(' ')
                msg += (self.dsc_list[1] if (s[0] == 'the' or s[0] == 'The') else self.dsc_list[2])
                msg += '<b>' + item['last_affiliation']['affiliation_name'] + '</b>'
                if item['last_affiliation'].get('affiliation_country') is not None:
                    msg += ', ' + item['last_affiliation']['affiliation_country'] + '. '
            else:
                msg += '. '
            msg += self.dsc_list[3]
            if item.get('publications') is not None:
                msg += self.dsc_list[4] + '<b>' + str(item['publications']) + '</b>' + '. '
            if item.get('citations') is not None:
                msg += self.dsc_list[5] + '<b>' + str(item['citations']) + '</b>' + '. '
            if item.get('h-index') is not None:
                msg += 'h-index: ' + '<b>' + str(item['h-index']) + '</b>' + '. '
            if item.get('h5-index') is not None:
                msg += 'h5-index: ' + '<b>' + str(item['h5-index']) + '</b>' + '. '
            if item.get('co_authors') is not None and item['co_authors'] > 0:
                msg += self.dsc_list[6] + '<b>' + str(item['co_authors']) + '</b>' + '. '
            if item.get('top_pub_topics') is not None and len(item['top_pub_topics']) > 0:
                msg += self.dsc_list[7] if len(item['top_pub_topics']) == 1 else self.dsc_list[8]
                msg += self.list_elements(item['top_pub_topics'], 'topic')
            if item.get('top_pub_conf') is not None and len(item['top_pub_conf']) > 0:
                msg += self.dsc_list[9] if len(item['top_pub_conf']) == 1 else self.dsc_list[10]
                msg += self.list_elements(item['top_pub_conf'], 'name')
            if item.get('top_journals') is not None and len(item['top_journals']) > 0:
                msg += self.dsc_list[11] if len(item['top_journals']) == 1 else self.dsc_list[12]
                msg += self.list_elements(item['top_journals'], 'name')
        elif query['obj_id'] == 2 or query['obj_id'] == 3:
            msg += '<b>' + item['acronym'] + '</b>' + self.dsc_list[13] + '<b>' + item['name'] + '</b>' + self.dsc_list[
                14]
            if item.get('activity_years') is not None:
                msg += self.dsc_list[28] + '<b>' + str(item['activity_years']['from']) + '</b>'
                msg += ' and ' + '<b>' + str(item['activity_years']['to']) + '</b>, '
            msg += self.dsc_list[29]
            msg += self.list_elements(item['topics'], '')
            msg += self.dsc_list[15]
            if item.get('h5_index') is not None:
                msg += 'h5-index: ' + '<b>' + str(item['h5_index']) + '</b>. '
            if item.get('citationcount_5') is not None:
                msg += self.dsc_list[16] + '<b>' + str(item['citationcount_5']) + '</b>. '
            if item.get('last_year_publications') is not None and item['last_year_publications'] > 0:
                msg += self.dsc_list[19] + '<b>' + str(item['last_year_publications']) + '</b>. '
            if len(item['top_3_country']) > 0:
                msg += self.dsc_list[20] if len(item['top_3_country']) == 1 else self.dsc_list[21]
                msg += self.list_elements(item['top_3_country'], '')
            if len(item['top_3_edu']) > 0:
                msg += self.dsc_list[22] if len(item['top_3_edu']) == 1 else self.dsc_list[23]
                msg += self.list_elements(item['top_3_edu'], '')
            if len(item['top_3_company']) > 0:
                msg += self.dsc_list[24] if len(item['top_3_company']) == 1 else self.dsc_list[25]
                msg += self.list_elements(item['top_3_company'], '')
        elif query['obj_id'] == 4:
            msg += '<b>' + item['name'] + '</b>'
            msg += ((' -<b> ' + item['country'] + ' </b>-') if item.get('country') is not None else '')
            msg += ' is an organization'
            if item.get('type') is not None and (item['type'] == 'academia' or item['type'] == 'industry'):
                msg += ' in <b>' + ('Edu' if item['type'] == 'academia' else 'Industry') + '</b> sector. '
            else:
                msg += '. '

            msg += self.dsc_list[15]
            if item.get('h5-index') is not None:
                msg += 'h5-index: <b>' + str(item['h5-index']) + '</b>. '
            if item.get('publications_5') is not None:
                msg += self.dsc_list[26] + '<b>' + str(item['publications_5']) + '</b>. '
            if item.get('citations_5') is not None:
                msg += self.dsc_list[16] + '<b>' + str(item['citations_5']) + '</b>. '
            if item.get('authors_number') is not None:
                msg += self.dsc_list[27] + '<b>' + str(item['authors_number']) + '</b>. '
            if item.get('top_3_topics') is not None and len(item['top_3_topics']) > 0:
                msg += self.dsc_list[7] if len(item['top_3_topics']) == 1 else self.dsc_list[8]
                msg += self.list_elements(item['top_3_topics'], '')
            if item.get('top_3_conferences') is not None and len(item['top_3_conferences']) > 0:
                msg += self.dsc_list[9] if len(item['top_3_conferences']) == 1 else self.dsc_list[10]
                msg += self.list_elements(item['top_3_conferences'], '')
            if item.get('top_3_journals') is not None and len(item['top_3_journals']) > 0:
                msg += self.dsc_list[11] if len(item['top_3_journals']) == 1 else self.dsc_list[12]
                msg += self.list_elements(item['top_3_journals'], '')
            else:
                msg += 'Sorry, Query not yet implemented!'
                return msg
        msg += 'You can ask to perform another query on the data contained in the AIDA database or ask for Help. '
        return msg + 'What would you like to try?'

    def get_instances_from_query(self, query):
        for prep in self.compare_preps:
            instances = query.split(prep)
            if len(instances) > 1:
                return instances
        if len(query) > 0:
            return [query]
        return []

    def get_user_compare_query_text(self, msg):
        query = msg
        idx = -1
        for i in range(len(self.intents['compare'])):
            if self.intents['compare'][i] in query:
                idx = query.index(self.intents['compare'][i])
                if idx >= 0:
                    query = query[idx + len(self.intents['compare'][i]) + 1: len(query)]
                    return self.get_instances_from_query(query)
        return self.get_instances_from_query(query)

    def cmp(self, term1, term2):
        comb = str(term1['obj_id']) + '-' + str(term2['obj_id'])
        if comb in self.compare_valid_combinations:
            params = {'obj1': term1['object'], 'obj2': term2['object']}
            self.set_message('COMPARE_WRONG_PAIR_MSG', params)
        if term1['item'] == term2['item']:
            params = {'obj1': self.compare_categories[term1['obj_id'] - 1]}
            self.set_message('COMPARE_SAME_OBJ_MSG', params)

        parameters = {}

        if term1['obj_id'] == 1:
            pub_diff = term1['item']['publications'] - term2['item']['publications']
            parameters['author1'] = self.upper_first(term1['item']['name'])
            parameters['author2'] = self.upper_first(term2['item']['name'])
            if pub_diff != 0:
                publications = str(abs(pub_diff)) + (' fewer ' if pub_diff < 0 else ' more ') + 'publications ('
                publications += str(term1['item']['publications']) + ' vs ' + str(term2['item']['publications']) + ')'
            else:
                publications = 'the same number of publications ' + '(' + str(term1['item']['publications']) + ')'
            parameters['publications'] = publications

            cit_diff = term1['item']['citations'] - term2['item']['citations']
            if cit_diff != 0:
                citations = str(abs(cit_diff)) + (' fewer ' if cit_diff < 0 else ' more ') + 'citations ('
                citations += str(term1['item']['citations']) + ' vs ' + str(term2['item']['citations']) + ')'
            else:
                citations = 'the same number of citations ' + '(' + str(term1['item']['citations']) + ')'

            parameters['citations'] = citations

            h_index_diff = term1['item']['h-index'] - term2['item']['h-index']
            if h_index_diff != 0:
                h_index = 'an h-index ' + str(abs(h_index_diff)) + ' points'
                h_index += ' lower ' if h_index_diff < 0 else ' higher '
                h_index += '(' + str(term1['item']['h-index']) + ' vs '
                h_index += str(term2['item']['h-index']) + ') than'
            else:
                h_index = 'the same h-index ' + '(' + str(term1['item']['h-index']) + ') as'

            parameters['h_index'] = h_index

            topics = ''
            name1 = '<b>' + parameters['author1'].split(' ')[0] + '</b>'
            name2 = '<b>' + parameters['author2'].split(' ')[0] + '</b>'
            topics1 = term1['item']['top_pub_topics']
            topics2 = term2['item']['top_pub_topics']
            topic_analysis = self.commons(topics1, topics2, term1['obj_id'])

            if len(topic_analysis['commons']) > 0:
                topics = 'Both of them work in ' + self.list2string(topic_analysis['commons']) + '. '

            if len(topic_analysis['first']) > 0 and len(topic_analysis['second']) > 0:
                topics += name1 + ' focuses more on ' + self.list2string(topic_analysis['first'])
                topics += ' while ' + name2 + ' focuses more on ' + self.list2string(topic_analysis['second']) + '. '
            elif len(topic_analysis['first']) > 0:
                topics += name1 + ' focuses more on ' + self.list2string(topic_analysis['first']) + '. '
            elif len(topic_analysis['second']) > 0:
                topics += name2 + ' focuses more on ' + self.list2string(topic_analysis['second']) + '. '

            parameters['topics'] = topics
            self.set_message('COMPARE_AUTHORS_MSG', parameters)
            return

        if term1['obj_id'] == 2 or term1['obj_id'] == 3:
            conf1 = '<b>'
            conf2 = '<b>'
            if 'conference' in term1['item']['name'].lower():
                conf1 += term1['item']['name'] + '</b>'
            else:
                conf1 += term1['item']['name'] + '</b> conference'

            if 'conference' in term2['item']['name'].lower():
                conf2 += term2['item']['name'] + '</b>'
            else:
                conf2 += term2['item']['name'] + '</b> conference'

            parameters['conf1'] = conf1
            parameters['conf2'] = conf2
            parameters['name1'] = '<b>' + term1['item']['acronym'] + '</b>'
            parameters['name2'] = '<b>' + term2['item']['acronym'] + '</b>'

            activity_diff = term1['item']['activity_years']['from'] - term2['item']['activity_years']['from']
            num = str(abs(activity_diff)) + (' years after ' if activity_diff < 0 else ' years before ')
            if activity_diff == 0:
                num = 'the same year as'

            parameters['years'] = num

            cit_diff = term1['item']['citationcount_5'] - term2['item']['citationcount_5']
            citations = str(abs(cit_diff)) + (' less ' if cit_diff < 0 else ' more ')
            if cit_diff == 0:
                citations = 'the same number of'

            parameters['citations'] = citations

            h_index_diff = term1['item']['h5_index'] - term2['item']['h5_index']
            if h_index_diff != 0:
                h_index = 'an h-index ' + str(abs(h_index_diff)) + ' points'
                h_index += (' lower ' if h_index_diff < 0 else ' higher ')
                h_index += '(' + str(term1['item']['h5_index']) + ' vs ' + str(term2['item']['h5_index']) + ') than'
            else:
                h_index = 'the same h-index ' + '(' + str(term1['item']['h5_index']) + ') as'

            parameters['h5_index'] = h_index

            topics1 = term1['item']['topics']
            topics2 = term2['item']['topics']
            topic_analysis = self.commons(topics1, topics2, term1['obj_id'])
            topics = ''
            if len(topic_analysis['commons']) > 0:
                topics = 'Both have ' + self.list2string(topic_analysis['commons']) + ' as their main topic'

            if len(topic_analysis['commons']) > 1:
                topics += 's. '
            elif len(topic_analysis['commons']) > 0:
                topics += '. '

            if len(topic_analysis['first']) > 0 and len(topic_analysis['second']) > 0:
                topics += parameters['name1'] + ' focuses more on '
                topics += self.list2string(topic_analysis['first']) + ' while ' + parameters['name2']
                topics += ' focuses more on ' + self.list2string(topic_analysis['second']) + '. '
            elif len(topic_analysis['first']) > 0:
                topics += parameters['name1'] + ' focuses more on ' + self.list2string(topic_analysis['first']) + '. '
            elif len(topic_analysis['second']) > 0:
                topics += parameters['name2'] + ' focuses more on ' + self.list2string(topic_analysis['second']) + '. '

            parameters['topics'] = topics

            self.set_message('COMPARE_CONFERENCE_MSG', parameters)
            return

        if term1['obj_id'] == 4:
            parameters['org1'] = '<b>' + term1['item']['name'] + '</b>'
            parameters['org2'] = '<b>' + term2['item']['name'] + '</b>'

            pub_diff = term1['item']['publications_5'] - term2['item']['publications_5']

            if pub_diff != 0:
                publications = str(abs(pub_diff)) + (' fewer ' if pub_diff < 0 else ' more ') + 'publications ('
                publications += str(term1['item']['publications_5']) + ' vs '
                publications += str(term2['item']['publications_5']) + ')'
            else:
                publications = 'the same number of publications ' + '(' + str(term1['item']['publications_5']) + ')'

            parameters['publications'] = publications

            cit_diff = term1['item']['citations_5'] - term2['item']['citations_5']

            if cit_diff != 0:
                citations = str(abs(cit_diff)) + (' fewer ' if cit_diff < 0 else ' more ') + 'citations ('
                citations += str(term1['item']['citations_5']) + ' vs ' + str(term2['item']['citations_5']) + ')'
            else:
                citations = 'the same number of citations ' + '(' + term1['item']['citations_5'] + ')'

            parameters['citations'] = citations

            h_index_diff = term1['item']['h5-index'] - term2['item']['h5-index']
            if h_index_diff != 0:
                h_index = 'an h-index ' + str(abs(h_index_diff)) + ' points'
                h_index += (' lower ' if h_index_diff < 0 else ' higher ') + '('
                h_index += str(term1['item']['h5-index']) + ' vs ' + str(term2['item']['h5-index']) + ') than'
            else:
                h_index = 'the same h-index ' + '(' + str(term1['item']['h-index']) + ') as'

            parameters['h5_index'] = h_index

            topics = ''
            topics1 = term1['item']['top_3_topics']
            topics2 = term2['item']['top_3_topics']
            topic_analysis = self.commons(topics1, topics2, term1['obj_id'])

            if len(topic_analysis['commons']) > 0:
                topics = 'Both have ' + self.list2string(topic_analysis['commons']) + ' as their main topic'

            if len(topic_analysis['commons']) > 1:
                topics += 's. '
            elif len(topic_analysis['commons']) > 0:
                topics += '. '

            if len(topic_analysis['first']) > 0 and len(topic_analysis['second']) > 0:
                topics += parameters['org1'] + ' focuses more on ' + self.list2string(topic_analysis['first'])
                topics += ' while ' + parameters['org2'] + ' focuses more on '
                topics += self.list2string(topic_analysis['second']) + '. '
            elif len(topic_analysis['first']) > 0:
                topics += parameters['org1'] + ' focuses more on ' + self.list2string(topic_analysis['first']) + '. '
            elif len(topic_analysis['second']) > 0:
                topics += parameters['org2'] + ' focuses more on ' + self.list2string(topic_analysis['second']) + '. '

            parameters['topics'] = topics
            self.set_message('COMPARE_ORGANIZATIONS_MESSAGE', parameters)
            return

    def commons(self, l1, l2, obj_id):
        common_topics = []
        topics1 = []
        topics2 = []
        if obj_id == 1:
            for topic in l1:
                for topic2 in l2:
                    if topic['topic'] == topic2['topic']:
                        common_topics.append(topic['topic'])

            for topic in l1:
                if topic['topic'] not in common_topics:
                    topics1.append(topic['topic'])

            for topic in l2:
                if topic['topic'] not in common_topics:
                    topics2.append(topic['topic'])

        else:
            for topic in l1:
                if topic in l2:
                    common_topics.append(topic)

            for topic in l1:
                if topic not in common_topics:
                    topics1.append(topic)

            for topic in l2:
                if topic not in common_topics:
                    topics2.append(topic)

        return {'commons': common_topics, 'first': topics1, 'second': topics2}

    def list2string(self, word_list):
        n = len(word_list)
        word_string = ''
        for i in range(len(word_list)):
            if i < n - 2:
                word_string += word_list[i] + ', '
            elif i < n - 1:
                word_string += word_list[i] + ' and '
            else:
                word_string += word_list[i]

        return word_string

    def session_reset(self):
        answer = self.session['answer']
        self.session = {'level': 0, 'intent': {'name': '', 'level': 0, 'slots': {}}, 'confirmation': True,
                        'answer': answer}

    def intent_verify(self, msg):
        intent = self.get_intent(msg)
        msg = msg.replace(intent[1], intent[0])
        intent = intent[0]

        if intent == 'hello':
            self.set_message('HELLO_MSG')
        elif intent == 'reset':
            self.set_message('REPROMPT_MSG')
            self.session_reset()
        elif intent == 'help':
            self.set_message('HELP_MSG')
        elif intent == 'cancel':
            self.set_message('GOODBYE_MSG')
            self.session_reset()

        elif intent == 'count' or intent == 'list':
            self.session['level'] = 1
            self.set_intent_slots(self.get_data('cmd=parser&ins=', str(msg)))

        elif intent == 'describe':
            self.session['intent']['name'] = 'describe'
            self.session['level'] = 1
            query = self.get_user_describe_query_text(msg)
            if len(query) > 0:
                self.session['intent']['slots']['ins'] = query
            self.describe_query('')
            return

        elif intent == 'compare':
            self.session['intent']['name'] = 'compare'
            self.session['level'] = 1
            query = self.get_user_compare_query_text(msg)
            if len(query) > 1:
                self.session['intent']['slots']['ins'] = query[0]
                self.session['intent']['slots']['ins2'] = query[1]
            elif len(query) > 0:
                self.session['intent']['slots']['ins'] = query[0]
            self.compare_query('')
            return

        elif intent == 'fallback':
            self.set_message('FALLBACK_MSG')
        return

    # set intent name and slots with the results from the parser
    def set_intent_slots(self, data):
        cmd = ''

        if data.get('cmd') is not None:
            cmd = data['cmd']['value']

        if cmd == 'count':
            self.session['intent']['name'] = 'count'
            if data.get('sub') is not None:
                self.session['intent']['slots']['sub'] = data['sub']['value']
            if data.get('ins') is not None:
                self.session['intent']['slots']['ins'] = data['ins']['value']
            if data.get('obj') is not None:
                self.session['intent']['slots']['obj'] = data['obj']['value']
            elif data.get('sub') is not None and data.get('ins') is not None and data['ins']['value'] == 'all':
                self.session['intent']['slots']['obj'] = self.combinations[data['sub']['value']]
            self.count_query('')

        if cmd == 'list':
            self.session['intent']['name'] = 'list'
            if data.get('num') is not None:
                self.session['intent']['slots']['num'] = data['num']['value']
            if data.get('sub') is not None:
                self.session['intent']['slots']['sub'] = data['sub']['value']
            if data.get('ins') is not None:
                self.session['intent']['slots']['ins'] = data['ins']['value']
            if data.get('obj') is not None:
                self.session['intent']['slots']['obj'] = data['obj']['value']
            elif data.get('sub') is not None and data.get('ins') is not None and data['ins']['value'] == 'all':
                self.session['intent']['slots']['obj'] = 'all'
            if data.get('order') is not None:
                self.session['intent']['slots']['order'] = data['order']['value']
            self.list_query('')

    def is_list_legal(self, sub, obj, order=None):
        if sub is None or obj is None:
            return False
        if order is not None:
            return self.list_legal_queries[sub][obj][self.orders.index(order.split(' ')[0])]
        return self.list_legal_queries[sub][obj][0] or self.list_legal_queries[sub][obj][1]

    def count_query(self, msg):
        slots = self.session['intent']['slots']
        sub = slots.get('sub')
        obj = slots.get('obj')
        ins = slots.get('ins')
        idx = slots.get('id')
        sub_id = (self.subject_categories.index(sub) + 1) if sub in self.subject_categories else 0
        obj_id = (self.object_categories.index(obj) + 1) if obj in self.object_categories else 0

        # no level - verifying slots
        if self.session['intent'].get('level') == 0:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            if sub is None and len(msg) == 0:
                self.session['confirmation'] = False
                self.set_message('SUBJECT_REQUEST_MSG')
                return

            if sub is None and len(msg) > 0:
                if msg in self.subject_categories:
                    sub_id = self.subject_categories.index(msg) + 1
                    self.session['intent']['slots']['sub'] = msg
                    sub = msg
                    msg = ''

                else:
                    self.set_message('SUBJECT_WRONG_MSG', {'sub': msg})
                    return

            if sub is not None and sub not in self.subject_categories:
                self.set_message('SUBJECT_WRONG_MSG', {'sub': sub})
                del self.session['intent']['slots']['sub']
                return

            if ins is not None and ins != 'all':
                self.session['intent']['level'] = 1
                data = self.get_data('cmd=fnd&ins=', ins)
                self.count_query(data)
                return

            if ins is None and len(msg) == 0:
                self.session['confirmation'] = False
                message = 'INSTANCE_MSG'
                if sub_id == 5:
                    message = 'INSTANCE2_MSG'
                self.set_message(message, {'list': self.item_question(sub), 'sub': sub})
                return

            if ins is None and len(msg) > 0 and msg != 'all':
                self.session['intent']['slots']['ins'] = msg
                data = self.get_data('cmd=fnd&ins=', msg)
                self.session['intent']['level'] = 1
                self.count_query(data)
                return

            if (sub is not None and ins is not None and ins == 'all') or (
                    sub is not None and ins is None and msg == 'all'):
                if not self.count_legal_queries[sub][self.combinations[sub]][1]:
                    self.set_message('NO_SENSE_MSG')
                    self.session_reset()
                    return
                obj = self.combinations[sub]
                self.session['intent']['slots']['obj'] = obj
                self.session['intent']['slots']['ins'] = 'no'
                self.session['intent']['level'] = 2
                if self.session['confirmation']:
                    self.set_message('INTENT_CONFIRMATION_1_MSG',
                                     {'sub': self.count_dict['sub'][sub][obj],
                                      'prep': self.count_dict['prep'][sub][obj],
                                      'obj': self.count_dict['obj'][sub][obj]})
                    return
                else:
                    self.count_query('')
            return

        # verifying ins
        if self.session['intent']['level'] == 1:
            # case ok
            if msg['result'] == 'ok':
                ins = msg['item']
                self.session['intent']['slots']['ins'] = ins
                obj_id = msg['obj_id']
                obj = msg['object']
                self.session['intent']['slots']['obj'] = obj

                if obj_id == 2 or obj_id == 4:
                    self.session['intent']['slots']['id'] = msg['id']

                if not self.count_legal_queries[sub][obj][0]:
                    self.set_message('NO_SENSE_MSG', {})
                    self.session_reset()
                    return

                if obj_id == 4:
                    ins = self.upper_first(ins)

                self.session['intent']['level'] = 2

                if self.session['confirmation']:
                    self.set_message('INTENT_CONFIRMATION_2_MSG',
                                     {'sub': self.count_dict['sub'][sub][obj],
                                      'prep': self.count_dict['prep'][sub][obj],
                                      'obj': self.count_dict['obj'][sub][obj],
                                      'ins': ins})
                    return
                else:
                    self.count_query('')
                return

            # case kk (too many results fnd search)
            if msg['result'] == 'kk':
                message = self.kk_message(msg, 1)
                self.set_message('TOO_GENERIC_MSG', {'ins': ins, 'results': message})
                self.session['intent']['level'] = 0
                del self.session['intent']['slots']['ins']
                return

            # case ko (no result fnd search)
            if msg['result'] == 'ko':
                self.set_message('NO_RESULT_MSG', {'ins': ins})
                self.session['intent']['level'] = 0
                del self.session['intent']['slots']['ins']
                return

            # case k2 (multiple results fnd search)
            if msg['result'] == 'k2':

                num_res = 0
                for i in range(len(msg['num'])):
                    obj = self.object_categories[i]
                    if not self.count_legal_queries[sub][obj][0]:
                        msg['num'][i] = 0
                        msg['keys'][i] = []
                    num_res += msg['num'][i]
                if num_res == 0:
                    self.set_message('NO_SENSE_MSG')
                    self.session_reset()
                    return
                elif num_res == 1:
                    for i in range(len(msg['num'])):
                        if msg['num'][i] == 1:
                            self.session['intent']['slots']['ins'] = msg['keys'][i][0]
                            self.session['intent']['level'] = 0
                            self.count_query('')
                            return

                self.session['intent']['items_list'] = msg
                message = self.choice_list(msg)
                self.set_message('ITEM_MSG', {'ins': ins, 'msg': message})
                self.session['intent']['level'] = 3
                return

            # case ka(homonyms fnd search)
            if msg['result'] == 'ka':
                obj = msg['object']
                if not self.count_legal_queries[sub][obj][0]:
                    self.set_message('NO_SENSE_MSG')
                    self.session_reset()
                    return

                self.session['intent']['homonyms_list'] = msg
                message = self.homonyms(msg)
                self.set_message('HOMONYMS_MSG', {'msg': message, 'obj': self.homonyms_objects[msg['obj_id'] - 1]})
                self.session['intent']['level'] = 4
                return

        # check, confirm and display of results
        if self.session['intent']['level'] == 2:
            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG', {})
                self.session_reset()
                return

            inst = ins
            if idx is not None:
                inst = idx

            data = self.get_data('cmd=how&sub=' + str(sub_id) + '&obj=' + str(obj_id) + '&ins=', inst)

            if data['result'] != 'ok':
                self.set_message('NO_QUERY_MSG', {})
                self.session_reset()
                return

            if obj_id == 4:
                ins = self.upper_first(ins)

            message = 'QUERY_1_MSG'
            if ins == 'no':
                message = 'QUERY_2_MSG'
                self.set_message(message, {'num': data['hits'], 'sub': self.count_dict['sub'][sub][obj],
                                           'obj': self.count_dict['obj'][sub][obj],
                                           'prep': self.count_dict['prep'][sub][obj]})
            else:
                msg_sub = self.count_dict['sub'][sub][obj][0: len(sub) - 1] if data['hits'] == '1' else \
                    self.count_dict['sub'][sub][obj]
                self.set_message(message, {'num': data['hits'], 'sub': msg_sub, 'obj': self.count_dict['obj'][sub][obj],
                                           'prep': self.count_dict['prep'][sub][obj], 'ins': ins})

            self.session_reset()
            return

        # multiple result list management
        if self.session['intent']['level'] == 3:
            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG', {})
                self.session_reset()
                return

            num = self.get_number(msg)
            if num is not None and num <= sum(self.session['intent']['items_list']['num']):
                ins = self.get_choice(self.session['intent']['items_list'], num)
                self.session['intent']['slots']['ins'] = ins
                self.session['intent']['level'] = 0
                del self.session['intent']['items_list']
                self.count_query('')
                return
            else:
                self.session['intent']['level'] = 1
                msg = self.session['intent']['items_list']
                del self.session['intent']['items_list']
                self.count_query(msg)

        # homonyms list management
        if self.session['intent']['level'] == 4:
            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG', {})
                self.session_reset()
                return

            num = self.get_number(msg)
            if num is not None and num <= (len(self.session['intent']['homonyms_list']['item']) - 1):
                if self.session['intent']['homonyms_list']['obj_id'] == 2:
                    # noinspection PyTypeChecker
                    ins = self.session['intent']['homonyms_list']['item'][num]['acronym']
                else:
                    # noinspection PyTypeChecker
                    ins = self.session['intent']['homonyms_list']['item'][num]['name']
                msg = copy.deepcopy(self.session['intent']['homonyms_list'])
                msg["result"] = "ok"
                # noinspection PyTypeChecker
                msg["id"] = self.session['intent']['homonyms_list']['item'][num]['id']
                msg["item"] = ins
            else:
                msg = self.session['intent']['homonyms_list']

            del self.session['intent']['homonyms_list']
            self.session['intent']['level'] = 1
            self.count_query(msg)
            return

    def list_query(self, msg):
        slots = self.session['intent']['slots']
        sub = slots.get('sub')
        obj = slots.get('obj')
        ins = slots.get('ins')
        idx = slots.get('id')
        num = slots.get('num')
        order = slots.get('order')

        sub_id = (self.list_subject_categories.index(sub) + 1) if sub in self.list_subject_categories else 0
        obj_id = (self.object_categories.index(obj) + 1) if obj in self.object_categories else 0
        order_id = (self.orders.index(order) + 1) if order in self.orders else 0

        # level == 0 - verifying slots
        if self.session['intent'].get('level') == 0:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG', {})
                self.session_reset()
                return

            if num is not None and (int(num) > 10 or int(num) < 2):
                if len(msg) == 0:
                    self.session['confirmation'] = False
                    msg_options = {'num': str(num) + (' is too big' if num > 10 else ' is too small')}
                    self.set_message('LIST_WRONG_NUMBER_MSG', msg_options)
                    return
                elif 1 < int(msg) < 11:
                    self.session['intent']['slots']['num'] = int(msg)
                    num = self.session['intent']['slots']['num']
                    msg = ''
                else:
                    num = int(msg)
                    msg_options = {'num': str(num) + (' is too big' if num > 10 else ' is too small')}
                    self.set_message('LIST_WRONG_NUMBER_MSG', msg_options)
                    return

            if sub is None and len(msg) == 0:
                self.session['confirmation'] = False
                self.set_message('LIST_SUBJECT_REQUEST_MSG', {})
                return

            if sub is None and len(msg) > 0:
                if msg in self.list_subject_categories:
                    sub = msg
                    self.session['intent']['slots']['sub'] = msg
                    msg = ''
                    sub_id = self.list_subject_categories.index(sub) + 1
                else:
                    self.set_message('LIST_SUBJECT_WRONG_MSG', {'sub': msg})
                    return

            if sub is not None and sub not in self.list_subject_categories:
                self.session['confirmation'] = False
                self.set_message('LIST_SUBJECT_WRONG_MSG', {'sub': sub})
                if self.session['intent']['slots'].get('sub') is not None:
                    del self.session['intent']['slots']['sub']
                return

            if ins is not None and ins != 'all':
                self.session['intent']['level'] = 1
                data = self.get_data('cmd=fnd&ins=', ins)
                self.list_query(data)
                return

            if (ins is not None and ins == 'all') or (ins is None and msg == 'all'):
                self.session['intent']['level'] = 2
                self.session['intent']['slots']['obj'] = 'all'
                self.session['intent']['slots']['ins'] = 'all'
                self.list_query('')
                return

            if ins is None and len(msg) == 0:
                self.session['confirmation'] = False
                message = 'LIST_INSTANCE_MSG'
                self.set_message(message, {'list': self.list_item_question(sub), 'sub': sub, 'num': num})
                return

            if ins is None and len(msg) > 0 and msg != 'all':
                self.session['intent']['slots']['ins'] = msg
                data = self.get_data('cmd=fnd&ins=', msg)
                self.session['intent']['level'] = 1
                self.list_query(data)
                return

        # verifying ins != 'all'
        if self.session['intent']['level'] == 1:
            assert isinstance(msg, dict)

            # ok case
            if msg['result'] == 'ok':
                # ins = msg['item']
                self.session['intent']['slots']['ins'] = msg['item']
                obj_id = msg['obj_id']
                obj = msg['object']
                self.session['intent']['slots']['obj'] = msg['object']

                if obj_id == 2 or obj_id == 4:
                    self.session['intent']['slots']['id'] = msg['id']

                if sub is not None and obj is not None and not self.is_list_legal(sub, obj):
                    self.set_message('NO_SENSE_MSG')
                    self.session_reset()
                    return

                self.session['intent']['level'] = 2
                self.list_query('')
                return

            # kk case
            if msg['result'] == 'kk':
                message = self.kk_message(msg, 1)
                self.set_message('TOO_GENERIC_MSG', {'ins': ins, 'results': message})
                if self.session['intent'].get('level') is not None:
                    self.session['intent']['level'] = 0
                if self.session['intent']['slots'].get('ins') is not None:
                    del self.session['intent']['slots']['ins']
                return

            # ko case
            if msg['result'] == 'ko':
                self.set_message('NO_RESULT_MSG', {'ins': ins})
                if self.session['intent'].get('level') is not None:
                    self.session['intent']['level'] = 0
                if self.session['intent']['slots'].get('ins') is not None:
                    del self.session['intent']['slots']['ins']
                return

            # k2 case
            if msg['result'] == 'k2':

                num_res = 0
                for i in range(len(msg['num'])):
                    obj = self.object_categories[i]
                    if not self.is_list_legal(sub, obj):
                        msg['num'][i] = 0
                        msg['keys'][i] = []
                    num_res += msg['num'][i]
                if num_res == 0:
                    self.set_message('NO_SENSE_MSG')
                    self.session_reset()
                    return
                elif num_res == 1:
                    for i in range(len(msg['num'])):
                        if msg['num'][i] == 1:
                            self.session['intent']['slots']['ins'] = msg['keys'][i][0]
                            self.session['intent']['level'] = 0
                            self.list_query('')
                            return

                self.session['intent']['items_list'] = msg
                message = self.choice_list(msg)
                self.set_message('ITEM_MSG', {'ins': ins, 'msg': message})
                self.session['intent']['level'] = 3
                return

            # ka case homonyms
            if msg['result'] == 'ka':
                self.session['intent']['homonyms_list'] = msg
                message = self.homonyms(msg)
                self.set_message('HOMONYMS_MSG', {'msg': message, 'obj': self.homonyms_objects[msg['obj_id'] - 1]})
                self.session['intent']['level'] = 4
                return

        # slots verify part II
        if self.session['intent']['level'] == 2:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG', {})
                self.session_reset()
                return

            if order is None and len(msg) == 0:
                self.session['confirmation'] = False
                message = 'LIST_ORDER_MSG'
                if sub is not None and self.list_subject_categories.index(sub) == 1:
                    message = 'LIST_PAPERS_ORDER_MSG'
                self.set_message(message, {'num': num, 'sub': sub})
                return

            if order is None and len(msg) > 0:
                n = self.get_number(msg)
                if n is not None:
                    if sub is not None and self.list_subject_categories.index(sub) == 1:
                        if -1 < n < 2:
                            msg = self.orders[n * 2 + 1]
                    else:
                        if -1 < n < 4:
                            msg = self.orders[n]

                if msg in self.orders:
                    order = msg
                    self.session['intent']['slots']['order'] = msg
                    msg = ''
                    order_id = self.orders.index(order) + 1
                else:
                    message = 'LIST_ORDER_WRONG_MSG'
                    if sub is not None and self.list_subject_categories.index(sub) == 1:
                        message = 'LIST_PAPERS_ORDER_WRONG_MSG'
                    self.set_message(message, {'sub': sub, 'order': msg})
                    return

            if ins is not None and ins == 'all':
                if not self.is_list_legal(sub, obj, order):
                    self.set_message('NO_SENSE_MSG')
                    self.session_reset()
                    return

                self.session['intent']['level'] = 5

                if self.session['confirmation']:
                    self.set_message('LIST_INTENT_CONFIRMATION_1_MSG',
                                     {'order': order, 'num': num,
                                      'sub': (self.list_dict[order.split(' ')[0]]['sub'][sub][sub]),
                                      'prep': self.list_dict[order.split(' ')[0]]['prep'][sub][sub],
                                      'obj': self.list_dict[order.split(' ')[0]]['obj'][sub][sub]})
                    return
                else:
                    self.list_query('')
                    return

            if ins is not None and ins != 'all':
                if not self.list_legal_queries[sub][obj][self.orders.index(order.split(' ')[0])]:
                    self.set_message('NO_SENSE_MSG')
                    self.session_reset()
                    return

                msg_ins = ins
                if obj_id == 4:
                    msg_ins = self.upper_first(ins)

                self.session['intent']['level'] = 5

                if self.session['confirmation']:
                    options = {'ins': msg_ins, 'order': order, 'num': num,
                               'sub': (self.list_dict[order.split(' ')[0]]['sub'][sub][obj]),
                               'prep': self.list_dict[order.split(' ')[0]]['prep'][sub][obj],
                               'obj': self.list_dict[order.split(' ')[0]]['obj'][sub][obj]}

                    self.set_message('LIST_INTENT_CONFIRMATION_2_MSG', options)
                    return
                else:
                    self.list_query('')
                    return

        # multiple result list management
        if self.session['intent']['level'] == 3:
            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            choice = self.get_number(msg)
            if choice is not None and choice <= sum(self.session['intent']['items_list']['num']):
                ins = self.get_choice(self.session['intent']['items_list'], choice)
                self.session['intent']['slots']['ins'] = ins
                self.session['intent']['level'] = 0
                del self.session['intent']['items_list']
                self.list_query('')
                return
            else:
                self.session['intent']['level'] = 1
                msg = self.session['intent']['items_list']
                del self.session['intent']['items_list']
                self.list_query(msg)

        # homonyms list management
        if self.session['intent']['level'] == 4:
            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG', {})
                self.session_reset()
                return

            choice = self.get_number(msg)
            if choice is not None and choice <= (len(self.session['intent']['homonyms_list']['item']) - 1):
                if self.session['intent']['homonyms_list']['obj_id'] == 2:
                    # noinspection PyTypeChecker
                    ins = self.session['intent']['homonyms_list']['item'][choice]['acronym']
                else:
                    # noinspection PyTypeChecker
                    ins = self.session['intent']['homonyms_list']['item'][choice]['name']
                msg = copy.deepcopy(self.session['intent']['homonyms_list'])
                msg["result"] = "ok"
                # noinspection PyTypeChecker
                msg["id"] = self.session['intent']['homonyms_list']['item'][choice]['id']
                msg["item"] = ins
            else:
                msg = self.session['intent']['homonyms_list']

            del self.session['intent']['homonyms_list']
            self.session['intent']['level'] = 1
            self.list_query(msg)
            return

        # check, confirm and display of results
        if self.session['intent']['level'] == 5:
            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            inst = ins
            if idx is not None:
                inst = idx

            call = 'cmd=lst&sub=' + str(sub_id) + '&obj=' + str(obj_id) + '&ord='
            call += str(order_id) + '&num=' + str(num) + '&ins='
            data = self.get_data(call, inst)

            if obj == 'all':
                obj = sub
                ins = ''

            msg_ins = ins
            if obj_id == 4:
                msg_ins = self.upper_first(ins)

            ord_ = order.split(' ')[0]
            sub1 = self.list_dict[ord_]['sub'][sub][obj]
            obj1 = self.list_dict[ord_]['obj'][sub][obj]
            prep = self.list_dict[ord_]['prep'][sub][obj]

            if data['result'] == 'ok' and len(data['lst']) > 0:

                msg_num = '' if len(data['lst']) == 1 else num
                msg_sub = sub1[0: len(sub) - 1] if len(data['lst']) == 1 else sub1
                # noinspection PyTypeChecker
                options = {'order': order, 'num': msg_num, 'sub': msg_sub, 'obj': obj1, 'prep': prep, 'ins': msg_ins,
                           'verb': (self.list_verbs[0] if len(data['lst']) == 1 else self.list_verbs[1]),
                           'lst': self.lst(data, order, sub)}
                self.set_message('LIST_QUERY_MSG', options)

            elif len(data['lst']) == 0:
                self.set_message('LIST_NO_RESULT_MSG', {'sub': sub1, 'obj': obj1, 'ins': ins, 'prep': prep})

            else:
                self.set_message('NO_QUERY_MSG')

            self.session_reset()
            return

        return

    def describe_query(self, msg):
        slots = self.session['intent']['slots']
        ins = slots.get('ins')

        # level 0 slots verify
        if self.session['intent']['level'] == 0:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            if ins is None and len(msg) == 0:
                self.session['confirmation'] = False
                self.set_message('DESCRIBE_INSTANCE_MSG')
                return

            if (ins is not None) or (ins is None and len(msg) > 0):
                if ins is None:
                    self.session['intent']['slots']['ins'] = self.session['original_input']  # previously msg
                data = self.get_data('cmd=dsc&ins=', self.session['intent']['slots']['ins'])
                self.session['intent']['level'] = 1
                self.describe_query(data)
                return

        # ins verify
        if self.session['intent']['level'] == 1:

            # ok case
            if msg['result'] == 'ok':
                message_ins = ''
                self.session['intent']['slots']['results'] = msg
                self.session['intent']['level'] = 2

                if msg['obj_id'] == 1:
                    message_ins += self.upper_first(msg['item']['name'])
                elif msg['obj_id'] == 4:
                    message_ins += msg['item']['name']
                elif 1 < msg['obj_id'] < 4 and 'conference' in msg['item']['name'].lower():
                    message_ins += msg['item']['name']
                else:
                    message_ins += msg['item']['name'] + ' conference'

                if self.session['confirmation']:
                    self.set_message("DESCRIBE_CONFIRM_MSG", {'ins': message_ins})
                    return
                else:
                    self.describe_query('')
                    return

            # kk case - too many results
            if msg['result'] == 'kk':
                self.session['confirmation'] = False
                message = self.kk_message(msg, 0)
                self.set_message('DSC_TOO_GENERIC_MSG', {'ins': ins, 'results': message})
                self.session['intent']['level'] = 0
                del self.session['intent']['slots']['ins']
                return

            # ko case - no result
            if msg['result'] == 'ko':
                self.set_message('DSC_NO_RESULT_MSG', {'ins': ins})
                self.session['intent']['level'] = 0
                del self.session['intent']['slots']['ins']
                return

            # k2 case multiple results
            if msg['result'] == 'k2':
                self.session['confirmation'] = False
                msg['cmd'] = 'dsc'
                self.session['intent']['items_list'] = msg
                message = self.choice_list(msg)
                self.set_message('ITEM_MSG', {'ins': ins, 'msg': message})
                self.session['intent']['level'] = 3
                return

            # ka case homonyms
            if msg['result'] == 'ka':
                self.session['confirmation'] = False
                self.session['intent']['homonyms_list'] = msg
                message = self.homonyms(msg)
                self.set_message('HOMONYMS_MSG', {'msg': message})
                self.session['intent']['level'] = 4
                return

        # check, confirm and display of results
        if self.session['intent']['level'] == 2:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            if self.session['intent']['slots'].get('results') is not None:
                message = self.dsc(self.session['intent']['slots']['results'])
                self.append_message(message)
                self.session_reset()
                return

            else:
                self.set_message('NO_QUERY_MSG')
                self.session_reset()
                return

        # multiple result list management
        if self.session['intent']['level'] == 3:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            num = self.get_number(msg)
            if num is not None and num <= sum(self.session['intent']['items_list']['num']):
                ins = self.get_choice(self.session['intent']['items_list'], num)
                self.session['intent']['slots']['ins'] = ins['name']
                self.session['intent']['level'] = 0
                del self.session['intent']['items_list']
                self.describe_query('')
                return

            else:
                self.session['intent']['level'] = 1
                msg = self.session['intent']['items_list']
                del self.session['intent']['items_list']
                self.describe_query(msg)

        # homonyms list management
        if self.session['intent']['level'] == 4:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            num = self.get_number(msg)
            if num is not None and num <= len(self.session['intent']['homonyms_list']['item']) - 1:
                # noinspection PyTypeChecker
                idx = self.session['intent']['homonyms_list']['item'][num]['id']

                if self.session['intent']['homonyms_list']['obj_id'] == 4:
                    idx = '0000000000' + str(idx)
                del self.session['intent']['homonyms_list']
                data = self.get_data('cmd=dsc&ins=', idx)
                self.session['intent']['level'] = 1
                self.describe_query(data)
                return
            else:
                msg = self.session['intent']['homonyms_list']
                del self.session['intent']['homonyms_list']
                self.session['intent']['level'] = 1
                self.describe_query(msg)
                return

    def compare_query(self, msg):
        slots = self.session['intent']['slots']
        ins = slots.get('ins')
        ins2 = slots.get('ins2')
        term1 = slots.get('term1')

        # level 0 slots verify
        if self.session['intent']['level'] == 0:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            if ins is None and len(msg) == 0:
                self.session['confirmation'] = False
                self.set_message('COMPARE_FIRST_INSTANCE')
                return

            if ins is not None and term1 is not None and ins2 is None and len(msg) == 0:
                self.session['confirmation'] = False
                message_ins = '<b>'

                if term1['obj_id'] == 1:
                    message_ins += self.upper_first(term1['item']['name']) + '</b>'
                elif term1['obj_id'] == 4:
                    message_ins += term1['item']['name'] + '</b>'
                elif 1 < term1['obj_id'] < 4 and 'conference' not in term1['item']['name'].toLowerCase():
                    message_ins += term1['item']['name'] + '</b>'
                else:
                    message_ins += term1['item']['name'] + '</b> conference'
                params = {'obj': self.compare_categories[term1['obj_id'] - 1], 'ins': message_ins}
                self.set_message('COMPARE_SECOND_INSTANCE', params)
                return

            if (ins is not None and term1 is None) or (ins is None and len(msg) > 0):
                if ins is None:
                    self.session['intent']['slots']['ins'] = self.session['original_input']
                data = self.get_data('cmd=dsc&ins=', self.session['intent']['slots']['ins'])
                self.session['intent']['level'] = 1
                self.compare_query(data)
                return

            cond1 = ins is not None and term1 is not None and ins2 is not None
            cond2 = ins is not None and term1 is not None and ins2 is None and len(msg) > 0

            if cond1 or cond2:
                if ins2 is None:
                    self.session['intent']['slots']['ins2'] = self.session['original_input']
                data = self.get_data('cmd=dsc&ins=', self.session['intent']['slots']['ins2'])
                self.session['intent']['level'] = 10
                self.compare_query(data)
                return

        # level 1 ins verify
        if self.session['intent']['level'] == 1:

            # case ok
            if msg['result'] == 'ok':
                self.session['intent']['slots']['term1'] = msg
                self.session['intent']['level'] = 0
                self.compare_query('')
                return

            # case kk (too many results)
            if msg['result'] == 'kk':
                message = self.kk_message(msg, 0)
                self.session['confirmation'] = False
                self.set_message('COMPARE_TOO_GENERIC_FIRST_MSG', {'ins': ins, 'results': message})
                self.session['intent']['level'] = 0
                del self.session['intent']['slots']['ins']
                return

            # case ko (no result)
            if msg['result'] == 'ko':
                self.set_message('COMPARE_NO_RESULT_FIRST_MSG', {'ins': ins})
                self.session['confirmation'] = False
                self.session['intent']['level'] = 0
                del self.session['intent']['slots']['ins']
                return

            # case k2 (multiple result)
            if msg['result'] == 'k2':
                self.session['confirmation'] = False
                msg['cmd'] = 'dsc'
                self.session['intent']['items_list'] = msg
                message = self.choice_list(msg)
                self.set_message('ITEM_MSG', {'ins': ins, 'msg': message})
                self.session['intent']['level'] = 3
                return

            # ka case homonyms
            if msg['result'] == 'ka':
                self.session['confirmation'] = False
                self.session['intent']['homonyms_list'] = msg
                message = self.homonyms(msg)
                self.set_message('HOMONYMS_MSG', {'msg': message})
                self.session['intent']['level'] = 4
                return

        # multiple result list management
        if self.session['intent']['level'] == 3:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            num = self.get_number(msg)
            if num is not None and num <= sum(self.session['intent']['items_list']['num']):
                ins = self.get_choice(self.session['intent']['items_list'], num)
                self.session['intent']['slots']['ins'] = ins['name']
                self.session['intent']['level'] = 0
                del self.session['intent']['items_list']
                self.compare_query('')
                return

            else:
                self.session['intent']['level'] = 1
                msg = self.session['intent']['items_list']
                del self.session['intent']['items_list']
                self.compare_query(msg)

        # homonyms list management
        if self.session['intent']['level'] == 4:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            num = self.get_number(msg)
            if num is not None and num <= len(self.session['intent']['homonyms_list']['item']) - 1:
                # noinspection PyTypeChecker
                idx = self.session['intent']['homonyms_list']['item'][num]['id']
                if self.session['intent']['homonyms_list']['obj_id'] == 4:
                    idx = '0000000000' + str(idx)
                del self.session['intent']['homonyms_list']
                data = self.get_data('cmd=dsc&ins=', idx)
                self.session['intent']['level'] = 1
                self.compare_query(data)
                return
            else:
                msg = self.session['intent']['homonyms_list']
                del self.session['intent']['homonyms_list']
                self.session['intent']['level'] = 1
                self.compare_query(msg)
                return

        # level 10 ins2 verify
        if self.session['intent']['level'] == 10 and term1 is not None:

            # case ok
            if msg['result'] == 'ok':
                message_ins = '<b>'
                message_ins2 = '<b>'
                self.session['intent']['slots']['results'] = msg
                self.session['intent']['level'] = 20

                comb = str(term1['obj_id']) + '-' + str(msg['obj_id'])
                if comb not in self.compare_valid_combinations:
                    params = {'obj1': term1['object'], 'obj2': msg['object']}
                    self.set_message('COMPARE_WRONG_PAIR_MSG', params)
                    self.session_reset()
                    return

                if term1['item'] == msg['item']:
                    params = {'obj1': self.compare_categories[term1['obj_id'] - 1]}
                    self.set_message('COMPARE_SAME_OBJ_MSG', params)
                    self.session_reset()
                    return

                if term1['obj_id'] == 1:
                    message_ins += self.upper_first(term1['item']['name']) + '</b>'
                elif term1['obj_id'] == 4:
                    message_ins += term1['item']['name'] + '</b>'
                elif 1 < term1['obj_id'] < 4 and 'conference' in term1['item']['name'].lower():
                    message_ins += term1['item']['name'] + '</b>'
                else:
                    message_ins += term1['item']['name'] + '</b> conference'

                if msg['obj_id'] == 1:
                    message_ins2 += self.upper_first(msg['item']['name']) + '</b>'
                elif msg['obj_id'] == 4:
                    message_ins2 += msg['item']['name'] + '</b>'
                elif 1 < msg['obj_id'] < 4 and 'conference' in msg['item']['name'].lower():
                    message_ins2 += msg['item']['name'] + '</b>'
                else:
                    message_ins2 += msg['item']['name'] + '</b> conference'

                if self.session['confirmation']:
                    params = {'ins': message_ins, 'ins2': message_ins2}
                    self.set_message("COMPARE_CONFIRM_MSG", params)
                else:
                    self.compare_query('')

                return

            # case kk (too many results)
            if msg['result'] == 'kk':
                message = self.kk_message(msg, 0)
                self.session['confirmation'] = False
                self.set_message('COMPARE_TOO_GENERIC_SECOND_MSG', {'ins': ins2, 'results': message})
                self.session['intent']['level'] = 0
                del self.session['intent']['slots']['ins2']
                return

            # case ko (no result)
            if msg['result'] == 'ko':
                self.set_message('COMPARE_NO_RESULT_SECOND_MSG', {'ins': ins2})
                self.session['confirmation'] = False
                self.session['intent']['level'] = 0
                del self.session['intent']['slots']['ins2']
                return

            # case k2 (multiple result)
            if msg['result'] == 'k2':
                self.session['confirmation'] = False
                msg['cmd'] = 'dsc'
                self.session['intent']['items_list'] = msg
                message = self.choice_list(msg)
                self.set_message('ITEM_MSG', {'ins': ins2, 'msg': message})
                self.session['intent']['level'] = 30
                return

            # ka case homonyms
            if msg['result'] == 'ka':
                self.session['confirmation'] = False
                self.session['intent']['homonyms_list'] = msg
                message = self.homonyms(msg)
                self.set_message('HOMONYMS_MSG', {'msg': message})
                self.session['intent']['level'] = 40
                return

        # check, confirm and display of results
        if self.session['intent']['level'] == 20:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            if self.session['intent']['slots'].get('results') is not None:
                self.cmp(term1, self.session['intent']['slots']['results'])
                self.session_reset()
                return

            else:
                self.set_message('NO_QUERY_MSG')
                self.session_reset()
                return

        # multiple result list management
        if self.session['intent']['level'] == 30:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            num = self.get_number(msg)
            if num is not None and num <= sum(self.session['intent']['items_list']['num']):
                ins2 = self.get_choice(self.session['intent']['items_list'], num)
                self.session['intent']['slots']['ins2'] = ins2['name']
                self.session['intent']['level'] = 0
                del self.session['intent']['items_list']
                self.compare_query('')
                return

            else:
                self.session['intent']['level'] = 10
                msg = self.session['intent']['items_list']
                del self.session['intent']['items_list']
                self.compare_query(msg)

        # homonyms list management
        if self.session['intent']['level'] == 40:

            if msg in self.cancel_words:
                self.set_message('REPROMPT_MSG')
                self.session_reset()
                return

            num = self.get_number(msg)
            if num is not None and num <= len(self.session['intent']['homonyms_list']['item']) - 1:
                # noinspection PyTypeChecker
                idx = self.session['intent']['homonyms_list']['item'][num]['id']
                if self.session['intent']['homonyms_list']['obj_id'] == 4:
                    idx = '0000000000' + str(idx)
                del self.session['intent']['homonyms_list']
                data = self.get_data('cmd=dsc&ins=', idx)
                self.session['intent']['level'] = 10
                self.compare_query(data)
                return
            else:
                msg = self.session['intent']['homonyms_list']
                del self.session['intent']['homonyms_list']
                self.session['intent']['level'] = 10
                self.compare_query(msg)
                return

    def cycle(self, user_input):
        if len(user_input) == 0:
            return
        msg = user_input
        for i in range(len(self.marks_list)):
            msg = msg.replace(self.marks_list[i], '')
        self.session['original_input'] = user_input
        msg = msg.lower()
        # verification of intent
        if self.session['level'] == 0:
            self.intent_verify(msg)
            return
        # transfers control to complex intents depending on the intent name
        if self.session['level'] == 1:
            intent = self.get_intent(msg)[0]

            if intent != 'fallback':
                self.session['level'] = 0
                self.session['confirmation'] = True
                if self.session['intent'].get('level') is not None:
                    self.session['intent']['level'] = 0
                if self.session['intent'].get('homonyms_list') is not None:
                    del self.session['intent']['homonyms_list']
                if self.session['intent'].get('items_list') is not None:
                    del self.session['intent']['items_list']
                self.intent_verify(msg)
                return
            if self.session['intent']['name'] == 'count':
                self.count_query(msg)
                return
            elif self.session['intent']['name'] == 'list':
                self.list_query(msg)
                return
            elif self.session['intent']['name'] == 'describe':
                self.describe_query(msg)
                return
            elif self.session['intent']['name'] == 'compare':
                self.compare_query(msg)
                return

    def question(self, user_input):
        self.cycle(user_input)
        answer = self.session['answer']
        for i in range(len(self.tags_list)):
            answer = answer.replace(self.tags_list[i], '')
        return answer, self.session['answer']


def main():
    data_server_url = 'http://aidabot.ddns.net/api?pass=123abc&'
    bot = AidaBot(data_server_url)

    user_input = ''
    while user_input != 'bye':
        user_input = input('User... ')
        answer, _ = bot.question(user_input)
        print('AIDA-Bot... ' + answer)


if __name__ == '__main__':
    main()
