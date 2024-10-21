def evaluate_rules(condition, action, nodes_and_their_status):
    # Extract operator and conditions
    operator = condition['operator']
    node_conditions = condition['conditions']

    # Create a mapping of node_id to their status from nodes_and_their_status
    node_status_map = {node['node_id']: node['status'] for node in nodes_and_their_status}

    # Debug prints
    print(f"Operator: {operator}")
    print(f"Node Status Map: {node_status_map}")
    print(f"Node Conditions: {node_conditions}")

    if operator == 'AND':
        # Check if all conditions are met using bracket notation
        result = all(node_id in node_status_map and node_status_map[node_id] == expected_status 
                     for node_id, expected_status in node_conditions.items())
        print("All conditions met:", result)
        return result

    elif operator == 'OR':
        # Check if any condition is met using bracket notation

        test = [node_id in node_status_map and node_status_map[node_id] == expected_status 
                     for node_id, expected_status in node_conditions.items()]
        


        second = [node_id in node_status_map and node_status_map[node_id] == expected_status 
                     for node_id, expected_status in node_conditions.items()]

        
        print('test is ')
        print(test)
        result = any(node_id in node_status_map and node_status_map[node_id] == expected_status 
                     for node_id, expected_status in node_conditions.items())
        print("At least one condition met:", result)
        return result

# Example usage
condition = {
    'operator': 'OR',  # Change to 'OR' to test the other case
    'conditions': {5: 'down', 4: 'up', 8: 'up', 7: 'up'}
}

action = None  # Not used in this example
nodes_and_their_status = [
    {'status': 'up', 'node_id': 5},
    {'status': 'up', 'node_id': 4},
    {'status': 'down', 'node_id': 7},
    {'status': 'up', 'node_id': 8}
]

evaluate_rules(condition, action, nodes_and_their_status)
