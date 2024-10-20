import os
from github import Github
import chromadb
from semchunk import chunkerify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def fetch_github_code(repo_url):
    g = Github(os.getenv('GITHUB_TOKEN'))
    # print(os.getenv('GITHUB_TOKEN'))
    # exit()

    repo = g.get_repo(repo_url.split('github.com/')[-1])
    code_files = []

    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            try:
                code_files.append({
                    'name': file_content.name,
                    'path': file_content.path,
                    'content': file_content.decoded_content.decode('utf-8')
                })
            except UnicodeDecodeError:
                print(f"Skipping file {file_content.path} (unable to decode)")
            except Exception as e:
                print(f"Error processing file {file_content.path}: {str(e)}")

    return code_files

def fetch_filenames(repo_url):
    g = Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_repo(repo_url.split('github.com/')[-1])
    return [file.name for file in repo.get_contents("") if file.type == "dir"]

def split_into_chunks(code, chunk_size=1000):
    chunker = chunkerify(lambda text: len(text.split()), chunk_size)
    return chunker(code)

def store_in_chromadb(chunks, collection_name='repodb'):
    client = chromadb.PersistentClient(path="./chromadb")
    collection = client.create_collection(name=collection_name)

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk['content']],
            metadatas=[{'file_name': chunk['name'], 'file_path': chunk['path']}],
            ids=[f"chunk_{i}"]
        )

    return collection

def retrieve_relevant_chunks(query, collection, n_results=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results

def generate_non_contextual_code(query, repo_url):
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    prompt = f"""Given the following context and query, generate relevant code:

    Name of the repo: {repo_url.split('/')[-1]}

    These are the names of the files in the repo:
    {fetch_filenames(repo_url)}

    Query: {query}

    Generated Code:
    """

    response = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-70b-8192",
    )

    print(response.choices[0].message.content)
    return response.choices[0].message.content

def fetch_and_store_code_chunks(repo_url):
    code_files = fetch_github_code(repo_url)

    chunks = []
    for file in code_files:
        file_chunks = split_into_chunks(file['content'])
        chunks.extend([{'name': file['name'], 'path': file['path'], 'content': chunk} for chunk in file_chunks])

    # # Store chunks in ChromaDB
    collection = store_in_chromadb(chunks, 'repodb')
    return collection
    # exit()


def rag_code_generation(collection, non_contextual_code):
    # client = chromadb.Client()
    # collection_name = "code_chunks"
    # collection = client.get_collection(name=collection_name)
    # Retrieve relevant chunks
    # collection = 'code_chunks'
    relevant_chunks = retrieve_relevant_chunks(non_contextual_code, collection)
    codes = [doc for doc_list in relevant_chunks['documents'] for doc in doc_list]

    # print(codes)
    exit()

    # Generate code using Groq API
    combined_context = "\n".join(codes)
    prompt = f"""Given the following code context and query, generate only code in triple backticks:

    Name of the repo: {repo_url.split('/')[-1]}

    These are the names of the files in the repo:
    {fetch_filenames(repo_url)}

    Code Context:
    {combined_context}

    Query: {query}

    Generated Code:
    """
    
    response = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-70b-8192",
    )

    print(response.choices[0].message.content)
    return response.choices[0].message.content

    # generated_code = "testing"
    # return generated_code




repo_url = "https://github.com/SushaanthSrinivasan/Terminal-Todo-List-Manager"
# collection = fetch_and_store_code_chunks(repo_url)

collection_name = "repodb"
client = chromadb.PersistentClient(path="./chromadb")
collection = client.get_collection(name=collection_name)

query = "implement task export feature"
non_contextual_code = generate_non_contextual_code(query, repo_url)

generated_code = rag_code_generation(collection, non_contextual_code)
print(generated_code)
