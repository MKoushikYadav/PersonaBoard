from pyairtable import Api
api = Api('patEbpe81GWzbuUym.130c8078b8074c326b00889b9c446db184827be3988ae41fd1ab4192c37f63f9')
table = api.table('appBxWO4y4RQpAe36', 'apt_qs')
# print(table.all())
questions = []
import random
records = table.all()
random_records = random.sample(records, 5)
for record in random_records:
	record = record['fields']
	record.pop('cat')
	questions.append(record)
# print(questions)

table = api.table('appBxWO4y4RQpAe36', 'eq_qs')
records = table.all()
random_records = random.sample(records, 5)
for record in random_records:
	record = record['fields']
	questions.append(record)
# print(questions)

table = api.table('appBxWO4y4RQpAe36', 'ws_qs')
records = table.all()
random_records = random.sample(records, 5)
for record in random_records:
	record = record['fields']
	questions.append(record)
print(questions)
interests = []
table = api.table('appBxWO4y4RQpAe36', 'interests')
# global interests
interests_records = table.all()
for record in interests_records:
	record = record['fields']
	interests.append(record['name'])
print(interests)