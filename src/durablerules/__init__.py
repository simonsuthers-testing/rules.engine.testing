#from durable.lang import ruleset, post, when_all, m, c, assert_fact, post_batch, count
from durable.lang import *
import pandas as pd
import json

# see https://pypi.org/project/durable-rules/
# https://github.com/jruizgit/rules/blob/master/docs/py/reference.md

#############################################################################################################

'''
post('risk', {'ID': 1, 'ISIN': 'IS0001', 'Date': '2022-07-06T00:00:00.000Z', 'Price': 100})
post('risk', {'ID': 2, 'ISIN': 'IS0001', 'Date': '2022-07-07T00:00:00.000Z', 'Price': 150})
post('risk', {'ID': 3, 'ISIN': 'IS0001', 'Date': '2022-07-08T00:00:00.000Z', 'Price': 200})
post('risk', {'ID': 4, 'ISIN': 'IS0002', 'Date': '2022-07-06T00:00:00.000Z', 'Price': 100})
post('risk', {'ID': 5, 'ISIN': 'IS0002', 'Date': '2022-07-07T00:00:00.000Z', 'Price': 150})
post('risk', {'ID': 6, 'ISIN': 'IS0002', 'Date': '2022-07-08T00:00:00.000Z', 'Price': 200000})
post('risk', {'ID': 7, 'ISIN': 'IS0003', 'Date': '2022-07-06T00:00:00.000Z', 'Price': 3000})
post('risk', {'ID': 8, 'ISIN': 'IS0003', 'Date': '2022-07-07T00:00:00.000Z', 'Price': 4000})
post('risk', {'ID': 9, 'ISIN': 'IS0003', 'Date': '2022-07-07T00:00:00.000Z', 'Price': 4000})
'''

#############################################################################################################
# import testing workbook
df = pd.read_excel("durablerules\\durable_rules_test.xlsx")
dict = json.loads(df.to_json(orient='records', date_format="iso"))
print(dict)

#############################################################################################################
# basic test using testing workbook
with ruleset("test"):
    # antecedent
    @when_all(m.Price > 0)
    def say_hello(c):
        print(f"Basic rule: ISIN is {c.m.ISIN}")

for record in dict:
    post("test", record)

#############################################################################################################
# events test using example
with ruleset('risk'):
    @when_all(c.first << m.Price > 50,
              c.second << m.ISIN == c.first.ISIN, 
              c.second << m.Price > c.first.Price * 2)
    # the event pair will only be observed once
    def fraud(c):
        print('Fraud detected -> {0}, {1}'.format(c.first.ID, c.second.ID))

for record in dict:
    post("risk", record)

#############################################################################################################
# Arrays
# Don't know what this is doing: If change Price to 4000 it fails

with ruleset('array'):
    # matching object array
    @when_all(m.payments.allItems((item.Price < 250) | (item.Price >= 3000)))
    def rule2(c):
        print('fraud 2 detected {0}'.format(c.m.payments))
     
post('array', {'payments': dict})


#############################################################################################################
# batching

with ruleset('expense'):
    # this rule will trigger as soon as three events match the condition
    @when_all(count(3), m.Price > 100)
    def approve(c):
        print('approved {0}'.format(c.m))

    # this rule will be triggered when 'expense' is asserted batching at most two results       
    @when_all(cap(2),
              c.expense << m.Price >= 100,
              c.approval << m.review == True)
    def reject(c):
        print('rejected {0}'.format(c.m))

post_batch('expense', dict)
assert_fact('expense', { 'review': True })

#############################################################################################################

# with ruleset("animal"):
#     @when_all((m.thing == "can") & (m.activity == "fly"))
#     def bird(c):
#         c.assert_fact({"subject": c.m.subject, "thing": "is", "activity": "bird"})

#     @when_all(+m.subject)
#     def output(c):
#         print('Fact: {0} {1} {2}'.format(c.m.subject, c.m.thing, c.m.activity))

# assert_fact("animal", {"subject": "kermit", "thing": "can", "activity": "fly"})




# test for duplicate
