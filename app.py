
from flask import Flask, jsonify, redirect, render_template, request
from psycopg2.extras import RealDictCursor
import psycopg2  
from constants import DB_HOST, DB_NAME, DB_USER, DB_PASS 

app = Flask(__name__)

def get_db_connection():
    postgres = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return postgres

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

@app.route("/api/v1/post", methods=["POST"])
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


@app.route("/api/v1/get/reports/distinct", methods=["GET"])
def distinct_reports():
    try:
        postgres = get_db_connection()
        cursor = postgres.cursor(cursor_factory=RealDictCursor)

        cursor.execute("select distinct(report_id), title, description from reports where parent is null");
        response = cursor.fetchall()
        
        return jsonify(response)
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  
    finally:
        cursor.close()
        postgres.close()


@app.route("/api/v1/post/reports", methods=["POST"]) 
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

        if parent and response != None:
            return jsonify('Cannot create report: a node with the same parent already exists')
        elif parent:

            cursor.execute("SELECT * FROM reports WHERE report_id = %s", (report_id,))
            response = cursor.fetchall()

            if response:
                for report in response:
                    if report['parent'] is not None and report['parent'] != parent:
                        return jsonify({'message': 'Report can be associated only to 1 parent'}), 400

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
    
# * rules
@app.route("/get_rules", methpds=["GET"])
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



@app.route("/post_rules", methods=["GET"])
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
    app.run(debug=True, port=80)

