# Advance RAG
# - query transformation
# - Routing
# - Query Construction
# - Indexing 
# - Retrival
# - Generation


# query transformation
# - user query => user don't know waht he want so he search anything that have multiple meaning so output will be some with mutliple meaning not accurate op so we can not make good RAG with user query so what if we transalte user input into waht he want(what he ask/what he want to know(our work to decide)) then RAG will be good.(improve user prompt)
# - Rewrite query(Rag fusion, multi query)
# - Parallar query(fan out) retrival -> give user query to llm for rewrite say hey you are an helpful ai assistant who rewrite query based on users qurty in 3-4 ways then search simillarity from pinecone/quadrant db for all those query it will give output you have to cobine and remove duplicate op from that result. now result and user query(what he ask) give it to llm
# - Resiprocate Rank Fusion => we rank output that comes from pinecone/quadrant db,  baki jo parallar me kiya hai wohi process hai
# - query decomposition -> user ki query ko break down kardo uske baad chain of thought(prompting) karna hai (3-4) step me uske baad har step pe pincone db me similarity search karke uske op to user query ke sath llm me daldo jo result aayega usko next step me add karke use step ke liye same procees for all step then get all o/p for all steps and give that to llm with user query
# - step back prompting
# - HyDE = Hypothetical document enbedding -> 