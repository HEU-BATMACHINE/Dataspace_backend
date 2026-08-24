from fastapi import APIRouter, File, UploadFile
from fastapi import HTTPException, Query, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
import httpx
from base64 import b64encode
import os
import pandas.io.sql as sqlio
from io import StringIO

from app.routers.timescaledb import get_connection

router = APIRouter(tags=["fuseki"], prefix="/fuseki")

if "FUSEKI_URL" in os.environ:
    FUSEKI_URL = os.environ.get("FUSEKI_URL")
    FUSEKI_USERNAME = os.environ.get("FUSEKI_USERNAME")
    FUSEKI_PASSWORD = os.environ.get("FUSEKI_PASSWORD")

    # Encode the username and password for Basic Auth
    encoded_credentials = b64encode(f"{FUSEKI_USERNAME}:{FUSEKI_PASSWORD}".encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/sparql-results+json",
    }


# http://localhost:8000/query
default_sparql = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 25"
@router.get("/{dataset}/query")
async def query_sparql(dataset: str, sparql_query: str = Query(default=default_sparql)):
    """
    Endpoint to query the Fuseki triple store with Basic Auth.
    """
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/sparql-results+json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FUSEKI_URL}/{dataset}/sparql",
            params={"query": sparql_query},
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=400, detail="Query failed")


@router.post("/{dataset}/update")
async def update_sparql(dataset:str, update: str):
    """
    Endpoint to update the Fuseki triple store.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FUSEKI_URL}/{dataset}/update",
            data={"update": update},
            headers=headers,
        )
        if response.status_code == 200:
            return {"detail": "Update successful"}
        else:
            return {"detail": "Update failed"}


@router.post("/{dataset}/upload")
async def upload_file(
    dataset: str,
    file: UploadFile = File(...),
):
    """
    Endpoint to upload various RDF file formats to the Fuseki triple store.
    """
    if file.filename is None:
        raise HTTPException(
            status_code=400,
            detail="Filename not found. Upload failed."
        )

    supported_formats = [".ttl", ".rdf", ".jsonld", ".nt", ".xml"]
    if not any(file.filename.endswith(format) for format in supported_formats):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only Turtle (.ttl), RDF (.rdf), JSON-LD (.jsonld), N-Triples (.nt), or XML (.xml) files are allowed.",
        )

    # Read the uploaded file content
    contents =  file.file.read()

    # Determine content type based on file extension
    content_type = "text/turtle"  # default to Turtle
    if file.filename.endswith((".jsonld")):
        content_type = "application/ld+json"
    elif file.filename.endswith((".nt")):
        content_type = "application/n-triples"
    elif file.filename.endswith((".xml")):
        content_type = "application/rdf+xml"
    # Send the file contents to Fuseki
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FUSEKI_URL}/{dataset}/data",
            data=contents,
            headers={"Content-Type": content_type, **headers},
        )
        if response.status_code == 200:
            return {"detail": f"{file.filename} uploaded successfully"}
        else:
            raise HTTPException(status_code=400, detail="Upload failed")


@router.post("/{dataset}/entity")
async def query_sparql_entity(dataset: str,
                              entities: list[str] = Body(default=["<https://w3id.org/netzsch/public/ontology#netzsch_6d437f40_8ce9_50fd_8696_d4a6cc4b5dc6>"]),
                              ):
    """
    Return all tableId connected to entity in fuseki
    """
    entities_str = " ".join(entities)
    sparql_query = """
        SELECT DISTINCT ?entity
            WHERE {
                VALUES ?entity { """ + entities_str + """ } .

                { ?inst ?pred ?entity . }
                UNION
                { ?inst ?entity ?objc . }
                UNION
                { ?entity ?pred ?objc . }
        }"""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FUSEKI_URL}/{dataset}/sparql",
            params={"query": sparql_query},
            headers=headers,
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="SPARQL query failed. "+sparql_query)

        bindings = response.json()["results"]["bindings"]
        if len(bindings) != len(entities):
            raise HTTPException(status_code=400, detail="Entity does not exist in fuseki. "+sparql_query )


    entities_str = " ".join(entities)
    sparql_query = """
PREFIX csvw: <http://www.w3.org/ns/csvw#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?columnName WHERE {
    VALUES ?entity { """ + entities_str + """ } .
    ?table csvw:tableSchema ?schema ;
           dc:title ?tableName .

    ?schema csvw:columns ?column .

    ?column csvw:name ?columnName ;
            csvw:propertyUrl ?entity .
    
}"""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FUSEKI_URL}/{dataset}/sparql",
            params={"query": sparql_query},
            headers=headers,
        )

        if response.status_code == 200:
            bindings = response.json()["results"]["bindings"]
            tableIds = []
            for elem in bindings:
                tableIds.append(elem["columnName"]["value"])
            return tableIds
        else:
            raise HTTPException(status_code=400, detail=f"Query failed. {response.text}. "+sparql_query)


#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
@router.post("/{dataset}/entity_data", response_class = PlainTextResponse)
async def query_entity_data(request:Request, dataset: str,
                              entity: str = Body(default="<https://w3id.org/netzsch/public/ontology#netzsch_6d437f40_8ce9_50fd_8696_d4a6cc4b5dc6>"),
                              dbname: str = Body(default="bedrock"),
                              limit:int=Body(default=50)
                              ):
    
    """
    Return data connected to one entity in fuseki
    Get all data from table in database, sorted by time, in CSV.
    Returns:
    - output_csv(str): Table as a CSV file in string format
    """

    endpoint_url = str(request.url_for("query_sparql_entity",dataset=dataset))
    print(endpoint_url)
    
    body = [ entity ] #{ "entities" : [ entity ] ,
    #"dataset": dataset}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint_url,json=body,
            headers=headers,
        )

        if response.status_code != 200:
            print(response.json())
            raise HTTPException(status_code=400, detail="SPARQL query failed")
        
        print("***testing entity_data\n",response.json())
        tableId = response.json()[0]
        print("***tableId \n",tableId)
        #if len(bindings) != len(entities):
        #    raise HTTPException(status_code=400, detail="Entity does not exist in fuseki")


    sql_query = f"SELECT * FROM {tableId} ORDER BY time DESC LIMIT {limit}" 

    # Save response as Pandas dataframe
    conn = get_connection(dbname)
    df = sqlio.read_sql_query(sql_query, conn)

    # Save response to csv, then to str
    outputIO = StringIO()
    df.to_csv(outputIO, index=False)
    output_csv = outputIO.getvalue()

    return output_csv
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------


@router.post("/{dataset}/init")
async def initialize_graph(dataset : str):
    """
    Endpoint to initialize the Fuseki triple store with the dataset and default triples.
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FUSEKI_URL}/$/datasets",
            params={"dbType": "mem", "dbName": dataset},
            headers=headers,
        )
        if response.status_code == 409:
            return {"detail": "Dataset already exists. Consider deleting it first."}

    headers_local = headers.copy()
    headers_local['Content-Type'] = 'text/turtle;charset=utf-8'

    for fnames in ["fuseki/table_channels.ttl", "fuseki/netzsch_public.ttl", "fuseki/emmo-inferred-1.0.0-beta7.ttl"]:
        with open(fnames) as file:
            data = file.read()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FUSEKI_URL}/{dataset}/data",
                data=data,
                headers=headers_local,
            )

            if response.status_code != 200:
                return {"detail": "Initialization failed", "status_code": response.status_code}

    return {"detail": "Initialization successful"}

@router.get("/{dataset}/visualize", response_class=HTMLResponse)
async def visualize(dataset: str):
    """
    Endpoint to visualize the knowledge graph in Fuseki
    """
    from pyvis.network import Network
    from rdflib.graph import Graph
    from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

    # Retrieve graph as turtle
    async with httpx.AsyncClient() as client:
        headers_local = { "Authorization": f"Basic {encoded_credentials}", }
        response = await client.get(
            f"{FUSEKI_URL}/{dataset}/get",
            headers=headers_local,
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Query failed")

    # Get NetworkX graph
    g = Graph()
    g = g.parse(data=response.text)
    G = rdflib_to_networkx_multidigraph(g, edge_attrs=lambda s, p, o: {"key": p, "title":p})

    groups = {}
    max_group_id = 0
    for (_, node) in enumerate(G.nodes()):
        try:
            group, label = str(node).split("#")
        except ValueError:
            # Literals cannot be split
            group = "literal"
            label = str(node)

        if group not in groups:
            max_group_id += 1
            groups[group] = max_group_id
        id = groups[group]

        G.nodes[node]["group"] = id
        G.nodes[node]["label"] = label
        G.nodes[node]["title"] = str(node)

    # Generate HTML
    net = Network(cdn_resources="in_line", directed=True)
    net.from_nx(G)
    net.generate_html()
    return net.html
    


@router.delete("/{dataset}")
async def delete_graph(dataset : str):
    """
    Endpoint to delete a Fuseki dataset
    """

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{FUSEKI_URL}/$/datasets/{dataset}",
            headers=headers,
        )
        if response.status_code == 200:
            return {"detail": "Dataset successfully deleted"}
        else:
            raise HTTPException(status_code=400, detail="Deletion failed")
