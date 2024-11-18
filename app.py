from flask import Flask, jsonify, request
import json
from flask_cors import CORS
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import psycopg2  
from constants import DB_HOST, DB_NAME, DB_USER, DB_PASS
from threading import Thread

app = Flask(__name__)

CORS(app)

def get_db_connection(): # * config
    try:
        postgres = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return postgres
    
    except Exception as e:
        print(e)

# @app.errorhandler(404)
# def page_not_found(e):
#     return jsonify(message='Undefined route, 404'), 404 # * this code causes this error: Undefined route, 404.

@app.route("/", methods=["GET"])
def root():
    try:
        response = {
            "message": "Monitoring system api",
            "status": "ok",
            "version": "1.0.0" 
        }
        return jsonify(response), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  

# * time 
@app.route("/get_time", methods=["GET"]) 
def get_time():
    try:
        # current_time = datetime.now().strftime("%H:%M:%S")
        # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        israel_time_and_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        return jsonify(time=israel_time_and_date)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  

# * nodes
@app.route("/api/v1/root_nodes", methods=["GET"])
def get_nodes():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor) 

        cursor.execute("SELECT * FROM nodes WHERE parent is null")
        response = cursor.fetchall()  

        return jsonify(response), 200
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500 
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/nodes/<id>", methods=["GET"]) # * get specific node.
def specified_node(id):
    try:   
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM nodes WHERE parent = %s", (id,))
        nodes = cursor.fetchall()

        cursor.execute("SELECT DISTINCT ON (report_id) id, report_id, parent, title, description, value, time FROM reports WHERE parent = %s ORDER BY report_id, time DESC;", (id,))
        reports = cursor.fetchall()

        return jsonify(nodes=nodes, reports=reports), 200
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500 
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/only/nodes/<id>", methods=["GET"]) # * get only nodes under specified parent.
def get_only_nodes(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM nodes WHERE parent = %s", (id,))
        nodes = cursor.fetchall()

        return jsonify(nodes), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500 
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/node/name/<id>", methods=["GET"])
def get_node_name(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select distinct(title) from nodes where node_id = %s", (id,))
        specified_node_name = cursor.fetchone()

        return jsonify(specified_node_name), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/post/nodes", methods=["POST"])
def post_data():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        data = request.get_json()

        title = data.get('title')
        description = data.get('description')
        parent = data.get('parent')

        cursor.execute("SELECT * FROM reports WHERE parent = %s", (parent,))
        nodes = cursor.fetchone()

        print(nodes)

        if parent and nodes:
            return jsonify(message="Cannot create node: a report with the same parent already exists."),400

        cursor.execute(
            "INSERT INTO nodes (title, description, parent) VALUES (%s, %s, %s) RETURNING *;",
            (title, description, parent)
        )

        postgres.commit()

        new_node = cursor.fetchone()
        return jsonify(new_node), 201  

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()


@app.route("/api/v1/delete/node/<id>", methods=["DELETE"]) #! delete
def delete_node(id): # TODO make that you can't delete nodes if they have rules under them. 
    try:
        print(type(id))
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("delete from nodes where node_id = %s", (id,))

        postgres.commit()

        return jsonify({"message": "Node deleted successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()     

# ? reports
@app.route("/api/v1/latest/reports", methods=["GET"]) # * get latest reports , in a distinct way.
def get_latest_reports():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select distinct on (title) title, time, value from reports order by title, time desc;")
        latest_reports = cursor.fetchall()

        return jsonify(latest_reports)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/get/reports", methods=["GET"]) 
def get_reports():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select * from reports")
        response = cursor.fetchall()

        return jsonify(response)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/report/graph/<id>", methods=["GET"])
def report_graph(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select * from reports where report_id = %s order by time desc", (id,))
        tiime_series_report = cursor.fetchall()

        return jsonify(tiime_series_report),200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/get/reports/distinct/null", methods=["GET"])
def distinct_reports():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select distinct(report_id), title, description, parent from reports where parent is null");
        response = cursor.fetchall()
        
        return jsonify(response), 200
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/get/reports/distinct/parent", methods=["GET"])
def distinct_reports_parent():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select distinct(report_id), title, description, parent from reports where parent is not null");
        response = cursor.fetchall()
        
        return jsonify(response), 200
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()


@app.route("/api/v1/post/reports", methods=["POST"])  #* post
def post_report():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        data = request.get_json()

        report_id = data.get('report_id')
        title = data.get('title')
        description = data.get('description')
        parent = data.get('parent')
        value = data.get('value')

        cursor.execute("SELECT * FROM nodes WHERE parent = %s", (parent,))
        response = cursor.fetchone()

        if parent and response != None: # ! if it will find a node with same parent throw an error, can't have nodes and report in the same place.
            return jsonify({'message': 'Cannot create report: a node with the same parent already exists'}), 400
        elif parent:

            cursor.execute("SELECT * FROM reports WHERE report_id = %s", (report_id,))
            response = cursor.fetchall()

            if response: # * checking if the report posted is already attached to other parent .
                for report in response:
                    if report['parent'] is not None and report['parent'] != parent:
                        return jsonify({'message': 'Report can be associated only to 1 parent'}), 400
            
            cursor.execute("SELECT * FROM reports WHERE parent = %s", (parent,))
            reports_with_specified_parent = cursor.fetchall()

            if reports_with_specified_parent:
                for report in reports_with_specified_parent:
                    if report['parent'] is not None and report['report_id'] != report_id:  
                        # print(report)     
                        return jsonify({'message': 'Only 1 report can be under a specified node'}), 400

            cursor.execute(
                "INSERT INTO reports (report_id, title, description, parent, value) VALUES (%s, %s, %s, %s, %s) RETURNING *;",
                (report_id, title, description, parent, value)
            )
            postgres.commit()  

            new_node = cursor.fetchone()

            evaluate_report_rules(report_id, value, parent)

            return jsonify(new_node), 201 

        else:

            cursor.execute("SELECT * FROM reports WHERE report_id = %s", (report_id,))
            response = cursor.fetchall()  

            report_parent = None
            for item in response:
                # print(item)
                if item['parent'] != None:
                    report_parent = item['parent']
                    break

            # print(f'old parent {parent}, new parent {report_parent}')

            cursor.execute(
                "INSERT INTO reports (report_id, title, description, parent, value) VALUES (%s, %s, %s, %s, %s) RETURNING *;",
                (report_id, title, description,  report_parent, value)
            )

            postgres.commit()

            new_node = cursor.fetchone()

            evaluate_report_rules(report_id, value, report_parent)

            return jsonify(new_node), 201  

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()


@app.route("/api/v1/delete/report/<id>", methods=["DELETE"]) # ! delete the entire report!
def delete_reports(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("delete from reports where report_id = %s", (id,))

        postgres.commit()

        return jsonify({"message": "Node deleted successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/remove/report/null/<id>", methods=["PATCH"]) #TODO check if report has rules before allowing to remove him
def set_report_to_null(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select * from reports where parent is not null and report_id = %s", (id,))
        report = cursor.fetchone()
        report_parent = report['parent']
   
        cursor.execute("update reports set parent = null where report_id = %s", (id,))  

        postgres.commit()

        cursor.execute("select * from report_rules where report_id = %s", (id,))
        rules = cursor.fetchone()
        
        if rules:
            cursor.execute("delete from report_rules where report_id = %s", (id,))
            postgres.commit()

        if report_parent:
            cursor.execute("update nodes set status = 'expired' where node_id = %s", (report_parent,))
            postgres.commit()

        return jsonify(message='report removed successfully'), 204

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()

    
# * report rules 
@app.route("/api/v1/get/rules/<id>", methods=["GET"])
def get_specific_report_rules(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select * from report_rules where report_id = %s", (id,))
        report_rules = cursor.fetchall()

        return jsonify(report_rules), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/post/report/rules", methods=["POST"])
def post_rule():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        data = request.get_json()

        report_id = data.get('report_id')
        condition_operator = data.get('condition_operator')
        threshold = data.get('threshold')
        action = data.get('action')

        if not report_id or not condition_operator or not threshold or not action:
            return jsonify({'message': 'All fields (report_id, condition_operator, threshold, action) are required.'}), 400


        cursor.execute(
            "INSERT INTO report_rules (report_id, condition_operator, threshold, action) VALUES (%s, %s, %s, %s) RETURNING *;",
            (report_id, condition_operator, threshold, action)
        )
        postgres.commit()

        new_rule = cursor.fetchone()

        return jsonify(new_rule), 201

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()

def evaluate_report_rules(report_id, report_value, parent_node_id):
    try:
        # print(f'report id: {report_id}, value: {report_value}, parent_node:  {parent_node_id}')
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM report_rules WHERE report_id = %s", (report_id,))
        rules = cursor.fetchall()

        # print(rules)
        if rules == []: # ! if rules are empty make parent expired
            # print('no rules found')
            cursor.execute("UPDATE nodes SET status = 'expired' WHERE node_id = %s", (parent_node_id,))
            postgres.commit()

            return jsonify(message='rules deleted successfully')

        # print(f'rules are: {rules}')

        for rule in rules:
            condition_operator = rule['condition_operator']
            threshold = rule['threshold']
            action = rule['action']

            condition_met = False
            if condition_operator == '<' and report_value < threshold:
                condition_met = True
            elif condition_operator == '>' and report_value > threshold:
                condition_met = True
            elif condition_operator == '=' and report_value == threshold:
                condition_met = True
            elif condition_operator == '<=' and report_value <= threshold:
                condition_met = True
            elif condition_operator == '>=' and report_value >= threshold:
                condition_met = True

            if condition_met: #TODO add more action types in the future.
                if action == 'set_parent_status_up':
                    cursor.execute("UPDATE nodes SET status = 'up' WHERE node_id = %s", (parent_node_id,)) 
                elif action == 'set_parent_status_down':
                    cursor.execute("UPDATE nodes SET status = 'down' WHERE node_id = %s", (parent_node_id,))
                elif action == 'set_parent_status_critical':
                    cursor.execute("UPDATE nodes SET status = 'critical' WHERE node_id = %s", (parent_node_id,))

                postgres.commit()

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()

@app.route("/api/v1/delete/report/rules/<id>", methods=["DELETE"])
def delete_report_rules(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        data = request.get_json()

        parent_node_id = data.get('parent')
        report_id = data.get('report_id')

        cursor.execute("delete from report_rules where rule_id = %s", (id,))

        postgres.commit()

        cursor.execute("select * from report_rules where report_id = %s", (report_id,))
        rules = cursor.fetchall()
        # print(rules)
        if rules == []: # ! if rules are empty make parent expired
            # print('no rules found')
            cursor.execute("UPDATE nodes SET status = 'expired' WHERE node_id = %s", (parent_node_id,))
            postgres.commit()

            return jsonify(message='rules deleted successfully'),200

        return jsonify(message='rule deleted successfully'),200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()

def expired_tree_thread():
    try: 
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select distinct on (report_id) report_id, parent, title, description, time from reports where parent is not null order by report_id, time desc;")
        reports_with_parent = cursor.fetchall()

        for report in reports_with_parent: 
            report_id = report["report_id"]
            report_time = report["time"]
            parent = report["parent"] # TODO if time is more than 30, means data is expired, update to upper node.

            current_time = datetime.now()
            time_difference = current_time - report_time

            if time_difference < timedelta(minutes=30):
                print(f"Report {report_id} is recent (time: {report_time}).")
            else:
                print(f"Report {report_id} is expired (time: {report_time}).")
                cursor.execute("update nodes set status = 'expired' where node_id = %s", (parent,))
                postgres.commit()
   
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        postgres.close()

thread = Thread(target=(expired_tree_thread))
thread.start()
 
# * node rules
@app.route("/api/v1/post/node/rules/<id>", methods=["POST"]) # * post
def post_node_rules(id):
    try:
        # print(id)
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)
        
        data = request.get_json()

        if not data:
            return jsonify(message='no data in body'),404
        
        conditions = data.get('conditions')
        action = data.get('action')
        jsoned_conditions = json.dumps(conditions)

        if not conditions or not action:
            return jsonify(message='must provide action and conditions'), 400

        cursor.execute(
            "INSERT INTO node_rules (parent_node_id, conditions, action) VALUES (%s, %s, %s) RETURNING *;",
            (id, jsoned_conditions, action)
        )

        postgres.commit()
        new_rule = cursor.fetchone()
        return jsonify(new_rule), 201  

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()

# * get specific node rule
@app.route("/api/v1/get/node/rules/<id>", methods=["GET"])
def get_specific_node_rule(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select * from node_rules where parent_node_id = %s", (id,))
        specified_node_rules = cursor.fetchall()
        return jsonify(specified_node_rules), 200
    
    except Exception as e:
        print(e)
        print('error')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()

def thread_evaluation(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute('select * from nodes where parent = %s', (id,))
        sub_nodes =  cursor.fetchall()
 
        cursor.execute('select * from node_rules where parent_node_id = %s', (id,))
        rules = cursor.fetchall()


        nodes_and_their_status = {node['node_id']: node['status'] for node in sub_nodes}

        for rule in rules:
            condition = rule['conditions']
            action = rule['action']
            if threaded_evaluate_rules(condition, action, nodes_and_their_status): # * return true if there is a match.

                if action == "set_parent_status_up":

                    cursor.execute("update nodes set status = 'up' where node_id = %s", (id,))
                    postgres.commit()

                elif action == "set_parent_status_down":

                    cursor.execute("update nodes set status = 'down' where node_id = %s", (id,))
                    postgres.commit()

                elif action == "set_parent_status_critical":

                    cursor.execute("update nodes set status = 'critical' where node_id = %s", (id,))
                    postgres.commit()
  
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()

def threaded_evaluate_rules(condition, action, nodes_and_their_status):
    operator = condition['operator']
    node_conditions = condition['conditions']

    if operator == 'AND':
        result = all(nodes_and_their_status.get(cond['node_id']) == cond['status'] for cond in node_conditions)
        return result

    elif operator == 'OR':
        result = any(nodes_and_their_status.get(cond['node_id']) == cond['status'] for cond in node_conditions)
        return result
    
def rules_evaluation_thread(): #TODO , consider making it run as a threaded process.
    try: 
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        while True:
            cursor.execute("select distinct (node_id) from nodes")
            node_ids = cursor.fetchall()

            for item in node_ids:
                node_id = item['node_id']
                thread_evaluation(node_id) # TODO might want to use threads, consider using it in the future.
                
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        postgres.close()


thread = Thread(target=rules_evaluation_thread)
thread.start()
 
# ! delete node rule
@app.route("/api/v1/delete/node/rule/<id>", methods=["DELETE"])
def delete_node_rules(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("delete from node_rules where rule_id = %s ", (id,))
        postgres.commit()

        return jsonify(message='rules deleted successfully')

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()
    
@app.route("/api/v1/check/rules/parent/node/<id>", methods=["DELETE"])
def check_parent_node_rules(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select * from node_rules where parent_node_id = %s", (id,))
        rules_related_to_parent = cursor.fetchone()

        if rules_related_to_parent == None:
            # print(rules_related_to_parent)
            cursor.execute("update nodes set status = 'expired' where node_id = %s", (id,))
            postgres.commit()

        return jsonify(message='rules have been evaluated'), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()

if __name__ == "__main__":
    app.run(debug=True, port=80) #TODO when app is ready, change debug to false.
  
