from flask import Flask, render_template, jsonify, request, redirect
import openai
from tweety import Twitter
import random, ast
from pyairtable.formulas import match
from pyairtable import Api
api = Api('patEbpe81GWzbuUym.130c8078b8074c326b00889b9c446db184827be3988ae41fd1ab4192c37f63f9')
app = Flask(__name__)
c = 1
emailid = ""
name = ""
questions = []
interests = []
user_interests = []
results = []
l = 0
def get_data():
    global questions
    table = api.table('appBxWO4y4RQpAe36', 'apt_qs')
    records = table.all()
    random_records = random.sample(records, 5)
    for record in random_records:
        record = record['fields']
        record.pop('cat')
        questions.append(record)
    
    table = api.table('appBxWO4y4RQpAe36', 'eq_qs')
    records = table.all()
    random_records = random.sample(records, 5)
    for record in random_records:
        record = record['fields']
        questions.append(record)
    
    table = api.table('appBxWO4y4RQpAe36', 'ws_qs')
    records = table.all()
    random_records = random.sample(records, 5)
    for record in random_records:
        record = record['fields']
        questions.append(record)

    table = api.table('appBxWO4y4RQpAe36', 'interests')
    global interests
    interests_records = table.all()
    for record in interests_records:
        record = record['fields']
        interests.append(record['name'])
    
    global l
    l = len(interests)

def get_candidates():
    table = api.table('appBxWO4y4RQpAe36', 'candidate_results')
    return table.all()

def get_social_media_analytics(handle):
    app=Twitter('megathon')
    username='koushik15024'
    password='Roopa.18'
    app.sign_in(username=username, password=password)
    usertweets= app.get_tweets(username=handle,pages=1)
    a=('\n').join([tweet.text for tweet in usertweets.tweets])
    openai.api_key = "${{ secrets.OPENAI_APIKEY }}"

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role":"user","content":'Your task is to determine the person\'s personality and qualities by analyzing their tweets. You need to strictly get not more than 5 qualities.Here are some strict instructions you must follow: 1. Each Positive/Negative quality about the person must not be more than 4 words. 2. Avoid duplicate topics. 3. THE FORMAT OF YOUR OUTPUT MUST STRICTLY CONTAIN ONLY THE LIST OF COMMA SEPARATED POSITIVE TOPICS FOLLOWED BY NEGATIVE TOPICS. 4. ENSURE THAT NOT EVEN A SINGLE OTHER WORD i.e, NO UN-NECESSARY CHARACTERS(ASTERISKS, HYPHENS, etc) OR EXPLANATIONS ARE INCLUDED. 5.Incase negative topics arent available,END THE RESPONSE . 6.You need to provide ONLY 3-5 qualities about the person.  \nHere is the data: \n'+ a}])
    return completion.choices[0].message.content

@app.route('/start', methods=['GET'])
def start():
    global c
    c=1
    get_data()
    return render_template('start.html')

@app.route('/test', methods=['GET','POST'])
def test():
    if request.method == 'POST':
        global emailid
        emailid= request.form['emailid']
        global name
        name= request.form['name']
    return render_template('test.html', c = c, questions = questions, interests = interests, l = l, emailid = emailid, name = name)

@app.route('/recruiter', methods=['GET'])
def recruiter():
    candidates = get_candidates()
    final_candidates = []
    for candidate in candidates:
        final_candidates.append(candidate['fields'])
    return render_template('recruiter.html', candidates = final_candidates)

@app.route('/report', methods=['POST'])
def get_report():
    if request.method == 'POST':
        global emailid
        emailid= request.form['emailid']

    table = api.table('appBxWO4y4RQpAe36', 'candidate_results')
    formula = match({"emailid": emailid})
    candidate = table.first(formula=formula)['fields']
    # print(candidate)
    name = candidate['name']
    apt_score = candidate['apt_score']
    eq_score = candidate['eq_score']
    ws_data = ast.literal_eval(candidate['ws_data'])
    user_interests = ast.literal_eval(candidate['interests'])

    topics = []
    userlist=['koushik15024','BegumpetBalu','Srikar212232542']
    handle = random.choice(userlist)
    # get social media analytics
    x=get_social_media_analytics(handle)
    topics = x.split(',')
    return render_template('result.html', emailid = emailid, name = name, apt_score = apt_score, eq_score = eq_score, ws_data = ws_data, interests = user_interests, topics = topics)

@app.route('/result', methods=['POST'])
def result():
    global questions
    global results
    # print(questions)
    for i in range(1,11):
        if int(questions[i-1]['user_ans']) == int(questions[i-1]['ans']):
            results.append({'id':questions[i-1]['id'], 'result':1})
        else:
            results.append({'id':questions[i-1]['id'], 'result':0})
    for i in range(11,16):
        results.append({'q':questions[i-1]['q'], 'result':questions[i-1]['user_ans']})
    global user_interests
    user_interests = request.form.getlist('interests')
    # print(user_interests)
    # print(results)
    apt_score = 0
    eq_score = 0
    ws_data = []
    for i in range(0, 5):
        apt_score += int(results[i]['result'])
    for i in range(5, 10):
        eq_score += int(results[i]['result'])
    for i in range(10, 15):
        ws_data.append(results[i])
    # upload results, interests into db
    submit_data(emailid, name, apt_score, eq_score, ws_data, user_interests)
    
    topics = []
    userlist=['koushik15024','BegumpetBalu','Srikar212232542']
    handle = random.choice(userlist)
    # get social media analytics
    x=get_social_media_analytics(handle)
    topics = x.split(',')
    return render_template('result.html', emailid = emailid, name = name, apt_score = apt_score, eq_score = eq_score, ws_data = ws_data, interests = user_interests, topics = topics)

def submit_data(emailid, name, apt_score, eq_score, ws_data, interests):
    # Set the URL for the Airtable API endpoint
    table = api.table('appBxWO4y4RQpAe36','candidate_results')
    # Define the JSON data to send in the request
    data = {
        "emailid": emailid,
        "name": name,
        "apt_score": int(apt_score),
        "eq_score": int(eq_score),
        "ws_data": str(ws_data),
        "interests": str(interests)
    }
    table.create(data)

    return 'Data submitted successfully'

@app.route('/back', methods=['POST'])
def back():
    global c
    c -= 1
    return redirect('/test')

@app.route('/next', methods=['POST'])
def next():
    global questions
    global c
    if c < 16:
        ans = request.form['ans']
        if not ans:
            questions[c-1]['user_ans']= 0
        else:     
            questions[c-1]['user_ans'] =  ans
    c += 1
    return redirect('/test')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
