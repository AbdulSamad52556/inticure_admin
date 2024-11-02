import shutil
import time
from flask import Flask
from flask import redirect,url_for,render_template, request, flash,session,jsonify,send_file,send_from_directory
import json, requests
from datetime import datetime,date
from werkzeug.utils import secure_filename
import os, math
from urllib.parse import urlparse
from pathlib import Path
# import pandas as pd
# from bs4 import BeautifulSoup

app = Flask(__name__)

admin_webapp_url = "admin.inticure.com"

base_url="https://api.inticure.online/"

# api urls
admin_login_api="api/administrator/sign_in"
category_api="api/analysis/category"
create_category_api="api/analysis/create_category"
# api for edit and delete categories
category_viewset="api/analysis/category_viewset/"
answer_type_api="api/analysis/answer_type"
questionnaire_api="api/analysis/questionnaire"
add_question_api = "api/administrator/create_questions"
update_question_api="api/administrator/update_questions"
update_option_api="api/administrator/update_option"
delete_option_api = "api/administrator/remove_option"
delete_question_api="api/administrator/remove_question"
appointment_list_api="api/doctor/appointment_list"
appointment_detail_api="api/doctor/appointment_detail"
observations_api="api/doctor/observations"
reschedule_api="api/doctor/appointment_schedule"
prescription_api="api/doctor/prescriptions"
language_api="api/administrator/languages_viewset"
specialization_list_api="api/doctor/specialization_list"
doctor_listing_api="api/administrator/doc_list"
add_doctor_api="api/administrator/doc_create"
doctor_update_api="api/administrator/doctor_profile_edit"
file_upload_api="api/doctor/common_file/"
doctor_profile_api="api/doctor/doctor_profile"
doctor_admin_approval_api="/api/administrator/application_action"
customer_listing_api="api/customer/customer_crud"
customer_profile_api="api/customer/customer_profile"
specialization_list_api="api/doctor/specialization_list"
locations_api="api/administrator/locations_viewset"
invoice_detail_api="api/analysis/invoice_detail"
invoice_list_api="api/analysis/invoice_list"
transaction_list_api="api/administrator/transaction_list"
transaction_details_api="api/administrator/transaction_detail"
plans_api="api/administrator/plans_viewset"
payout_list_api="api/administrator/payout_list"
payout_details_api="api/administrator/payout_detail"
payout_approval_api="api/administrator/doctor_earnings"
inticure_earnings_api="api/administrator/inticure_earnings"
logout_api="api/administrator/logout"
refund_api_fullreq='f{base_url}api/administrator/refund/?date_from=2023-03-15&date_to=2023-03-29&limit=5&refund_id=2023-03-16-0008&status=0'
refund_api="/api/administrator/refund/"
admin_dashboard_api="/api/administrator/dashboard"
doctors_api = "/api/doctor/doctor_list"
get_plan = "/api/administrator/get-plan"
edit_plan_api = "/api/administrator/edit-plan"
remove_plan_api = "/api/administrator/remove-plan"
app.config["SECRET_KEY"]='fd4ceef3e778a8588dc1d31cdd30f163d4b305e11a2733e938b70c94b83a2be9'
doctor_time_slots='/api/doctor/doctor_time_slots'

#doctor_flag=3

# """"""" BASE DIRECTORY """"""""
BASE_DIR = Path(__file__).resolve().parent

# Template filters
@app.template_filter()
def date_format(date_string):
    date_object=datetime.strptime(date_string,f'%Y-%m-%d')
    formatted_string = date_object.strftime('%d %b %Y')
    return formatted_string

@app.template_filter()
def time_format(value):
    # dtm_obj = datetime.strptime(timing, f'%Y-%m-%dT%H:%M:%S.%f%z')
    # date_object1=datetime.strptime(value,f'%H:%M:%S.%f%z')
    date_object=datetime.strptime(value,f'%H:%M:%S.%f')
    formatted_string = date_object.strftime('%I:%M %p')
    return formatted_string

# this filter is for splitting time slot to the first value (Eg 10AM - 11AM to 10AM)
@app.template_filter()
def time_slot_format(value):
    time_strip=value.split("-")
    time=str(time_strip[0])
    return time

@app.route("/",methods=['GET','POST'])
def admin_login():
    session.clear()
    admin_login_api="api/administrator/sign_in"
    headers={
        "Content-Type":"application/json"
    }
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        data={
            "username":username,
            "password":password,
            "login_flag":"admin"
        }
        print('jdshfakjsdfhkasjdhfkajsdhf',username)
        api_data=json.dumps(data)
        
        try:
            admin_login_response=requests.post(base_url+admin_login_api,data=api_data,headers=headers)
            print(admin_login_response.status_code)
            admin_login=json.loads(admin_login_response.text)
            print(admin_login)
            #storing doctor flag key from login response in doctor flag variable
            doctor_flag=admin_login['doctor_flag']
        except:
            return redirect(url_for("admin_login")) 
        #storing doctor flag variable as doctor flag key in session
        session['doctor_flag']=doctor_flag
        print("doc",doctor_flag)
        #storing user id in session 
        admin_user_id=admin_login['user_id']
        session['admin_user_id']=admin_user_id
        print("admin user id",admin_user_id)

        if admin_login_response.status_code == 200:
            return redirect(url_for("dashboard",country=1))
        else:
            return redirect(url_for("admin_login"))
            # flash("Error please try again")
    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    try:
        headers = {
            "Content-Type":"application/json"
        }
        if 'admin_user_id' in session:
            user_id=session['admin_user_id']
            print(user_id)
        else:
            return redirect(url_for('admin_login'))
        payload={
            "user_id":user_id
        }
        api_data=json.dumps(payload)
        logout_request=requests.post(base_url+logout_api, data=api_data, headers=headers)
        logout_response=json.loads(logout_request.text)
        print(logout_response)
        session.clear()
        print("session cleared")
        return redirect(url_for('admin_login'))
    except Exception as e:
        print(e)
    return redirect(url_for('admin_login'))

# function
def appointment_listing(api_data):
    print(api_data)
    headers = {
        "Content-Type":"application/json"
    }
    print(headers)
    appointment_response=requests.post(base_url+appointment_list_api,data=api_data,headers=headers)
    print(base_url+appointment_list_api)
    print('appointment list api status code',appointment_response.status_code)
    appointment_data=json.loads(appointment_response.text)
    all_appointments=appointment_data['data']
    return all_appointments

@app.route("/dashboard/<int:country>")
def dashboard(country):
    try:
        if 'user_id' in session:
            doctor_id=session['user_id']
            print(doctor_id)
        # else:
        #     return redirect(url_for('admin_login'))
        if 'doctor_flag' in session:
            doctor_flag=session['doctor_flag']
            print(doctor_flag)
        if country == 1:
            currency = "inr"
        else:
            currency = "usd"
        headers = {
            "Content-Type":"application/json"
        }
        #dashboard api call
        dash_payload={
            "appointment_status":[2,8,12],
            "location":country
        }
        dash_json=json.dumps(dash_payload)
        print(dash_json)
        dashboard_request=requests.post(base_url+admin_dashboard_api,data=dash_json,headers=headers)
        print("dashboard code:",dashboard_request.status_code)
        dashboard_response=json.loads(dashboard_request.text)
        # dashboard_data=dashboard_response['data']
        # print(dashboard_data)
        # print(dashboard_response['doctors_count'])
        all_upcoming_orders = dashboard_response['data']
        if all_upcoming_orders:
            # if all_upcoming_orders['appointment_id']:
            upcoming_orders=all_upcoming_orders[0:10]
        else:
            upcoming_orders=[]

        #calling inticure earnings api
        ie_payload={
            "currency":currency
        }
        payout_json_data=json.dumps(ie_payload)
        print(payout_json_data)
        inticure_earnings_req=requests.post(base_url+inticure_earnings_api,data=payout_json_data,headers=headers)
        print("Inticure earnings api:",inticure_earnings_req.status_code)
        inticure_earnings_resp=json.loads(inticure_earnings_req.text)
        inticure_earnings=inticure_earnings_resp['data']
        print(inticure_earnings)
        

        if 'doctor_flag' in session:
            doctor_flag=session['doctor_flag']
            print(doctor_flag)

        headers = {
        "Content-Type":"application/json"
        }
        
        appointment_status=""
        specialization=""
        location=""

        payload={
                "appointment_status" : [1,2],
                "doctor_flag":"",
                "user_id":""
                # "specialization":specialization,
                # "location":location, 
            }
        api_data=json.dumps(payload)
        print(api_data)
        #header not passed as it caused error
        appointment_response=requests.post(base_url+appointment_list_api,data=api_data,headers=headers)
        print('appointment api status code',appointment_response.status_code)
        appointment_data=json.loads(appointment_response.text)
        appointment_list=appointment_data['data']

        # earnings api call
        payout_payload={
            "doctor_id":"",
            "payout_status":""
        }
        payout_json_data=json.dumps(payout_payload)
        payout_request=requests.post(base_url+payout_list_api, data=payout_json_data, headers=headers)
        print("payout",payout_request.status_code)
        payout_response=json.loads(payout_request.text)
        payouts=payout_response['data']
        # print("payouts",payouts)
        # print("error")
        payout_data=payouts['payouts']
        # print("payouts list",payout_data)
        return render_template('admin_dashboard.html',upcoming_orders=upcoming_orders,earnings=inticure_earnings,
         payouts=payouts,dash=dashboard_response)
        # return render_template('dashboard.html')
    except Exception as e:
        print(e)
        return render_template('dashboard.html')

@app.route("/answer_types")
def answer_types():
    headers = {
            "Content-Type":"application/json"
        }
    payload={
         "operation_flag":"view",
         "answer_type":"" 
        # operation_flag="add"/"view","answer_type":"radio"/etc
    }
    api_data=json.dumps(payload)
    answer_type_req=requests.post(base_url+answer_type_api, data=api_data, headers=headers)
    print("answer types api:",answer_type_req.status_code)
    answer_type_resp=json.loads(answer_type_req.text)
    # print(answer_type_resp)
    answer_types=answer_type_resp['data']
    return render_template('answer_types.html',answer_types=answer_types)

@app.route("/add_answer_types",methods=['GET','POST'])
def add_answer_type():
    headers = {
            "Content-Type":"application/json"
        }
    if request.method == 'POST':
        answer_type=request.form['answer_type']
        payload={
            "operation_flag":"add",
            "answer_type":answer_type 
            # operation_flag="add"/"view","answer_type":"radio"/etc
        }
        api_data=json.dumps(payload)
        answer_type_req=requests.post(base_url+answer_type_api, data=api_data, headers=headers)
        print("add answer type api:",answer_type_req.status_code)
        answer_type_resp=json.loads(answer_type_req.text)
        print(answer_type_resp)
    return render_template('add_answer_type.html')

@app.route("/categories")
def categories():
    headers = {
            "Content-Type":"application/json"
        }
    category_req=requests.post(base_url+category_api,headers=headers)
    print("category api:",category_req.status_code)
    category_resp=json.loads(category_req.text)
    print(category_resp)
    categories=category_resp['data']
    return render_template('categories.html',categories=categories)

@app.route("/add_category",methods=['GET','POST'])
def add_category():
    headers = {
            "Content-Type":"application/json"
        }
    if request.method == 'POST':
        title=request.form['title']
        description=request.form['description']
        payload={
            "title":title,
            "description":description,
            
        }
        api_data=json.dumps(payload)
        print(api_data)
        add_category_req=requests.post(base_url+create_category_api,data=api_data,headers=headers)
        print(add_category_req.status_code)
        add_category_resp=json.loads(add_category_req.text)
        if add_category_resp['response_code']==200:
            flash("Category added","success")
        else:
            flash("Something went wrong","error")
        return redirect(url_for('categories'))        
    return render_template('add_category.html')

@app.route("/edit_category/<int:category_id>",methods=['GET','POST'])
def edit_category(category_id):
    try:
        print(category_id)
        headers = {
                "Content-Type":"application/json"
            }
        # category list api call
        category_req=requests.post(base_url+category_api,headers=headers)
        print("category api:",category_req.status_code)
        category_resp=json.loads(category_req.text)
        print(category_resp)
        categories=category_resp['data']

        for cat in categories:
            if category_id == cat['id']:
                edit_cat={
                "title" : cat['title'],
                "description" : cat['description']
                }
        # if request is given edit api call
        if request.method == 'POST':
            title=request.form['title']
            description=request.form['description']
            payload={
                "title":title,
                "description":description,                
            }
            api_data=json.dumps(payload)
            print(api_data)
            edit_category_req=requests.patch(base_url+category_viewset+f'{category_id}/',data=api_data,headers=headers)
            print(edit_category_req.status_code)
            edit_category_resp=json.loads(edit_category_req.text)
            if edit_category_resp['response_code']==200:
                flash("Category updated","success")
            else:
                flash("Something went wrong","error")
            return redirect(url_for('categories'))        
        return render_template('edit_category.html', edit_cat=edit_cat)
    except Exception as e:
        print(e)
        flash("Something went wrong","error")
        return redirect(url_for('categories'))

@app.route("/remove_category/<int:category_id>", methods=['GET','POST'])
def remove_category(category_id):
    print(category_id)
    headers={
        "Content-Type":"application/json"
        }
    # delete_specialization_api=specialization_list_api+f'/{spec_id}/'
    #delete plan api call (plan list api with delete method)
    remove_request=requests.delete(base_url+category_viewset+f'{category_id}/', headers=headers)
    remove_response=json.loads(remove_request.text)
    print("delete category api",remove_request.status_code)
    print(remove_response)
    if remove_response['response_code']==200:
        flash("Category deleted","success")
    else:
        flash("something went wrong","error")
    return redirect(url_for('categories'))

@app.route("/admin/questions")
def questions():
    try:
        questionnaire_api="api/analysis/questionnaire"
        questionnaire_response=requests.get(base_url+questionnaire_api)
        print('questionnaire api status code',questionnaire_response.status_code)
        questionnaire_data=json.loads(questionnaire_response.text)
        questionnaire_list=questionnaire_data['data']
        # print(questionnaire_list)
        return render_template("question_list.html",questionnaire_list=questionnaire_list)
    except Exception as e:
        print(e)
        return render_template("questions.html")

@app.route("/admin/addquestion", methods=['GET','POST'])
def add_question():
    
        add_question_api = "api/administrator/create_questions"
        headers={
            "Content-Type":"application/json"
        }

        # category api call
        category_req=requests.post(base_url+category_api,headers=headers)
        print("category api:",category_req.status_code)
        category_resp=json.loads(category_req.text)
        print(category_resp)
        categories=category_resp['data']

        if request.method == 'POST':
            question = request.form['question']
            answer_type = request.form['answer_type']
            category_id = request.form['category_id']
            option_count=request.form['count']
            gender=request.form['gender']
            option_list=[]
            option_dict={}
            # * Here Dynamic Elements Value Is Fetched By for Loop *
            # * Count Is The Number of Options Present *
            for count in range(1,int(option_count)+1):
                print("option",count)
                option = request.form[f'option{count}']
                option_list.append(option)
            # option = request.form['option']
            # option2 = request.form['option2']
            payload={
                "question": question,
                "answer_type": answer_type,
                "category_id": category_id,
                "options": option_list,
                "customer_gender":gender
            }
            api_payload = json.dumps(payload)
            print(api_payload)
            add_question = requests.post(base_url+add_question_api,data=api_payload,headers=headers)
            add_question_response = json.loads(add_question.text)
            print("add question api status code",add_question.status_code)
            print(add_question_response)
            return redirect(url_for('questions'))
    
        return render_template("add_question.html",categories=categories)

@app.route("/admin/editquestion/<int:id_to_be_updated>", methods=['GET','POST'])
def edit_question(id_to_be_updated):
    print(id_to_be_updated)
    #api
    questionnaire_api="api/analysis/questionnaire"
    update_question_api="api/administrator/update_questions"
    update_option_api="api/administrator/update_option"

    headers={
            "Content-Type":"application/json"
        }

    # category api call
    category_req=requests.post(base_url+category_api,headers=headers)
    print("category api:",category_req.status_code)
    category_resp=json.loads(category_req.text)
    print(category_resp)
    categories=category_resp['data']    

    questionnaire_response=requests.get(base_url+questionnaire_api)
    print('questionnaire api status code',questionnaire_response.status_code)
    questionnaire_data=json.loads(questionnaire_response.text)
    questionnaire_list=questionnaire_data['data']
    for question in questionnaire_list:
        if id_to_be_updated == question['id']:
            print(f"{id_to_be_updated} == {question['id']}")
            existing_values = {
                "question": question['question'],
                "answer_type": question['answer_type'],
                "category_id" : question['category_id'],
                "question_id": question['id'],
                "option":question["options"]
            }
            print(existing_values)
            #taking single option from option list as choice
            for choice in question['options']:
                option_id=choice['id']
                # print("option id :",option_id)
            if request.method == 'POST':
                print("post")
                question = request.form['question']
                answer_type = request.form['answer_type']
                gender=request.form['gender']
                category_id = request.form['category_id']
                if 'count' in request.form:
                    option_count=request.form['count']
                    # option = request.form['option']
                    # option2 = request.form['option2']
                    option_list=[]
                    option_dict={}
                    # * Here Dynamic Elements Value Is Fetched By for Loop *
                    # * Count Is The Number of Options Present *
                    if int(option_count) >= 1:
                        print("count",option_count)
                        for count in range(1,int(option_count)+1):
                            print("option",count)
                            option = request.form[f'option{count}']
                            option_list.append(option)
                            # print(option_list)
                else:
                    option_list = ""

                payload={
                    "question": question,
                    "answer_type": answer_type,
                    "category_id": category_id,
                    "question_id": id_to_be_updated,
                    "customer_gender":gender,
                    "option": option_list,
                }
                api_payload = json.dumps(payload)
                print(api_payload)
                update_question = requests.post(base_url+update_question_api,data=api_payload,headers=headers)
                update_question_response = json.loads(update_question.text)
                print("update question api status code",update_question.status_code)
                print(update_question_response)
            
                # payload2={
                #         "option_id": option_id,
                #         "question_id": id_to_be_updated,
                #         "option": option
                #     }
                
                
                # api_payload2=json.dumps(payload2)
                # print(api_payload2)
                # update_option = requests.post(base_url+update_option_api,data=api_payload2,headers=headers)
                # update_option_response=json.loads(update_option.text)
                # print(update_option_response)
                # print(update_option.status_code)
                return redirect(url_for('questions'))
            return render_template("edit_question.html",question=question,choice=choice,
            id_to_be_updated=id_to_be_updated,categories=categories)

@app.route("/editoption/<int:option_id>",methods=['GET','POST'])
def edit_option(option_id):
    # edit option is done through javascript
    # go to edit_question.html for js code
    print(option_id)
    questionnaire_api="api/analysis/questionnaire"
    update_option_api="api/administrator/update_option"
    headers={
            "Content-Type":"application/json"
        }
    data={}
    # if request.method == 'POST'
    # data=request.get_data('data')
    # print(data)
    print(request.get_data())
    # data['option_id'] = request.get_data('option_id')
    # print('optionID',data['option_id'])
    data['question_id'] = request.get_data('question_id')
    data['option']=request.get_data('option')
    print("option",data['option'])
    
    # data=request.get_data('data')
    # option=request.get_data('option')
    # question_id = request.get_data('question_id')
    # payload={
    #     "option_id": option_id,
    #     "question_id": question_id,
    #     "option": option
    # }
    print("data",data)
    # print(payload)

    # edit_option=requests.post(base_url+update_option_api,data=data,headers=headers)
    # edit_option_response=json.loads(edit_option.text)
    # print(edit_option_response)

    # * CALLING QUESTIONAIRE API *
    questionnaire_response=requests.get(base_url+questionnaire_api)
    print('questionnaire api status code',questionnaire_response.status_code)
    questionnaire_data=json.loads(questionnaire_response.text)
    questionnaire_list=questionnaire_data['data']
    for question in questionnaire_list:
        for choice in question['options']:
            if option_id==choice['id']:
                print("option id :",option_id)
                question_id = choice['question_id']
    return redirect(url_for('edit_question',id_to_be_updated=question_id))

@app.route("/deleteoption/<int:option_id>")
def delete_option(option_id):
    print(option_id)
    delete_option_api = "api/administrator/remove_option"
    questionnaire_api="api/analysis/questionnaire"
    headers={
            "Content-Type":"application/json"
        }
    questionnaire_response=requests.get(base_url+questionnaire_api)
    print('questionnaire api status code',questionnaire_response.status_code)
    questionnaire_data=json.loads(questionnaire_response.text)
    questionnaire_list=questionnaire_data['data']
    for question in questionnaire_list:
        for choice in question['options']:
            if option_id==choice['id']:
                print("option id :",option_id)
                question_id = choice['question_id']
    data={
        "option_id" : option_id
    }
    api_data=json.dumps(data)
    print(api_data)
    delete_option = requests.post(base_url+delete_option_api,data=api_data,headers=headers)
    delete_option_response = json.loads(delete_option.text)
    print(delete_option_response)
    return redirect(url_for('edit_question',id_to_be_updated=question_id))

@app.route("/admin/deletequestion/<int:id_to_delete>")
def delete_question(id_to_delete):
    
    delete_question_api="api/administrator/remove_question"
    headers={
        "Content-Type":"application/json"
    }
    print(id_to_delete)
    data={
        "question_id":id_to_delete
    }
    api_data=json.dumps(data)
    print(api_data)
    delete_question=requests.post(base_url+delete_question_api,data=api_data,headers=headers)
    print(delete_question.text)
    delete_question_response=json.loads(delete_question.text)
    print(delete_question.status_code)
    print(delete_question_response)

    return redirect(url_for("questions"))

@app.route('/user_download/<int:doctor_id>')
def user_download(doctor_id):
    try:
        print(request.args)
        file_path=request.args.get('file_path')
        print(file_path)
        print("download")
        print(file_path)
        print(doctor_id)
        url=file_path


        if file_path:  # Check if file path is provided
            print('get')
            try:
                return send_file(file_path, as_attachment=True)
            except FileNotFoundError:
                print('post')
                return 'File not found.', 404  # Handle file not found error
        else:
            return 'Missing file path parameter.', 400  # Handle missing file path error

        # url="http://"+file_path 
        # print(url)
        # r = requests.get(url)
        # # r = requests.get(url)
        # # this removes http and website part from url
        # url_split_1 = urlparse(url)
        # print(url_split_1)
        # #this will split rest of the path from file name
        # file_name=os.path.basename(url_split_1.path)
        # print("filename",file_name)

        # # cwd = os.getcwd()+'/'
        # # print(cwd)
        # # if 'temp' not in os.listdir(cwd):
        # # os.mkdir(cwd + 'temp')
        # # #saving file in flask app
        # # file_temp_save=open(cwd + 'temp/'+ file_name, "wb").write(r.content)
        # # print("saved in temp")

        # print("Base dir: ", BASE_DIR)
        # if 'temp' not in os.listdir(BASE_DIR):
        #     os.mkdir(str(BASE_DIR) + 'temp')
        # # """""saving file in flask app"""""
        # file_temp_save=open(str(BASE_DIR) + '/' + 'temp/'+ file_name, "wb").write(r.content)
        # print("saved in temp")


        # #send file and as attachment downloads the file to desktop
        # # return send_file(f"{str(BASE_DIR) + '/' + 'temp/'+ file_name}", as_attachment=True)
        # file_path = os.path.join(BASE_DIR, 'temp', file_name)

        # response = send_file(file_path, as_attachment=True, download_name=file_name)

        # response.close()
        # if os.path.exists(file_path):
        #     try:
        #         os.remove(file_path)
        #         print(f"File '{file_path}' has been removed.")
        #     except OSError as e:
        #         print(f"Error: {e}.")
           
        # flash("Downloaded Successfully","success")
        # return redirect(url_for("doctor_details",doctor_id=doctor_id))
        
        # write to a file in the app's instance folder
        
        # with app.open_instance_resource('downloaded_file', 'wb') as f:
        #     f.write(r.content)
        # return redirect(url_for('order_details',appointment_id=appointment_id))
    except Exception as e:
        print(e)
        flash("Sorry.. Could not download the file","error")
        return redirect(url_for("doctor_details",doctor_id=doctor_id))

# @app.after_request
# def remove_file(response):
#     try:
#         os.remove(str(BASE_DIR)+'temp', request.path.split('/')[-1])
#     except Exception as error:
#         app.logger.error("Error removing or closing downloaded file handle", error)
#     return response

@app.route("/doctors" , methods=['GET','POST'])
def doctors():
    try:
        headers={
            "Content-Type":"application/json"
        }
        
        # doctor_listing=requests.post(base_url+doctor_listing_api, headers=headers)
        # doctor_list_response=json.loads(doctor_listing.text)
        # print(doctor_listing.status_code)
        # doctor_list = doctor_list_response['data']
        # return render_template("doctors.html",doctors=doctor_list)

        #specializations list api call
        specialization_request=requests.get(base_url+specialization_list_api, headers=headers)
        specialization_response=json.loads(specialization_request.text)
        print("specialization list api",specialization_request.status_code)
        specializations=specialization_response['data']
        # print(specializations)

        # language api call
        language_api_request=requests.get(base_url+language_api,headers=headers)
        print("language api",language_api_request.status_code)
        language_api_response=json.loads(language_api_request.text)
        languages=language_api_response['data']

        # approved doctor listing
        payload={                    
                    "specialization":"",
                    "location":"",
                    "is_accepted":1                    
                }
        json_data=json.dumps(payload)
        print(json_data)
        doctor_listing=requests.post(base_url+doctor_listing_api, data=json_data, headers=headers)
        doctor_list_response=json.loads(doctor_listing.text)
        print(doctor_listing.status_code)
        doctor_list = doctor_list_response['data']
        print(len(doctor_list))

        # rejected doctors
        payload={                    
                    "specialization":"",
                    "location":"",
                    "is_accepted":0                    
                }
        json_data1=json.dumps(payload)
        print(json_data1)
        doctor_listing=requests.post(base_url+doctor_listing_api, data=json_data1, headers=headers)
        doctor_list_response=json.loads(doctor_listing.text)
        print(doctor_listing.status_code)
        rejected_doctors = doctor_list_response['data']
        print(len(rejected_doctors))

        # new doctors
        payload={                    
                    "specialization":"",
                    "location":"",
                    "is_accepted":None               
                }
        json_data2=json.dumps(payload)
        print(json_data2)
        doctor_listing=requests.post(base_url+doctor_listing_api, data=json_data2, headers=headers)
        doctor_list_response=json.loads(doctor_listing.text)
        print(doctor_listing.status_code)
        new_doctors = doctor_list_response['data']
        print(len(new_doctors))

        # add doctor
        if request.method == 'POST':
            if request.form['form_type'] == "add_doctor":
                print("add doctor")
                first_name=request.form['first_name']
                last_name=request.form['last_name']
                email_address=request.form['email_address']
                phone_no=request.form['phone_no']
                designation=request.form['designation']
                specialization=request.form['specialization']
                location=request.form['location']

                payload={
                    "new_user":1,
                    "user_id":"",
                    "doc_fname":first_name,
                    "doc_lname":last_name,
                    "email":email_address,
                    "specialization":specialization,
                    "location":location,
                    "mobile_num":phone_no,
                    "doc_flag":designation
                }
                
                api_data=json.dumps(payload)
                print(api_data)
                add_doctor=requests.post(base_url+add_doctor_api,data=api_data, headers=headers)
                add_doctor_response=json.loads(add_doctor.text)
                print(add_doctor_response)
                return redirect(url_for('doctors'))

            if request.form['form_type'] == "filter":
                print("filter")
                # first_name=request.form['first_name']
                # last_name=request.form['last_name']
                # email_address=request.form['email_address']
                # phone_no=request.form['phone_no']
                # designation=request.form['designation']
                specialization_filter=request.form['specialization2']
                location=request.form['location']

                payload={                    
                    "specialization":specialization_filter,
                    "location":location,                    
                }
                api_data=json.dumps(payload)
                doctor_listing=requests.post(base_url+doctor_listing_api, data=api_data, headers=headers)
                doctor_list_response=json.loads(doctor_listing.text)
                print(doctor_listing.status_code)
                doctor_list = doctor_list_response['data']
        # else:
        #     specialization_filter=""
        #     location=""
        #     payload={                    
        #             "specialization":"",
        #             "location":"",                    
        #         }
        #     json_data=json.dumps(payload)
        #     doctor_listing=requests.post(base_url+doctor_listing_api, data=json_data, headers=headers)
        #     doctor_list_response=json.loads(doctor_listing.text)
        #     print(doctor_listing.status_code)
        #     doctor_list = doctor_list_response['data']

            return render_template("doctors.html",doctors=doctor_list, specializations=specializations, languages=languages,rejected_doctors=rejected_doctors,new_doctors=new_doctors)
        return render_template("doctors.html",doctors=doctor_list, specializations=specializations, languages=languages,rejected_doctors=rejected_doctors,new_doctors=new_doctors)
    except Exception as e:
        print(e)
        flash("Error","error")
    return render_template("doctors.html",doctors=doctor_list, specializations=specializations, languages=languages,rejected_doctors=rejected_doctors,new_doctors=new_doctors)

@app.route("/add_doctor",methods=['GET','POST'])
def add_doctor():
    try:
        headers={
            "Content-Type":"application/json"
        }
        #specializations list api call
        specialization_request=requests.get(base_url+specialization_list_api, headers=headers)
        specialization_response=json.loads(specialization_request.text)
        print("specialization list api",specialization_request.status_code)
        specializations=specialization_response['data']
        # print(specializations)

        # language api call
        language_api_request=requests.get(base_url+language_api,headers=headers)
        print("language api",language_api_request.status_code)
        language_api_response=json.loads(language_api_request.text)
        languages=language_api_response['data']
        print('gettttt')
        if request.method == 'POST':
            print('posttt')
            # if request.form['form_type'] == "add_doctor":
            print("add doctor")
            'ss'
            first_name=request.form['first_name']
            last_name=request.form['last_name']
            email_address=request.form['email_address']
            phone_no=request.form['phone_no']
            designation=request.form['designation']
            specialization=request.form['specialization']
            location=request.form['location']
            gender=request.form['gender']
            language=request.form['language']
            from_date=request.form['from_date']
            to_date=request.form['to_date']
            from_time=request.form['from_time']
            to_time=request.form['to_time']

            payload={
                    "new_user":1,
                    "user_id":"",
                    "doc_fname":first_name,
                    "doc_lname":last_name,
                    "email":email_address,
                    "specialization":specialization,
                    "location":location,
                    "mobile_num":phone_no,
                    "doc_flag":designation,
                    "language_known":language,
                    "gender":gender,
                    "date_from":from_date,
                    "date_to":to_date,
                    "time_slot_from":from_time,
                    "time_slot_to":to_time
            }
                
            api_data=json.dumps(payload)
            print(api_data)
            add_doctor=requests.post(base_url+add_doctor_api,data=api_data, headers=headers)
            add_doctor_response=json.loads(add_doctor.text)
            print(add_doctor_response)
            return redirect(url_for('doctors'))
        return render_template("add_doctor.html",specializations=specializations, languages=languages)
    except Exception as e:
        print(e,'asdfasdfasdfasdfasdfasdf')
    return render_template("add_doctor.html")

@app.route("/update_doctor/<int:doctor_id>",methods=['GET','POST'])
def update_doctor(doctor_id):
    try:
        # if 'user_id' in session:
        #     doctor_id=session['user_id']
        #     print(doctor_id)
        # else:
        #     return redirect(url_for('login'))
        headers = {
                "Content-Type":"application/json"
            }
        payload={
            "doctor_id":doctor_id
        }
        api_data=json.dumps(payload)
        print(api_data)
        # doctor profile api call
        doctor_profile_request=requests.post(base_url+doctor_profile_api, data=api_data, headers=headers)
        print(doctor_profile_request.status_code)
        doctor_profile_response=json.loads(doctor_profile_request.text)
        # print(doctor_profile_response)
        doctor_profile1=doctor_profile_response['data1']
        doctor_profile2=doctor_profile_response['data2']
         #language given as list must be separated
        language_list=doctor_profile2['language_known']
        # language_known=", ".join(language)
        # print(", ".join(language))
        # print(*language, sep = ', ')
        language_list_length=len(language_list)
        print("languages",language_list_length)
        
        # """" SIGNATURE """"
        # signature_url=doctor_profile2['signature']
        # r = requests.get(signature_url)
        # # """r = requests.get(url)"""
        # print("error")
        # # """this removes http and website part from url"""
        # url_split_1 = urlparse(signature_url)
        # print(url_split_1)
        # #"""this will split rest of the path from file name"""
        # signature_file=os.path.basename(url_split_1.path)
        # print("filename",signature_file)
        # cwd = os.getcwd()+'/'
        # print(cwd)
        # if 'temp' not in os.listdir(cwd):
        #     os.mkdir(cwd + 'temp')
        # #"""saving file in flask app"""
        # file_temp_save=open(cwd + 'temp/'+ signature_file, "wb").write(r.content)
        # print("saved in temp")
        # signature=signature_file


        # language api call
        language_api_request=requests.get(base_url+language_api,headers=headers)
        print("language api",language_api_request.status_code)
        language_api_response=json.loads(language_api_request.text)
        languages=language_api_response['data']
        #specializations list api call
        specialization_request=requests.get(base_url+specialization_list_api, headers=headers)
        specialization_response=json.loads(specialization_request.text)
        print("specialization list api",specialization_request.status_code)
        specializations=specialization_response['data']
        # print(specializations)

        # work hour timeslot api call
        # timeslot_list_request=requests.post(base_url+time_slot_list_api, data=api_data, headers=headers)
        # timeslot_list_response=json.loads(timeslot_list_request.text)
        # print(timeslot_list_request.status_code)
        # timeslots = timeslot_list_response['data']
        # days = timeslot_list_response['weekday']

        # working hours api call
        # working_hours_request=requests.post(base_url+working_hours_api, data=api_data, headers=headers)
        # working_hours_response=json.loads(working_hours_request.text)
        # print("working hours",working_hours_request.status_code)
        # working_hours=working_hours_response['data']
        print('gett')
        if request.method == 'POST':
            print("post")       
            # file upload
            # ******* FILE UPLOADS ********
            address_file = request.files["address_proof_file"]
            if address_file.filename == '':
                address_file_path=''
                addressFileName=''
                address_file_size=''

            # if request.files["address_proof_file"] == '':
                print("no address file")
            else:
                address_file = request.files["address_proof_file"]
                print("address",address_file)
                addressFileName = secure_filename(address_file.filename)
                print(addressFileName)
                # cwd = os.getcwd()+'/'
                # print(cwd)
                # if 'temp' not in os.listdir(cwd):
                #     os.mkdir(cwd + 'temp')
                # address_file.save(os.path.join(cwd + 'temp', addressFileName))

                # with open(cwd + 'temp/'+ addressFileName, 'rb') as f:
                #     # data_file = {
                #     #     "common_file":(addressFileName, 'rb')
                #     # }
                #     data_file = {
                #         "common_file":(addressFileName, f)
                #     }
                print("BASE_DIR : ",BASE_DIR)
                if 'temp' not in os.listdir(BASE_DIR):
                    print("print line 1")
                    os.mkdir(str(BASE_DIR) + '/' + 'temp')
                    print("print line 2")
                address_file.save(os.path.join(str(BASE_DIR) +'/' + 'temp', addressFileName))
                print("print line 3")

                file_stats = os.stat(str(BASE_DIR) + '/' + 'temp/'+ addressFileName)
                print("print line 4")
                # print(file_stats)
                address_file_size=f'{round(file_stats.st_size / (1024 * 1024),2)} MB'
                print(address_file_size)
                print(f'{file_stats.st_size / (1024)} KB')
                print(f'{file_stats.st_size / (1024 * 1024)} MB')

                with open(str(BASE_DIR) + '/' + 'temp/'+ addressFileName, 'rb') as f:
                    print("print line 5")
                    # data_file = {
                    #     "common_file":(addressFileName, 'rb')
                    # }
                    data_file = {
                        "common_file":(addressFileName, f)
                    }
                    print(data_file)
                    file_uploader_api=base_url+file_upload_api
                    file_upload_submit = requests.post(file_uploader_api,files=data_file,)
                    print(file_upload_submit.status_code)                    
                    file_upload_response=json.loads(file_upload_submit.text)
                    print(file_upload_response)
                    print(file_upload_submit.status_code)
                    address_file_path=file_upload_response['common_file']
                    print(address_file_path)
                    if file_upload_response['common_file']:
                        flash(f"{addressFileName} uploaded","success")
                    else:
                        flash("Something went wrong","error")

            certificate_file = request.files["certificate_file"]
            if certificate_file.filename == '':
                certificate_file_path=''
                certificateFileName=''
                certificate_file_size=''
                print("no certificate file")
            else:
                certificate_file = request.files["certificate_file"]
                certificateFileName = secure_filename(certificate_file.filename)
                print(certificateFileName)
                # cwd = os.getcwd()+'/'
                # print(cwd)
                # if 'temp' not in os.listdir(cwd):
                #     os.mkdir(cwd + 'temp')
                # certificate_file.save(os.path.join(cwd + 'temp', certificateFileName))

                # with open(cwd + 'temp/'+ certificateFileName, 'rb') as f:
                #     # data_file = {
                #     #     "common_file":(certificateFileName, 'rb')
                #     # }
                #     data_file = {
                #         "common_file":(certificateFileName, f)
                #     }

                print("BASE_DIR : ",BASE_DIR)
                if 'temp' not in os.listdir(BASE_DIR):
                    os.mkdir(str(BASE_DIR) + '/' + 'temp')
                certificate_file.save(os.path.join(str(BASE_DIR) +'/' + 'temp', certificateFileName))

                file_stats = os.stat(str(BASE_DIR) + '/' + 'temp/'+ certificateFileName)
                # print(file_stats)
                certificate_file_size=f'{round(file_stats.st_size / (1024 * 1024),2)} MB'
                print(certificate_file_size)
                print(f'{file_stats.st_size / (1024)} KB')
                print(f'{file_stats.st_size / (1024 * 1024)} MB')

                with open(str(BASE_DIR) + '/' + 'temp/'+ certificateFileName, 'rb') as f:
                    # data_file = {
                    #     "common_file":(certificateFileName, 'rb')
                    # }
                    data_file = {
                        "common_file":(certificateFileName, f)
                    }
                    print(data_file)
                    file_uploader_api=base_url+file_upload_api
                    file_upload_submit = requests.post(file_uploader_api,files=data_file,)
                    print(file_upload_submit.status_code)                    
                    file_upload_response=json.loads(file_upload_submit.text)
                    print(file_upload_response)
                    print(file_upload_submit.status_code)
                    certificate_file_path=file_upload_response['common_file']
                    if file_upload_response['common_file']:
                        flash(f"{certificateFileName} uploaded","success")
                    else:
                        flash("Something went wrong","error")

            photo_file = request.files["photo_file"]
            if photo_file.filename == '':
                photo_file_path=''
                photoFileName=''
                photo_file_size=''
                print("no photo file")
            else:
                photo_file = request.files["photo_file"]
                photoFileName = secure_filename(photo_file.filename)
                print(photoFileName)
                # cwd = os.getcwd()+'/'
                # print(cwd)
                # if 'temp' not in os.listdir(cwd):
                #     os.mkdir(cwd + 'temp')
                # photo_file.save(os.path.join(cwd + 'temp', photoFileName))

                # with open(cwd + 'temp/'+ photoFileName, 'rb') as f:
                #     # data_file = {
                #     #     "common_file":(photoFileName, 'rb')
                #     # }
                #     data_file = {
                #         "common_file":(photoFileName, f)
                #     }

                print("BASE_DIR : ",BASE_DIR)
                if 'temp' not in os.listdir(BASE_DIR):
                    os.mkdir(str(BASE_DIR) + '/' + 'temp')
                photo_file.save(os.path.join(str(BASE_DIR) +'/' + 'temp', photoFileName))

                file_stats = os.stat(str(BASE_DIR) + '/' + 'temp/'+ photoFileName)
                # print(file_stats)
                photo_file_size=f'{round(file_stats.st_size / (1024 * 1024),2)} MB'
                print(photo_file_size)
                print(f'{file_stats.st_size / (1024)} KB')
                print(f'{file_stats.st_size / (1024 * 1024)} MB')

                with open(str(BASE_DIR) + '/' + 'temp/'+ photoFileName, 'rb') as f:
                    # data_file = {
                    #     "common_file":(photoFileName, 'rb')
                    # }
                    data_file = {
                        "common_file":(photoFileName, f)
                    }
                    print(data_file)
                    file_uploader_api=base_url+file_upload_api
                    file_upload_submit = requests.post(file_uploader_api,files=data_file,)
                    print(file_upload_submit.status_code)                    
                    file_upload_response=json.loads(file_upload_submit.text)
                    print(file_upload_response)
                    print(file_upload_submit.status_code)
                    photo_file_path=file_upload_response['common_file']
                    if file_upload_response['common_file']:
                        flash(f"{photoFileName} uploaded","success")
                    else:
                        flash("Something went wrong","error")

            signature_file = request.files["signature_file"]
            if signature_file.filename == '':
                signature_file_path=''
                signatureFileName=''
                signature_file_size=''
                print("no signature file")
            else:
                signature_file = request.files["signature_file"]
                signatureFileName = secure_filename(signature_file.filename)
                print(signatureFileName)
                # cwd = os.getcwd()+'/'
                # print(cwd)
                # if 'temp' not in os.listdir(cwd):
                #     os.mkdir(cwd + 'temp')
                # signature_file.save(os.path.join(cwd + 'temp', signatureFileName))

                # with open(cwd + 'temp/'+ signatureFileName, 'rb') as f:
                #     # data_file = {
                #     #     "common_file":(signatureFileName, 'rb')
                #     # }
                #     data_file = {
                #         "common_file":(signatureFileName, f)
                #     }

                print("BASE_DIR : ",BASE_DIR)
                if 'temp' not in os.listdir(BASE_DIR):
                    os.mkdir(str(BASE_DIR) + '/' + 'temp')
                signature_file.save(os.path.join(str(BASE_DIR) +'/' + 'temp', signatureFileName))

                file_stats = os.stat(str(BASE_DIR) + '/' + 'temp/'+ signatureFileName)
                # print(file_stats)
                signature_file_size=f'{round(file_stats.st_size / (1024 * 1024),2)} MB'
                print(signature_file_size)
                print(f'{file_stats.st_size / (1024)} KB')
                print(f'{file_stats.st_size / (1024 * 1024)} MB')

                with open(str(BASE_DIR) + '/' + 'temp/'+ signatureFileName, 'rb') as f:
                    # data_file = {
                    #     "common_file":(signatureFileName, 'rb')
                    # }
                    data_file = {
                        "common_file":(signatureFileName, f)
                    }
                    print(data_file)
                    file_uploader_api=base_url+file_upload_api
                    file_upload_submit = requests.post(file_uploader_api,files=data_file,)
                    print(file_upload_submit.status_code)                    
                    file_upload_response=json.loads(file_upload_submit.text)
                    print(file_upload_response)
                    print(file_upload_submit.status_code)
                    signature_file_path=file_upload_response['common_file']
                    if file_upload_response['common_file']:
                        flash(f"{signatureFileName} uploaded","success")
                    else:
                        flash("Something went wrong","error")        

                # ******* FILE UPLOADS E ********

            # other fields
            first_name=request.form['first_name']
            last_name=request.form['last_name']
            email_address=request.form['email_address']
            phone_no=request.form['phone_no']
            designation=request.form['designation']
            qualification = request.form['qualification']
            specialization=request.form['specialization']
            address=request.form['address']
            location=request.form['location']
            gender=request.form['gender']
            language=request.form.getlist('language')
            certificate_number=request.form['certificate_number']
            doctor_bio=request.form['doctor_bio']
            # from_date=request.form['from_date']
            # to_date=request.form['to_date']
            # from_time=request.form['from_time']
            # to_time=request.form['to_time']
            print("error")

            payload={
                "user_id":doctor_id,
                "user_fname":first_name,
                "user_lname":last_name,
                "gender":gender,
                "mobile_num":phone_no,
                "user_mail":email_address,
                "language_known": language,
                "location":location,
                "doctor_flag":designation,
                "specialization":specialization,
                "doctor_bio":doctor_bio,

                "qualification":qualification,
                "address":address,
                "certificate_no":certificate_number,

                "address_proof":address_file_path,
                "addr_file_name": addressFileName,
                "addr_file_size": address_file_size,

                "registration_certificate":certificate_file_path,
                "reg_file_name": certificateFileName,
                "reg_file_size": certificate_file_size,

                "signature":signature_file_path,
                "sign_file_name": signatureFileName,
                "sign_file_size": signature_file_size,

                "profile_pic":photo_file_path,
                "profile_file_name":photoFileName,
                "profile_file_size":photo_file_size,
                "operation_flag":"edit"
            }
                # "date_from":from_date,
                # "date_to":to_date,
                # "time_from":from_time,
                # "time_to":to_time

            # }
                        
            api_data=json.dumps(payload)
            print(api_data)
            doctor_update_request=requests.post(base_url+doctor_update_api, data=api_data, headers=headers)
            print("update doctor",doctor_update_request.status_code)
            doctor_update_response=json.loads(doctor_update_request.text)
            print(doctor_update_response)
            if doctor_update_response['response_code']==200:
                flash("Doctor Profile Updated","success")
            else:
                flash("Something went wrong","error")
            return redirect(url_for('doctor_details',doctor_id=doctor_id))
        return render_template("update_doctor.html", doctor_profile1=doctor_profile1,doctor_profile2=doctor_profile2,
        languages=languages,specializations=specializations,language_list=language_list,doctor_id=doctor_id)
    except Exception as e:
        print(e)
    return render_template("update_doctor.html")

@app.route("/doctor_details/<int:doctor_id>",methods=['GET','POST'])
def doctor_details(doctor_id):
    try:
        print(doctor_id)
        if 'doctor_flag' in session:
            doctor_flag=session['doctor_flag']
            print(doctor_flag)
        headers = {
                "Content-Type":"application/json"
            }
        payload={
            "doctor_id":doctor_id
        }
        api_data=json.dumps(payload)
        doctor_profile_request=requests.post(base_url+doctor_profile_api, data=api_data, headers=headers)
        doctor_profile_response=json.loads(doctor_profile_request.text)
        doctor_profile1=doctor_profile_response['data1']
        doctor_profile2=doctor_profile_response['data2']
        locations=doctor_profile_response['locations']
        # * Languages from list are converted to string with comma *
        language=doctor_profile2['language_known']
        language_known=", ".join(language)
        print(", ".join(language))
        print(*language, sep = ', ')
        #  * DOCTOR FLAG FROM PROFILE API IS CONVERTED TO VALUES 1 AND 2 TO PASS THROUGH APPOINTMENT LIST API *
        doctor_desig=doctor_profile2['doctor_flag']
        if doctor_desig == 'senior':
            doc_flag = 1
        elif doctor_desig == 'junior':
            doc_flag = 2
        else :
            doc_flag=""

        # list of appointments assigned to the doctor
        if 'doctor_flag' in session:
            doctor_flag=session['doctor_flag']
            print(doctor_flag)

        headers = {
        "Content-Type":"application/json"
        }
        # if request.method == 'POST':
        #     print('POST')
        #     appointment_status=request.form['status']
        #     print(appointment_status)
        #     specialization=request.form['specialization']
        #     location=request.form['location']
        # else:
        #     appointment_status=""
        #     specialization=""
        #     location=""

        payload={
                "appointment_status" : "",
                "doctor_flag":doc_flag,
                "user_id":doctor_id
                # "specialization":specialization,
                # "location":location, 
            }
        api_data=json.dumps(payload)
        print(api_data)
        #header not passed as it caused error
        appointment_response=requests.post(base_url+appointment_list_api,data=api_data,headers=headers)
        print('appointment api status code',appointment_response.status_code)
        appointment_data=json.loads(appointment_response.text)
        appointment_list=appointment_data['data']
        if appointment_data['data']:
            print("No.of appointments",len(appointment_list))

        doctor_time_slot_response = requests.post(base_url+doctor_time_slots,data=api_data,headers=headers)
        print('asdfasd',doctor_time_slot_response)
        doctor_time_slot = json.loads(doctor_time_slot_response.text)
        print('doctor_time_slots', doctor_time_slot['data']  )
        # approving or rejecting a doctor by admin
        if request.method == 'POST':
            # is_accepted=request.form['form_type']
            # value 0 for reject, and value 1 for accept
            print(request.form)
            if request.form['form_type'] == "reject":
                is_accepted = 0
                session['is_accepted'] = is_accepted
                payload={
                    "user_id":doctor_id,
                    "is_accepted":0,
                    #"doctor_flag":doc_designation
                }
                api_data=json.dumps(payload)
                admin_approval_req=requests.post(base_url+doctor_admin_approval_api,data=api_data,headers=headers)
                print(admin_approval_req.status_code)
                admin_approval=json.loads(admin_approval_req.text)
                print(admin_approval)
                flash("Doctor Rejected","success")
                return redirect(url_for('doctor_details',doctor_id=doctor_id))
               
            if request.form['form_type'] == 1:
                
                is_accepted = 1
                # session['is_accepted'] = is_accepted
            if request.form['form_type'] == 'doctor_designation':
                print("doctor_designation")
                doc_designation = request.form['designation']
                
                payload={
                    "user_id":doctor_id,
                    "is_accepted":1,
                    "doctor_flag":doc_designation,
                }
                api_data=json.dumps(payload)
                admin_approval_req=requests.post(base_url+doctor_admin_approval_api,data=api_data,headers=headers)
                print(admin_approval_req.status_code)
                admin_approval=json.loads(admin_approval_req.text)
                print(admin_approval)
                flash("Doctor Approved","success")
                return redirect(url_for('doctor_details',doctor_id=doctor_id))
        return render_template("doctor_details.html",doctor_profile1=doctor_profile1,doctor_profile2=doctor_profile2,
        language_known=language_known,doctor_id=doctor_id,appointment_list=appointment_list,locations=locations, doctor_time_slot=doctor_time_slot['data'])
    except Exception as e:
        print(e)
        return redirect(url_for('doctors'))
    # return render_template("doctor_details.html",doctor_profile1=doctor_profile1,doctor_profile2=doctor_profile2,
    # language_known=language_known,doctor_id=doctor_id,appointment_list=appointment_list)

@app.route("/dashboard/doctor_dash/<actions>/<int:appointment_id>",methods=['GET','POST'])
def action_doctor(actions,appointment_id):
    # actions: accept=1,reject=3,escalate=2, # reschedule by doctor = 4, reschedule by customer = 5
    # appointment closed = 6, rescheduled = 7, follow up =8, no show = 9, transfered = 10
    appointent_status_api="api/doctor/appointment_status_update"
    headers={
            "Content-Type":"application/json"
        }
    print(appointment_id)
    print(actions)
    payload={
        'appointment_id':appointment_id,
        'appointment_status':actions
    }
    api_data=json.dumps(payload)
    action=requests.post(base_url+appointent_status_api,data=api_data,headers=headers)
    action_button_response=json.loads(action.text)
    print(action.status_code)
    print(action_button_response)
    return redirect(url_for("customers"))

@app.route("/customers", methods=['GET','POST'])
def customers():
    try:
        headers={
            "Content-Type":"application/json"
        }

         # language api call
        language_api_request=requests.get(base_url+language_api,headers=headers)
        print("language api",language_api_request.status_code)
        language_api_response=json.loads(language_api_request.text)
        languages=language_api_response['data']

        payload={
            "operation_flag":"view"
        }
        api_data=json.dumps(payload)
        customer_listing=requests.post(base_url+customer_listing_api, data=api_data, headers=headers)
        customer_list_response=json.loads(customer_listing.text)
        print(customer_listing.status_code)
        customer_list = customer_list_response['data']
        for i in customer_list:
            print(i)
        return render_template("customers.html",customers=customer_list)
    except Exception as e:
        print(e)
        flash("Error","error")
    return render_template("customers.html")

@app.route("/customers/customer_details/<int:user_id>")
def customer_details(user_id):
    if 'doctor_flag' in session:
        doctor_flag=session['doctor_flag']
    else:
        return redirect(url_for('admin_login'))
    headers={
        "Content-Type":"application/json"
        }
    # * Customer profile api call *
    # if 'user_id' in session:
    #         user_id=session['user_id']
    #         print(user_id)
    # else:
    #         return redirect(url_for('login'))
    headers = {
                "Content-Type":"application/json"
            }
    payload={
            "user_id":user_id
        }
    api_data=json.dumps(payload)
    customer_profile_request=requests.post(base_url+customer_profile_api, data=api_data, headers=headers)
    customer_profile_response=json.loads(customer_profile_request.text)
    profile1=customer_profile_response['data1']
    profile2=customer_profile_response['data2']

    # * Appointment list api call *
    payload={
        "user_id": user_id,
        "doctor_flag":doctor_flag,
        # "appointment_id":appointment_id
    }
    api_data=json.dumps(payload)
    print(api_data)
    appointment_response=requests.post(base_url+appointment_list_api,data=api_data, headers=headers)
    appointment_data=json.loads(appointment_response.text)
    appointment_list=appointment_data['data']

    if 'user_id' in session:
        user_id=session['user_id']
    headers={
    "Content-Type":"application/json"
    }
    payload1={
        "user_id":user_id,
        "status": "1"
    }
    api_data1=json.dumps(payload1)
    invoices_request=requests.post(base_url+invoice_list_api,data=api_data1,headers=headers)
    invoice_response=json.loads(invoices_request.text)
    paid_invoices=invoice_response['data']
    payload2={
        "user_id":user_id,
        "status": "2"
    }
    api_data2=json.dumps(payload2)
    invoices_request=requests.post(base_url+invoice_list_api,data=api_data2,headers=headers)
    invoice_response=json.loads(invoices_request.text)
    unpaid_invoices=invoice_response['data']
    # return render_template('invoices.html',paid_invoices=paid_invoices,unpaid_invoices=unpaid_invoices)

    print('appointment_list',appointment_list,'profile1',profile1,'profile2',profile2,'paid_invoices',paid_invoices, 'unpaid_invoices',unpaid_invoices)

    return render_template("customer_details.html", appointment_list=appointment_list,profile1=profile1,profile2=profile2,
                           paid_invoices=paid_invoices,unpaid_invoices=unpaid_invoices)

@app.route("/invoice_details/<int:invoice_id>", methods=['GET','POST'])
def invoice_details(invoice_id):
    try:
        headers={
        "Content-Type":"application/json"
        }
        payload={
            "invoice_id":invoice_id
        }
        api_data=json.dumps(payload)
        invoice_request=requests.post(base_url+invoice_detail_api,data=api_data,headers=headers)
        invoice_response=json.loads(invoice_request.text)
        print("invoice detail",invoice_request.status_code)
        invoice_details=invoice_response['data']
        print(invoice_details)
        paid_appointment="unpaid_invoice"
        session['paid_appointment']= paid_appointment
        session['invoice_data']=invoice_details
        # if request.method == 'POST':
        #     print("post")
        #     payload={
        #         "appointment_id":appointment_id,
        #         "location_id":1
        #     }
        #     api_data=json.dumps(payload)
        #     print(api_data)
        #     pay_confirm_request=requests.post(base_url+customer_payments_api,data=api_data,headers=headers)
        #     pay_confirm_response=json.loads(pay_confirm_request.text)
        #     print("payment confirm :", pay_confirm_request.status_code)
        #     print(pay_confirm_response)
        #     return redirect(url_for('pay_confirm'))
        return render_template('invoice_details.html',invoice_details=invoice_details)
    except Exception as e:
        print(e)
    return render_template('invoice_details.html')

@app.route("/invoice_preview",methods=['GET','POST'])
def invoice_preview():
    print("invoice preview")

    if 'country' in session:
        country = session['country']
        print('country')
        if (country == 'IN') or (country == 'IND'):
            location_id = 1
        else:
            location_id = 2
    else:
        location_id = 2

    session['loc_id']=location_id

    headers={
        "Content-Type":"application/json"
        }
  
    if 'invoice_data' in session:
        invoice_data=session['invoice_data']
        print("preview",invoice_data)
        user_id=invoice_data['user_id']
        appointment_id = invoice_data['appointment_id']
    # if 'new_appointment_specialization' in session:
    #     new_appointment_specialization=session['new_appointment_specialization']
    if request.method == 'POST':
        coupon = request.form['coupon']
    else:
        coupon = ""
        #paymemts api call
        # payload={
        # "location_id":1
        # }  
    payload={
                    "user_id":user_id,
                    "appointment_id":appointment_id,
                    "specialization":"",
                    "coupon_code":"",
                    "location_id":str(location_id)
                }
    api_data=json.dumps(payload)
    print(api_data)
    payments_request=requests.post(base_url+payments_api,data=api_data,headers=headers)
    payment_response=json.loads(payments_request.text)   
    print("payments api",payments_request.status_code)
    print(payment_response)
    payment=payment_response['payment']
    temp_data_id = payment_response['temp_data_id']
    session['temp_data_id']= temp_data_id
        # if request.method=='POST':
        #     print("post")
        #     api_data=json.dumps(new_data)
        #     new_appointment_request=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
        #     new_appointment_response=json.loads(new_appointment_request.text)
        #     print(new_appointment_request.status_code)
        #     print(new_appointment_response)
        #     new_appointment_id=new_appointment_response["appointment_id"]
        #     print("new id:",new_appointment_id)
        #     return redirect(url_for('pay_confirm',appointment_id=new_appointment_id))
            # return render_template('follow_up_preview.html')

    return render_template('unpaid_invoice_preview.html',invoice_data=invoice_data,payment=payment)

@app.route("/appointment_details/<int:appointment_id>" ,methods=['GET','POST'])
def appointment_details(appointment_id):
    print('1683', appointment_id)
    headers={
            "Content-type":"application/json"
    }
    print(id)
    payload={
        "appointment_id":appointment_id,
        "user_id":"",
        "file_flag":""
    }
    api_data=json.dumps(payload)
    appointment_detail=requests.post(base_url+appointment_detail_api, data=api_data, headers=headers)
    'ss'
    appointment_detail_response=json.loads(appointment_detail.text)
    print(appointment_detail_response)

    appointment_details=appointment_detail_response['data']
    print(appointment_details)
    user_id=appointment_details['user_id']
    category_id=appointment_details['category_id']
    follow_ups = appointment_details['followup']
    observations=appointment_details['observations']
    print(user_id,category_id, follow_ups, observations)
    
    if request.method == 'POST':
        if request.form['form_type'] == 'reschedule':
            print("reschedule")
            reschedule_date=request.form['reschedule_date']
            reschedule_time=request.form['reschedule_time']
            reschedule_data={
                "appointment_id":appointment_id,
                "appointment_date":reschedule_date,
                "appointment_time":reschedule_time,
                "appointment_status":4,
                "user_id": user_id
            }
            print(reschedule_data)
            reschedule_data_json=json.dumps(reschedule_data)
            reschedule_submit=requests.post(base_url+reschedule_api, data=reschedule_data_json, headers=headers)
            reschedule_submit_response=json.loads(reschedule_submit.text)
            print(reschedule_submit_response)
            print(reschedule_submit.status_code)

        if request.form['form_type'] == 'observation': 
            print("observation")       
            observations=request.form['observations']
            data={
                "appointment_id":appointment_id,
                "observations":observations
            }
            json_data=json.dumps(data)
            print(json_data)
            observation_submit=requests.post(base_url+observations_api, data=json_data, headers=headers)
            observation_submit_response=json.loads(observation_submit.text)
            print("post response:",observation_submit.status_code)
            print(observation_submit_response)

        if request.form['form_type'] == 'upload_prescription':
            print("upload prescription")
            file_headers={
                'files' : 'multipart/form-data'
            }
            print("error 1")
            prescription_file=request.files['customFile']
            print("error2")
            print(prescription_file)
            filename=secure_filename(prescription_file.filename)
            print("error3")
            print(filename)
            files={
                'document' : open(filename,'rb')
            }
            print(files)
            data={
                'appointment_id': appointment_id
            }
            api_data=json.dumps(data)
            prescription_submit=requests.post(base_url+prescription_api, files=files, data=api_data, headers=file_headers)
            prescription_submit_response=json.loads(prescription_submit.text)
            print(prescription_submit_response)
            print(prescription_submit.status_code)

        if request.form['form_type'] == 'prescription': 
            print("prescription")       
            prescription=request.form['prescription']
            # data={
            #     "appointment_id":id,
            #     "prescription":prescription
            # }
            json_data=json.dumps(data)
            print(json_data)
            prescription_submit=requests.post(base_url+prescription_api, data=json_data, headers=headers)
            prescription_submit_response=json.loads(prescription_submit.text)
            print(prescription_submit_response)
            print(prescription_submit.status_code)

        if request.form['form_type'] == 'follow_up':
            appointment_date=request.form['follow_up_date']
            appointment_time=request.form['follow_up_time']
            payload={
                        "new_user":0,
                        "user_id":user_id,
                        "appointment_date":appointment_date,
                        "appointment_time":appointment_time,
                        "followup_id":appointment_id,
                        "category_id":category_id,
                        "type_booking":"followup"
            }
            api_data=json.dumps(payload)
            follow_up_submit=requests.post(base_url+follow_up_api, data=api_data, headers=headers)
            follow_up_response=json.loads(follow_up_submit.text)
            print(follow_up_submit.status_code)
            print(follow_up_response)
        return redirect(url_for('customers'))
    return render_template("appointment_details2.html",appointment_details=appointment_details)

@app.route("/appointments" , methods=['GET','POST'])
def appointments():
    try:
        if 'doctor_flag' in session:
            doctor_flag=session['doctor_flag']
            print(doctor_flag)

        headers = {
        "Content-Type":"application/json"
        }
        if request.method == 'POST':
            print('POST')
            appointment_status=request.form['status']
            print(appointment_status)
            specialization=request.form['specialization']
            location=request.form['location']
        else:
            appointment_status=""
            specialization=""
            location=""

        payload={
                "appointment_status" : appointment_status,
                "doctor_flag":"",
                "user_id":""
                # "specialization":specialization,
                # "location":location, 
            }
        api_data=json.dumps(payload)
        print(api_data)
        #header not passed as it caused error
        appointment_response=requests.post(base_url+appointment_list_api,data=api_data,headers=headers)
        'ss'
        print('appointment api status code',appointment_response.status_code)
        appointment_data=json.loads(appointment_response.text)
        for i in appointment_data['data']:
            print(i)
            break
        appointment_list=appointment_data['data']
        return render_template("appointments.html",appointments=appointment_list)
    except Exception as e:
        print(e)
    return render_template("appointments.html")

@app.route("/receipt_list")
def receipt_list():
    try:
        # if 'user_id' in session:
        #     user_id=session['user_id']
        #     print(user_id)
        headers={
        "Content-Type":"application/json"
        }
        payload1={
            "user_id":"",
            "status": "1"
        }
        api_data1=json.dumps(payload1)
        print(api_data1)
        invoices_request=requests.post(base_url+invoice_list_api,data=api_data1,headers=headers)
        invoice_response=json.loads(invoices_request.text)
        print("invoice list:",invoices_request.status_code)
        paid_invoices=invoice_response['data']
        payload2={
            "user_id":"",
            "status": "2"
        }
        api_data2=json.dumps(payload2)
        print(api_data2)
        invoices_request=requests.post(base_url+invoice_list_api,data=api_data2,headers=headers)
        invoice_response=json.loads(invoices_request.text)
        print("invoice list:",invoices_request.status_code)
        unpaid_invoices=invoice_response['data']
        return render_template('receipt_list.html',paid_invoices=paid_invoices,unpaid_invoices=unpaid_invoices)

    except Exception as e:
        print(e)
    return render_template("receipt_list.html")

@app.route("/receipt_details/<int:invoice_id>")
def receipt_details(invoice_id):
    try:
        headers={
        "Content-Type":"application/json"
        }
        payload={
            "invoice_id":invoice_id
        }
        api_data=json.dumps(payload)
        invoice_request=requests.post(base_url+invoice_detail_api,data=api_data,headers=headers)
        invoice_response=json.loads(invoice_request.text)
        print("invoice detail",invoice_request.status_code)
        invoice_details=invoice_response['data']
        print(invoice_details)
        paid_appointment="unpaid_invoice"
        session['paid_appointment']= paid_appointment
        session['invoice_data']=invoice_details
        # if request.method == 'POST':
        #     print("post")
        #     payload={
        #         "appointment_id":appointment_id,
        #         "location_id":1
        #     }
        #     api_data=json.dumps(payload)
        #     print(api_data)
        #     pay_confirm_request=requests.post(base_url+customer_payments_api,data=api_data,headers=headers)
        #     pay_confirm_response=json.loads(pay_confirm_request.text)
        #     print("payment confirm :", pay_confirm_request.status_code)
        #     print(pay_confirm_response)
        #     return redirect(url_for('pay_confirm'))
        return render_template('receipt_details.html',invoice_details=invoice_details)

    except Exception as e:
        print(e)
    return render_template('receipt_details.html')

@app.route("/report_customer/<int:appointment_id>")
def report_customer(appointment_id):
    try:
        if 'user_id' in session:
            doctor_id=session['user_id']
            print(doctor_id)
        else:
            return redirect(url_for('login'))
        if 'doctor_flag' in session:
            doctor_flag=session['doctor_flag']
            print(doctor_flag)
        headers = {
            "Content-Type":"application/json"
        }
        payload={
        "appointment_id":appointment_id,
        "user_id":"",
        "file_flag":"",
        "doctor_id":doctor_id
        }
        api_data=json.dumps(payload)
        print(api_data)
        appointment_detail=requests.post(base_url+appointment_detail_api, data=api_data, headers=headers)
        appointment_detail_response=json.loads(appointment_detail.text)
        appointment_details=appointment_detail_response['data']
        print("detail api :",appointment_detail.status_code)
        user_id=appointment_details['user_id']
        data={
            "appointment_id":appointment_id,
            "customer_id":user_id,
            "doctor_id":doctor_id
        }
        api_data2=json.dumps(data)
        print(api_data2)
        report_customer_request=requests.post(base_url+report_customer_api,data=api_data2,headers=headers)
        print("report customer ",report_customer_request.status_code)
        report_customer_response=json.loads(report_customer_request.text)
        print("report customer :",report_customer_response)
        flash("Customer Reported","info")
        return redirect(url_for('order_detail',id=appointment_id))
    except Exception as e:
        print(e)
    return redirect(url_for('order_detail',id=appointment_id))

@app.route("/discussion/<int:appointment_id>", methods=['GET','POST'])
def discussion(appointment_id):
    try:
        if 'user_id' in session:
            doctor_id=session['user_id']
            print(doctor_id)
        else:
            return redirect(url_for('login'))
        headers={
        "Content-Type":"application/json"
        }
        # calling discussion list api
        payload={
            "appointment_id":appointment_id
        }
        api_data=json.dumps(payload)
        discussion_list_request=requests.post(base_url+discussion_list_api, data=api_data, headers=headers)
        discussion_list_response=json.loads(discussion_list_request.text)
        print("discussion list", discussion_list_request.status_code)
        discussion_list=discussion_list_response['data']
        limit = discussion_list_response['discussion_count']
        # print(discussion_list)

        # calling detail api:            
        if 'doctor_flag' in session:
            doctor_flag=session['doctor_flag']
            print(doctor_flag)

        payload={
            "appointment_id":appointment_id,
            "user_id":"",
            "file_flag":"",
            "doctor_id":doctor_id
        }
        api_data=json.dumps(payload)
        print(api_data)
        appointment_detail=requests.post(base_url+appointment_detail_api, data=api_data, headers=headers)
        appointment_detail_response=json.loads(appointment_detail.text)
        appointment_details=appointment_detail_response['data']
        print("detail api :",appointment_detail.status_code)

        # calling create discussion api
        if request.method == 'POST' :
            # limit=request.form['form_type']
            # print(limit)
            if limit != 3:
                discuss_text=request.form['discuss_text']
                create_payload={
                        "appointment_id":appointment_id,
                        "content":discuss_text,
                        "is_query":0,
                        "is_reply":1,
                        "doctor_id":doctor_id
                    }
                create_api_data=json.dumps(create_payload)
                print("create discussion payload",create_api_data)
                create_discussion_request=requests.post(base_url+create_discussion_api, data=create_api_data, headers=headers)
                create_discussion_response=json.loads(create_discussion_request.text)
                print("create discussion", create_discussion_request.status_code)
                print(create_discussion_request.text)
                return redirect(url_for('discussion',appointment_id=appointment_id))
            else :
                flash("You have reached discussion limit","info")
        return render_template("discussion.html",discussion_list=discussion_list,appointment_details=appointment_details,
        limit=limit)
    except Exception as e:
        print(e)
    return render_template("discussion.html")

@app.route("/payouts/<currency>")
def payouts(currency): 
    try:
        print(currency)
        headers={
        "Content-Type":"application/json"
        }
        
        payout_payload={
            "doctor_id":"",
            "payout_status":"",
            "currency": currency
        }
        payout_json_data=json.dumps(payout_payload)
        print(payout_json_data)
        payout_request=requests.post(base_url+payout_list_api, data=payout_json_data, headers=headers)
        print("payout list api:",payout_request.status_code)
        payout_response=json.loads(payout_request.text)
        payouts=payout_response['data']
        # print("payouts",payouts)
        
        payout_data=payouts['payouts']
        # print("payouts list",payout_data)
        approved_payouts=payouts['earnings']

        payout_payload={
            "doctor_id":"",
            "payout_status":0,
            "currency":currency
        }
        payout_json_data=json.dumps(payout_payload)
        print(payout_json_data)
        payout_request=requests.post(base_url+payout_list_api, data=payout_json_data, headers=headers)
        print("payout list api:",payout_request.status_code)
        payout_response=json.loads(payout_request.text)
        payouts=payout_response['data']
        # print("payouts",payouts)        
        new_payouts=payouts['payouts']

        payout_payload={
            "doctor_id":"",
            "payout_status":2,
            "currency":currency
        }
        payout_json_data=json.dumps(payout_payload)
        print(payout_json_data)
        payout_request=requests.post(base_url+payout_list_api, data=payout_json_data, headers=headers)
        print("payout list api:",payout_request.status_code)
        payout_response=json.loads(payout_request.text)
        payouts=payout_response['data']
        # print("payouts",payouts)        
        rejected_payouts=payouts['payouts']

        #calling inticure earnings api
        ie_payload={
            "currency":currency
        }
        payout_json_data=json.dumps(ie_payload)
        print(payout_json_data)
        inticure_earnings_req=requests.post(base_url+inticure_earnings_api,data=payout_json_data,headers=headers)
        print("Inticure earnings api:",inticure_earnings_req.status_code)
        inticure_earnings_resp=json.loads(inticure_earnings_req.text)
        inticure_earnings=inticure_earnings_resp['data']
        print(inticure_earnings)
        return render_template("payouts.html",payouts=payout_data,approved_payouts=approved_payouts,
        new_payouts=new_payouts, rejected_payouts=rejected_payouts,inticure_earnings=inticure_earnings,currency=currency)
    except Exception as e:
        print("Exception : ",e)
        return redirect(url_for('error_page'))

@app.route("/payout_details/<int:payout_id>")
def payout_details(payout_id):
    try:
        print("Payout id:",payout_id)
        headers={
        "Content-Type":"application/json"
        }
        payout_payload={
            "payout_id":payout_id
        }
        payout_json_data=json.dumps(payout_payload)
        print(payout_json_data)
        payout_request=requests.post(base_url+payout_details_api, data=payout_json_data, headers=headers)
        print("payout details api:",payout_request.status_code)
        payout_response=json.loads(payout_request.text)
        payout_details=payout_response['data']
        print("payouts",payout_details)
        return render_template("payout_details.html",payout_details=payout_details)
    except Exception as e:
        print("Exception in payout details: ",e)
        return redirect(url_for('error_page'))

@app.route("/payout_approval/<int:doctor_id>/<int:payout_id>/<int:payout_status>", methods=['GET','POST'])
def payout_approval(doctor_id,payout_status,payout_id):
    try:
        
        print("doctor id" , doctor_id)
        print("payout id" , payout_id)
        print("payout status", payout_status)
        headers={
        "Content-Type":"application/json"
        }
        payout_payload={
            "doctor_id":doctor_id,
            "payout_id":payout_id,
            "payout_status":payout_status
        }
        api_data=json.dumps(payout_payload)
        print("request:",api_data)
        approval_req=requests.post(base_url+payout_approval_api,data=api_data,headers=headers)
        print("payout approval api:", approval_req.status_code)
        approval_resp=json.loads(approval_req.text)
        print(approval_resp)
        if approval_resp['response_code']==200:
            flash("Payout approved","success")
        else:
            flash("Something went wrong","error")
        return redirect(url_for("payouts",currency='inr'))
    except Exception as e:
        print("Exception in payout approval: ",e)
        return redirect(url_for('error_page'))

@app.route("/earnings")
def earnings():
    return render_template("earnings.html")

@app.route("/earnings_details")
def earnings_details():
    return render_template("earnings_details.html")

@app.route("/transactions/<currency>")
def transactions(currency):
    try:
        headers={
        "Content-Type":"application/json"
        }
        payload={ "currency":currency}
        data=json.dumps(payload)
        transactions_req=requests.post(base_url+transaction_list_api,data=data,headers=headers)
        print(transactions_req.status_code)
        transactions_resp=json.loads(transactions_req.text)
        transactions=transactions_resp['data']
        print(transactions)
        # 1:pending, 2:paid, 3:refunded, 0:NA
        return render_template("transactions.html",transactions=transactions)
    except Exception as e:
        print(e)
    return render_template("transactions.html")

@app.route("/transaction_details")
def transaction_details():
    try:
        headers={
        "Content-Type":"application/json"
        }
        transactions_req=requests.post(base_url+transaction_details_api,headers=headers)
        print(transactions_req.status_code)
        transactions_resp=json.loads(transactions_req.text)
        transactions=transactions_resp['data']
        return render_template("transaction_details.html",transactions=transactions)
    except Exception as e:
        print(e)
    return render_template("transaction_details.html")

@app.route("/plans")
def plans():
    headers={
        "Content-Type":"application/json"
        }
    plans_req=requests.get(base_url+plans_api,headers=headers)
    print(plans_req.status_code)
    plans_resp=json.loads(plans_req.text)
    plans=plans_resp['data']
    # calling location api 
    location_req=requests.get(base_url+locations_api, headers=headers)
    print("locations",location_req.status_code)
    location_resp=json.loads(location_req.text)
    print(location_req.status_code)
    print(location_resp)
    print('plans',plans)
    locations=location_resp['data']

    return render_template("plans.html",plans=plans,locations=locations)
    
@app.route("/add_plan", methods=['GET','POST'])
def add_plan():
    headers={
        "Content-Type":"application/json"
        }
    
    # Specializations list api call
    specialization_request=requests.get(base_url+specialization_list_api, headers=headers)
    specialization_response=json.loads(specialization_request.text)
    print("specialization list api",specialization_request.status_code)
    specializations=specialization_response['data']
    doctors_request = requests.get(base_url+doctors_api, headers=headers)
    doctors_response = json.loads(doctors_request.text)
    doctors = doctors_response['data']
    print(doctors)
    # print(specializations)

    # Calling location api 
    location_req=requests.get(base_url+locations_api, headers=headers)
    print("locations",location_req.status_code)
    location_resp=json.loads(location_req.text)
    print(location_req.status_code)
    print(location_resp)
    locations=location_resp['data']
    if request.method == 'POST':
        print('post')
        doctor=request.form['plan_name']
        price=request.form['plan_price']
        location=request.form['location']
        print(doctor)
        doctor_profile_id, doc_name, specialization = doctor.split('|')
        payload={
            "price_for_single": price,
            "price_for_couple": math.ceil(float(price)*1.75),
            "doctor_id":str(doctor_profile_id),
            "location_id":location,
            "doc_name":doc_name,
            "speciality":specialization
        }
        api_data=json.dumps(payload)
        print("payload", api_data)
        plans_req=requests.post(base_url+plans_api+'/', data=api_data,headers=headers)
        print(plans_req.status_code)
        plans_resp=json.loads(plans_req.text)
        print(plans_resp)
        if plans_resp['response_code']==200:
            flash("Plan created","success")
            return redirect(url_for('add_plan'))
        elif plans_resp['response_code'] == 401:
            flash("plan is already exits, better try edit", "warning")
            return redirect(url_for("plans"))
        else:
            flash("Something went wrong..","error")
    return render_template("create_plan.html",locations=locations,specializations=specializations,doctors=doctors)

@app.route("/edit_plan", methods=['GET','POST'])
def edit_plan():
    doctor_id = request.args.get('doctor_id')
    location_id = request.args.get('location_id')
   
    headers={
        "Content-Type":"application/json"
        }
    payload = {
        "plan_id":doctor_id,
        "location_id":location_id
    }
    api_data=json.dumps(payload)
    print("payload", api_data)
    plans_req=requests.post(base_url+get_plan,data=api_data,headers=headers)
    print(plans_req.status_code)
    plans_resp=json.loads(plans_req.text)
    # plans=plans_resp['data']
    print('plans2',plans_resp)

    location_req=requests.get(base_url+locations_api, headers=headers)
    print("locations",location_req.status_code)
    location_resp=json.loads(location_req.text)
    print(location_req.status_code)
    print('2287 ',location_resp)
    locations=location_resp['data']

    if request.method == 'POST':
        price=request.form['plan_price']
        duration=request.form['duration']
        payload={
            "doc_id":doctor_id,
            "price_for_single":price,
            "price_for_couple": math.ceil(float(price)*1.75),
            "location_id":location_id,
            "duration":duration
        }
        print(payload)
        try:
            api_data=json.dumps(payload)
            plans_req=requests.post(base_url+edit_plan_api,data=api_data, headers=headers)
            print(plans_req.status_code)
            plans_resp=json.loads(plans_req.text)
            print(plans_resp)
            if plans_resp['response_code']==200:
                flash("Plan updated","success")
            else:
                flash("Something went wrong..","error")
        except Exception as e:
            flash("select a proper plan","warning")
            print(e)
        # return redirect(url_for('plans'))
    return render_template("edit_plan.html",plans=plans_resp,locations=locations)

@app.route("/remove_plan", methods=['GET','POST'])
def remove_plan():
    headers={
        "Content-Type":"application/json"
        }
    doctor_id = request.args.get('doctor_id')
    location_id = request.args.get('location_id')
    print('doctor_id',doctor_id)
    print('location_id',location_id)

    payload={
        "doc_id":doctor_id,
        "location_id":location_id
    }
    print(payload)
    api_data=json.dumps(payload)
    remove_request=requests.post(base_url+remove_plan_api,data=api_data, headers=headers)
    remove_response=json.loads(remove_request.text)
    print("delete plan api",remove_request.status_code)
    print(remove_response)
    if remove_response['response_code']==200:
        flash("Plan deleted","success")
    else:
        flash("select an available plan","error")
    return redirect(url_for('plans'))
    # return render_template("remove_plan.html")

@app.route("/plan_details")
def plan_details():
    return render_template("plan_details.html")

@app.route("/specializations")
def specializations():
    headers={
        "Content-Type":"application/json"
        }
    #specializations list api call
    print(base_url+specialization_list_api)
    specialization_request=requests.get(base_url+specialization_list_api, headers=headers)
    specialization_response=json.loads(specialization_request.text)
    print("specialization list api",specialization_request.status_code)
    specializations=specialization_response['data']
    print(specializations)
    return render_template("specializations.html",specializations=specializations)

@app.route("/add_specialization",methods=['GET','POST'])
def add_specialization():
    headers={
        "Content-Type":"application/json"
        }
    if request.method == "POST":
        specialization=request.form['specialization']
        description=request.form['description']

        payload={
            "specialization":str(specialization).lower(),
            "description":description,
        }
        api_data=json.dumps(payload)
        #add specialization api call (specialization list api with post method)
        spec_request=requests.post(base_url+specialization_list_api+'/', data=api_data, headers=headers)
        print("add specialization api",spec_request.status_code)
        spec_response=json.loads(spec_request.text)
        print("add specialization api",spec_request.status_code)
        flash("New specialization added","success")
        return redirect(url_for('specializations'))
    return render_template("add_specialization.html")

@app.route("/edit_specialization/<int:spec_id>",methods=['GET','POST'])
def edit_specialization(spec_id):
    headers={
        "Content-Type":"application/json"
        }
    #specializations list api call
    specialization_request=requests.get(base_url+specialization_list_api, headers=headers)
    specialization_response=json.loads(specialization_request.text)
    print("specialization list api",specialization_request.status_code)
    specializations=specialization_response['data']
    print(specializations)
    for spec in specializations:
        edit={}
        if spec['id'] == spec_id:
            spec_to_edit=spec['specialization']
            description_to_edit=spec['description']
            # edit={
            # "spec_to_edit":spec['specialization'],
            # "description_to_edit":spec['description'],
            # "slot_duration_to_edit":spec['time_duration']
            # }
    edit_specialization_api=specialization_list_api+f'/{spec_id}/'
    print(base_url+specialization_list_api+f'/{spec_id}/')
    # when specialization is edited
    if request.method == "POST":
        specialization=request.form['specialization']
        description=request.form['description']

        payload={
            "specialization":str(specialization).lower(),
            "description":description,
        }
        api_data=json.dumps(payload)
        print(api_data)
        #edit specialization api call (specialization list api with patch method)
        spec_request=requests.patch(base_url+edit_specialization_api, data=api_data, headers=headers)
        print("edit specialization api",spec_request.status_code)
        spec_response=json.loads(spec_request.text)
        print("edit specialization api",spec_request.status_code)
        print(spec_response) 
        flash("Specialization edited","success")
        return redirect(url_for('specializations'))   
    return render_template("edit_specialization.html",specializations=specializations,spec_to_edit=spec_to_edit,
    description_to_edit=description_to_edit)

@app.route("/remove_specialization/<int:spec_id>",methods=['GET','POST'])
def remove_specialization(spec_id):
    print(spec_id)
    headers={
        "Content-Type":"application/json"
        }
    delete_specialization_api=specialization_list_api+f'/{spec_id}/'
    #delete specialization api call (specialization list api with delete method)
    spec_request=requests.delete(base_url+delete_specialization_api, headers=headers)
    spec_response=json.loads(spec_request.text)
    print("delete specialization api",spec_request.status_code)
    print(spec_response)
    flash("Specialization deleted","success")
    return redirect(url_for('specializations'))
    # return render_template("remove_specialization.html")
@app.route("/pricing_details")
def pricing_details():
    return render_template('pricing_details.html')

@app.route("/locations")
def locations():    
    headers={
        "Content-Type":"application/json"
        }
    location_req=requests.get(base_url+locations_api, headers=headers)
    print("locations",location_req.status_code)
    location_resp=json.loads(location_req.text)
    print(location_req.status_code)
    print(location_resp)
    locations=location_resp['data']
    return render_template("locations.html",locations=locations)

@app.route("/add_location",methods=['GET','POST'])
def add_location():
    headers={
        "Content-Type":"application/json"
        }
    if request.method == "POST":
        location=request.form['location']
        currency=request.form['currency']
        country_code=request.form['country_code']
        payload={
            "location":location,
            "currency":currency,
            "country_code":country_code
        }
        api_data=json.dumps(payload)
        print(api_data)
        #add location api call (location list api with post method)
        add_location_request=requests.post(base_url+locations_api+'/', data=api_data, headers=headers)
        add_location_response=json.loads(add_location_request.text)
        print("add location api",add_location_request.status_code)
        flash("New location added","success")
        return redirect(url_for('locations'))
    return render_template("add_location.html")

@app.route("/edit_location/<int:location_id>",methods=['GET','POST'])
def edit_location(location_id):
    print("edit id",location_id)
    headers={
        "Content-Type":"application/json"
        }
    location_req=requests.get(base_url+locations_api, headers=headers)
    print(location_req.status_code)
    location_resp=json.loads(location_req.text)
    print(location_req.status_code)
    print(location_resp)
    locations=location_resp['data']
    edit={}
    for location in locations:
        if location_id == location['location_id']:
            edit={
            "location_to_edit":location['location'],
            "currency_to_edit":location['currency'],
            "code_to_edit":location['country_code']
            }

    if request.method == "POST":
        location=request.form['location']
        currency=request.form['currency']
        country_code=request.form['country_code']
        payload={
            "location":location,
            "currency":currency,
            "country_code":country_code
        }
        api_data=json.dumps(payload)
        #edit location api call (location list api with post method)
        edit_location_request=requests.patch(base_url+locations_api+f'/{location_id}/', data=api_data, headers=headers)
        print("edit location api",edit_location_request.status_code)
        edit_location_response=json.loads(edit_location_request.text)
        print("edit location api",edit_location_request.status_code)
        flash("Location edited","success")
        return redirect(url_for('locations'))
    return render_template("edit_location.html",locations=locations
    ,edit=edit)

@app.route("/remove_location/<int:location_id>",methods=['GET','POST'])
def remove_location(location_id):
    headers={
        "Content-Type":"application/json"
        }
    print("remove id",location_id)
    #delete location api call (location list api with post method)
    delete_location_request=requests.delete(base_url+locations_api+f'/{location_id}/', headers=headers)
    delete_location_response=json.loads(delete_location_request.text)
    print("delete location api",delete_location_request.status_code)
    print(delete_location_response)
    flash("Location deleted","success")
    return redirect(url_for('locations'))

@app.route("/refund/<currency>",methods=['POST','GET'])
def refund(currency):
    api="https://api.inticure.online/api/administrator/refund/"
    "?date_from=2023-03-15&date_to=2023-03-29&limit=5&refund_id=2023-03-16-0008&status=0"
    try:
        print(currency)
        headers={
        "Content-Type":"application/json"
        }
        # refund_api_pgload=refund_api+"?date_from=&date_to=&limit=5&refund_id=&status="
        refund_api_pgload=refund_api+"?date_from=&date_to=&limit=5&refund_id=&status=&currency="+currency
        print(refund_api_pgload)
        refund_req=requests.get(base_url+refund_api_pgload,headers=headers)
        print(refund_req.status_code)
        refund_resp=json.loads(refund_req.text)
        print(refund_resp)

        # Taking pagination from response        
        next=refund_resp['next']
        prev=refund_resp['previous']
        refund_data=refund_resp['results']

        # if request.method == "POST":
        #     print('post')
        #     # getting data from refund pop up
        #     refund_id=request.form['refund_id']
        #     status=request.form['refund_status'] 
        #     print(refund_id)  
        #     #  getting data from filters
        #     status_filter = request.form['status']
        #     print(status_filter)
        #     if status_filter == None:
        #         status_filter = ""
                
        #     from_d = request.form['from']
        #     print(from_d)
        #     to_d = request.form['to']
        #     print(to_d)
            
        #     payload={
        #         "status":int(status)
        #     }
        #     api_data=json.dumps(payload)
        #     print(api_data)
        #     api_url=base_url+"?date_from="+from_d+"&date_to="+to_d+"&limit=5&refund_id="+refund_id+"&status="+status_filter
        #     print(api_url)
        #     ref_stat_req=requests.post(api_url,data=api_data,headers=headers)
        #     print(ref_stat_req.status_code)
        #     ref_stat_resp=json.loads(ref_stat_req.text)
        #     print(ref_stat_resp)
        #     # return render_template("refund.html",next=next,prev=prev,refund_data=refund_data)
        #     return redirect(url_for('refund'))
            
        return render_template("refund.html",next=next,prev=prev,refund_data=refund_data,currency=currency)
    except Exception as e:
        print("refund exception",e)
        return render_template("refund copy.html")
    # return render_template("refund.html")


@app.route("/languages",methods=['GET','POST'])
def languages():
    try:
        # listing
        headers={
        "Content-Type":"application/json"
        }
        # language api call
        language_api_request=requests.get(base_url+language_api,headers=headers)
        print("language api",language_api_request.status_code)
        language_api_response=json.loads(language_api_request.text)
        languages=language_api_response['data']
        print(languages)
       
        try:
            if request.method == 'POST':
                 # add language
                if request.form['form_type'] == "add":
                    print('post')
                    language=request.form['language']
                    
                    payload={
                        "language":language
                        
                    }
                    api_data=json.dumps(payload)
                    print("payload", api_data)
                    add_lang_req=requests.post(base_url+language_api+'/', data=api_data,headers=headers)
                    print(add_lang_req.status_code)
                    add_lang_resp=json.loads(add_lang_req.text)
                    # print(add_lang_resp)
                    if add_lang_resp['response_code'] == 200:
                        flash("Language added","success")
                    else:
                        flash("Something went wrong..","error")
                    return redirect(url_for('languages'))
                
                # edit / update language                
                if request.form['form_type'] == "update":
                    print("edit")
                    lang_id=request.form['lang_id']
                    language=request.form['language']
                    payload={
                        "language":language
                    }
                    api_data=json.dumps(payload)
                    print("payload", api_data)
                    edit_lang_req=requests.patch(base_url+language_api+'/'+lang_id+'/', data=api_data,headers=headers)
                    print(edit_lang_req.status_code)
                    edit_lang_resp=json.loads(edit_lang_req.text)
                    # print(edit_lang_resp)
                    if edit_lang_resp['response_code'] == 200:
                        flash("Language edited","success")
                    else:
                        flash("Something went wrong..","error")
                    return redirect(url_for('languages'))

        except Exception as e:
            print("post",e)
            return render_template("languages.html",languages=languages)
        
        return render_template("languages.html",languages=languages)
    except Exception as e:
        print(e)
        return render_template("languages.html",languages=languages)
        # return redirect(url_for("error_page"))

@app.route("/remove_language/<int:lang_id>") 
def remove_language(lang_id):
    headers={
        "Content-Type":"application/json"
        }
    try:
        print(lang_id)
        remove_request=requests.delete(base_url+language_api+f'/{lang_id}/', headers=headers)
        remove_response=json.loads(remove_request.text)
        print("delete plan api",remove_request.status_code)
        print(remove_response)
        if remove_response['response_code']==200:
            flash("Language deleted","success")
        else:
            flash("something went wrong","error")
        return redirect(url_for('languages'))
    except Exception as e:
        print(e)
        flash("Something went wrong","error")
        return redirect(url_for('languages'))


@app.route("/add_language", methods=['GET','POST'])
def add_language():
    try:
        headers={
            "Content-Type":"application/json"
            }
        # calling location api 
        # location_req=requests.get(base_url+locations_api, headers=headers)
        # print("locations",location_req.status_code)
        # location_resp=json.loads(location_req.text)
        # print(location_req.status_code)
        # print(location_resp)
        # locations=location_resp['data']
        if request.method == 'POST':
            print('post')
            language=request.form['language']
            
            payload={
                "language":language
                
            }
            api_data=json.dumps(payload)
            print("payload", api_data)
            add_lang_req=requests.post(base_url+language_api+'/', data=api_data,headers=headers)
            print(add_lang_req.status_code)
            add_lang_resp=json.loads(add_lang_req.text)
            print(add_lang_resp)
        return render_template("add_language.html")
    except Exception as e:
        print(e)
        return redirect(url_for('error_page'))

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/customer_appointments")
def customer_appointments():
    return render_template("customer_appointments.html")

@app.route("/error_400")
def error_page():
    return render_template("404_error_page.html")


if __name__ == '__main__':
    app.run(port=8005,debug = True)