
from flask import Flask, jsonify, redirect, render_template, request
import json
from flask_cors import CORS
from psycopg2.extras import RealDictCursor
from datetime import datetime
import psycopg2  
from constants import DB_HOST, DB_NAME, DB_USER, DB_PASS 

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

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(message='Undefined route, 404'), 404

# * time 
@app.route("/get_time", methods=["GET"]) 
def time():
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
            return jsonify(message="Cannot create node: a report with the same parent already exists.")

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
                        print(report)     
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
                print(item)
                if item['parent'] != None:
                    report_parent = item['parent']
                    break

            print(f'old parent {parent}, new parent {report_parent}')

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


@app.route("/api/v1/delete/report/<id>", methods=["DELETE"]) # ! delete
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

    
# * rules 
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
        print(f'report id: {report_id}, value: {report_value}, parent_node:  {parent_node_id}')
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM report_rules WHERE report_id = %s", (report_id,))
        rules = cursor.fetchall()

        print(rules)
        if rules == []: # ! if rules are empty make parent expired
            print('no rules found')
            cursor.execute("UPDATE nodes SET status = 'expired' WHERE node_id = %s", (parent_node_id,))
            postgres.commit()

            return jsonify(message='rules deleted successfully')

        print(f'rules are: {rules}')

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
        print(rules)
        if rules == []: # ! if rules are empty make parent expired
            print('no rules found')
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
# * node rules

# * post
@app.route("/api/v1/post/node/rules/<id>", methods=["POST"])
def post_node_rules(id):
    try:
        print(id)
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

# * get specific rule
@app.route("/api/v1/get/node/rules/<id>", methods=["GET"])
def get_specific_node_rule(id):
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select * from node_rules where parent_node_id = %s ", (id))
        specified_node_rules = cursor.fetchall()
        return jsonify(specified_node_rules), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        postgres.close()


# @app.route("/api/v1/nodes/<node_id>/rules/evaluate", methods=["GET"])
# def evaluate_node_rules(node_id):
#     try:
#         postgres = get_db_connection()
#         cursor = postgres.cursor(cursor_factory=RealDictCursor)

#         # Fetch the child nodes
#         cursor.execute("SELECT * FROM nodes WHERE parent = %s", (node_id,))
#         child_nodes = cursor.fetchall()

#         # Fetch the rules for this node
#         cursor.execute("SELECT * FROM node_rules WHERE parent_node_id = %s", (node_id,))
#         rules = cursor.fetchall()

#         for rule in rules:
#             # Here, 'conditions' is already stored as a JSON string in the database,
#             # so no need to use json.loads() if it's already a valid JSON object
#             conditions = rule['conditions']
#             action = rule['action']
            
#             # Evaluate the conditions
#             if evaluate_conditions(child_nodes, conditions):  # Directly pass conditions
#                 # Perform the action based on the rule
#                 if action == "make parent up":
#                     cursor.execute("UPDATE nodes SET status = 'up' WHERE node_id = %s", (node_id,))
#                 elif action == "make parent down":
#                     cursor.execute("UPDATE nodes SET status = 'down' WHERE node_id = %s", (node_id,))
#                 elif action == "make parent critical":
#                     cursor.execute("UPDATE nodes SET status = 'critical' WHERE node_id = %s", (node_id,))
#                 # Add more actions as needed

#         postgres.commit()
#         return jsonify({"message": "Rules evaluated successfully"}), 200

#     except Exception as e:
#         print(e)
#         return jsonify({"error": str(e)}), 500  
#     finally:
#         cursor.close()
#         postgres.close()

# # Recursive condition evaluation function
# def evaluate_conditions(child_nodes, conditions):

#     node_statuses = {node['node_id']: node['status'] for node in child_nodes}

#     def evaluate_condition_group(condition_group):
#         operator = condition_group['operator']
#         group_conditions = condition_group['conditions']
        
#         results = []
#         for cond in group_conditions:
#             # Check if the current condition is a nested condition group
#             if 'operator' in cond and 'conditions' in cond:
#                 # Recursively evaluate nested condition group
#                 results.append(evaluate_condition_group(cond))
#             else:
#                 # Evaluate a simple condition
#                 node_id = cond['node_id']
#                 expected_status = cond['status']
#                 actual_status = node_statuses.get(node_id)

#                 # Compare statuses
#                 if actual_status is not None:
#                     results.append(actual_status == expected_status)
#                 else:
#                     results.append(False)  # If node_id not found, consider it as failed condition

#         # Apply the operator
#         if operator == "AND":
#             return all(results)
#         elif operator == "OR":
#             return any(results)

#     # Evaluate the top-level conditions
#     return evaluate_condition_group(conditions[0])



if __name__ == "__main__":
    app.run(debug=True, port=80) #TODO when app is ready, change debug to false.

