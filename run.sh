python3 english_to_narsese_with_yago_categories.py < input.txt | python3 ./opennars-for-applications/concept_net_narsese.py | ./opennars-for-applications/NAR shell InspectionOnExit | python3 ./opennars-for-applications/concept_usefulness_filter.py 10 | python3 ./opennars-for-applications/concepts_to_graph.py
#cypher-shell -a bolt://localhost:7687 "call apoc.import.graphml('memory.graphml', {})"
