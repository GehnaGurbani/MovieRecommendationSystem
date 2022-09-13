import pandas as pd
import numpy as np
import sys
from py2neo import Graph
from flask import Flask, render_template, request, g, jsonify,Response

app = Flask(__name__)

g  = Graph("bolt://localhost:7687", auth=("neo4j", "Gehna@1502"))

@app.route("/")
def hello():
    return render_template('hello.html')

@app.route("/usernodesearch", methods = ['POST'])
def post():
    name = request.form['name']
    task_name = request.form['task_name']
    sub_task_name = request.form['sub_task_name']
    task_class = request.form['task_class']

    query = ""
    if name == '':
        if task_name == '':
            if sub_task_name== '':
                if task_class== '':
                    message = "Enter at least one field out of the four"
                    return render_template('visualise.html',result = message)
                else: #Only Movie_id is given (return pure content based sim in genre)
                    query = """MATCH p=(m:Movie{title:'"""+str(task_class)+"""'})-[r:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(rec:Movie)
                               UNWIND nodes(p) as nodes UNWIND relationships(p) as rels 
                               RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels 
                               """
                results = g.run(query).data()
                m_count = 1
                g_count =0
                movie_to_id = {}
                genre_to_id = {}
                genres = []
                movies = []
                cnt =1


                for r in results:
                        
                    for m in r['nodes']:
                            movie = m['title']
                            movies.append((m_count,movie))  
                            movie_to_id[movie] = m_count
                            m_count+=1 
                            if (cnt == 2):
                                genre = m['genre']
                                genres.append((g_count,genre))
                                genre_to_id[genre] = g_count 
                            cnt+=1

                    rels = []
                    for r in results:
                        rel = r['rels']
                        for relation in rel:
                            src = relation.start_node['title']
                            src = movie_to_id[src]
                            tgt_name = relation.end_node['genre']
                            tgt = genre_to_id[tgt_name]
                            rels.append((src,tgt)) 
           
                nodes = movies + genres

                print(results, flush = True)
                return render_template('visualise.html', nodes=nodes, edges=rels)
            else: #year#(pure content based year sim)
                if task_class == '':
                    query  = """MATCH p=(m:Movie)-[:RELEASED_IN]->(y:release_date{rel_date: '"""+str(sub_task_name)+"""'})<-[:RELEASED_IN]-(rec:Movie)
                               UNWIND nodes(p) as nodes UNWIND relationships(p) as rels 
                               RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels
                               """
                    results = g.run(query).data() 
                    m_count = 1
                    y_count = 0
                    movie_to_id = {}
                    year_to_id = {}
                    years = []
                    movies = []
                    cnt =2 
                 
                    for r in results:
                            
                        for m in r['nodes']:
                                movie = m['title']
                                movies.append((m_count,movie))  
                                movie_to_id[movie] = m_count
                                m_count+=1
                                if (cnt == 2):
                                    rel_year = m['rel_date']
                                    years.append((y_count,rel_year))
                                    year_to_id[rel_year] = y_count 
                                    cnt +=1

                        rels = []
                        for r in results:
                            rel = r['rels']
                            for relation in rel:
                                src = relation.start_node['title']
                                src = movie_to_id[src]
                                tgt_name = relation.end_node['rel_date']
                                tgt = year_to_id[tgt_name]
                                rels.append((src,tgt)) 
               
                    nodes = movies + years

                    print(results, flush = True)
                    return render_template('visualise.html', nodes = nodes, edges = rels)
                else: 
                    query = """MATCH p = (n:Table)-[:Depends_on* {sub_task_name : '"""+str(sub_task_name)+"""',task_class : '"""+str(task_class)+"""'}]-()  
                    UNWIND nodes(p) as nodes UNWIND relationships(p) as rels RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
        else: #genre #(pure content based on genre)
            if sub_task_name == '':
                if task_class == '':
                    query = """MATCH p=(m:Movie)-[:HAS_GENRE]->(a:Genre{genre: '"""+str(task_name)+"""'})<-[:HAS_GENRE]-(rec:Movie)
                               UNWIND nodes(p) as nodes UNWIND relationships(p) as rels 
                               RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels
                            """
                    print(task_name)
                    results = g.run(query).data()
                    m_count = 1
                    g_count =0
                    movie_to_id = {}
                    genre_to_id = {}
                    genres = []
                    movies = []
                    cnt =1
                    for r in results:
                            
                        for m in r['nodes']:
                                movie = m['title']
                                movies.append((m_count,movie))  
                                movie_to_id[movie] = m_count
                                m_count+=1 
                                if (cnt == 2):
                                    genre = m['genre']
                                    genres.append((g_count,genre))
                                    genre_to_id[genre] = g_count 
                                cnt+=1

                        rels = []
                        for r in results:
                            rel = r['rels']
                            for relation in rel:
                                src = relation.start_node['title']
                                src = movie_to_id[src]
                                tgt_name = relation.end_node['genre']
                                tgt = genre_to_id[tgt_name]
                                rels.append((src,tgt)) 
               
                    nodes = movies + genres

                    print(results, flush = True)
                    return render_template('visualise.html', nodes=nodes, edges=rels)
                else: 
                    query = """MATCH p = (n:Table)-[:Depends_on* {task_name : '"""+str(task_name)+"""',task_class : '"""+str(task_class)+"""'}]-()  
                    UNWIND nodes(p) as nodes UNWIND relationships(p) as rels RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
            
            else:
                if task_class == '': 
                    query = """MATCH p = (n:Table)-[:Depends_on* {sub_task_name : '"""+str(sub_task_name)+"""',task_name : '"""+str(task_name)+"""'}]-() 
                     UNWIND nodes(p) as nodes UNWIND relationships(p) as rels RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
                else: 
                    query = """MATCH p = (n:Table)-[:Depends_on* {task_name : '"""+str(task_name)+"""',sub_task_name : 
                    '"""+str(sub_task_name)+"""',task_class : '"""+str(task_class)+"""'}]-()  UNWIND nodes(p) as nodes UNWIND relationships(p) as rels
                     RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
    else: #name
        if task_name ==  '':
            if sub_task_name == '':
                if task_class == '':
                    query = """MATCH (u1:User {user_id:'"""+str(name)+"""'})-[r:HAS_RATED]->(m:Movie)
                            WITH u1, avg(r.rating) AS u1_mean
 
                                MATCH (u1)-[r1:HAS_RATED]->(m:Movie)<-[r2:HAS_RATED]-(neighbour)
                                WITH u1, u1_mean, neighbour, collect({r1: r1, r2: r2}) AS ratings
                                WHERE size(ratings) > 10
                                 
                                MATCH (neighbour)-[r:HAS_RATED]->(m:Movie)
                                WITH u1, u1_mean, neighbour, avg(r.rating) AS neighbour_mean, ratings
                                 
                                UNWIND ratings AS r
                                 
                                WITH sum( (r.r1.rating-u1_mean) * (r.r2.rating-neighbour_mean) ) AS nom,
                                     sqrt( sum( (r.r1.rating - u1_mean)^2) * sum( (r.r2.rating - neighbour_mean) ^2)) AS denom,neighbour_mean,
                                     u1, neighbour WHERE denom <> 0
                                WITH u1, neighbour, nom/denom AS pearson,neighbour_mean
                                MATCH (neighbour)-[r:HAS_RATED]->(m:Movie) 
                                WHERE r.rating > neighbour_mean
                                MATCH p = (neighbour)-[r:HAS_RATED]->(m:Movie)            
                                           

                                WHERE not (u1)-[:HAS_RATED]->(m)                      
                                 

                                WITH p, u1, m,r,neighbour, pearson        
                                 
                                UNWIND relationships(p) as rels
                                 
                                 
                                RETURN u1,neighbour, COLLECT(m)[0..2] as recos ,collect(DISTINCT rels)[0..2] as rels,pearson
                                 
                                ORDER BY pearson DESC LIMIT 5


                            """
                    results = g.run(query).data()        
                    cnt = 1
                    neighbours = []
                    m_count = 1
                    movie_to_id = {}
                    user_to_id = {}
                    movies = []
                    for r in results:
                        if (cnt == 1):
                            user_node = r['u1']['user_id']
                        neighbour_number  = r['neighbour']['user_id']
                        
                        neighbour_gender = r['neighbour']['gender']
                        user_to_id[int(neighbour_number)] = m_count
                    
                        neighbours.append((m_count,neighbour_number))
                        m_count+=1
                        for m in r['recos']:
                            movie = m['title']
                            movies.append((m_count,movie))  
                            movie_to_id[movie] = m_count
                            m_count+=1   
                        cnt +=1
                    
                    rels = []
                    for r in results:
                        rel = r['rels']
                        for relation in rel:
                            src = int(relation.start_node['user_id'])
                            src = user_to_id[src]
                            tgt_name = relation.end_node['title']
                            tgt = movie_to_id[tgt_name]
                            rels.append((src,tgt)) 
           
                    nodes = neighbours + movies
                    print(results, flush = True)

                else:
                    query = """MATCH p = (n:Table)-[:Depends_on* {name : '"""+str(name)+"""',task_class : '"""+str(task_class)+"""'}]-() 
                     UNWIND nodes(p) as nodes UNWIND relationships(p) as rels RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
            else:
                if task_class == '':
                    query = """MATCH p = (n:Table)-[:Depends_on* {sub_task_name : '"""+str(sub_task_name)+"""',name : '"""+str(name)+"""'}]-()  
                    UNWIND nodes(p) as nodes UNWIND relationships(p) as rels RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
                else :
                    query = """MATCH p = (n:Table)-[:Depends_on* {name : '"""+str(name)+"""',sub_task_name : 
                    '"""+str(sub_task_name)+"""',task_class : '"""+str(task_class)+"""'}]-()  UNWIND nodes(p) as nodes UNWIND relationships(p) as rels
                     RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
        else:
            if sub_task_name == '':
                if task_class == '':
                    query = """MATCH p = (n:Table)-[:Depends_on* {name : '"""+str(name)+"""',task_name : '"""+str(task_name)+"""'}]-()
                      UNWIND nodes(p) as nodes UNWIND relationships(p) as rels RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
                else:
                    query = """MATCH p = (n:Table)-[:Depends_on* {name : '"""+str(name)+"""',task_name : '"""+str(task_name)+"""',task_class : '"""+str(task_class)+"""'}]-()
                      UNWIND nodes(p) as nodes UNWIND relationships(p) as rels RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
            else:
                query = """MATCH p = (n:Table)-[:Depends_on* {name : '"""+str(name)+"""',task_name : 
                '"""+str(task_name)+"""',sub_task_name : '"""+str(sub_task_name)+"""',task_class : '"""+str(task_class)+"""'}]-()  UNWIND nodes(p) as nodes 
                UNWIND relationships(p) as rels RETURN collect(DISTINCT nodes) as nodes, collect(DISTINCT rels) as rels """
    
    results = g.run(query).data()
    return render_template('visualise.html', nodes = nodes, edges = rels)

            








