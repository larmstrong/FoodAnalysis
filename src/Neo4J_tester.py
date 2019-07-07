
# This script is for initial testing with Neo4J before it is more deeply embedded into the project.
# 1. Get a basic graph operational. CHECK.
# 2. Successfully query data from the graph.
# 3. Investigate the optional schema model.

#--------------------------------------------------------------------------------------------------
# Load Libraries

from py2neo import Database, Graph
from py2neo.data import Node, Relationship
from py2neo.database import Transaction

# Open the food graph DB
#food_db = Database(uri="bolt://localhost:7687")
food_gr = Graph(auth=('neo4j', 'food'), host='localhost', port="7687", scheme='bolt')
print(food_gr.database.name)

##--------------------------------------------------------------------------------------------------
# Create basic relationships

# Query the whole DB
x = food_gr.run('MATCH (r) RETURN r').to_data_frame()
x

# Show how many nodes were retrieved.
print(len(x))

# Delete the current Graph
food_gr.delete_all()

tx = food_gr.begin()

mac_n_cheese = Node("Recipe", name="Macaroni and Cheese")
tx.create(mac_n_cheese)
pasta = Node("Ingredient", name="elbow macaroni")
tx.create(pasta)
cheese = Node("Ingredient", name="shredded cheddar")
tx.create(cheese)
milk = Node("Ingredient", name="milk")
tx.create(milk)

rels = {
    "r1": Relationship(pasta, 'IS_USED_IN', mac_n_cheese)
}

tx.create(rels["r1"])
tx.commit()
print(food_gr.exists(rels["r1"]))

print(rels['r1'])
