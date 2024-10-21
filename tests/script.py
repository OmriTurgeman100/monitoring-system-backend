node_status = [{'node': 'up'}, {'node': 'up'}, {'node': 'down'}]

# Check if all nodes are 'up'
all_up = all(node['node'] == 'up' for node in node_status)

any_up = any(item['node'] == 'up' for item in node_status)
print(any_up)

for item in node_status:
    print(item['node'])

test = [0, 1, 2, 3, 4]

numbers = (num for num in test)

for item in numbers:
    print(item)


array = any(item['node'] == 'up' for item in node_status)
print(array)




