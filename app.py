
from flask import Flask, jsonify, redirect, render_template, request
from psycopg2.extras import RealDictCursor
import psycopg2  
from constants import DB_HOST, DB_NAME, DB_USER, DB_PASS 

app = Flask(__name__)

def get_db_connection(): # * config
    postgres = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return postgres

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(message='Undefined route, 404'), 404

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
@app.route("/get_rules", methods=["GET"]) # TODO: make rules be evaluated each time a new report is being posted.
def get_rules():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        return jsonify('undefined')

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()


@app.route("/post_rules", methods=["POST"])
def post_rules():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        return jsonify('undefined')

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()


if __name__ == "__main__":
    app.run(debug=True, port=80) #TODO when app is ready, change debug to false.

