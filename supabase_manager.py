import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = None

if url and key:
    supabase = create_client(url, key)

def upload_file(bucket_name, file_path, remote_path):
    """
    Upload a local file to a Supabase bucket.
    Returns the public URL of the uploaded file.
    """
    if not supabase:
        print("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_KEY.")
        return None

    with open(file_path, 'rb') as f:
        response = supabase.storage.from_(bucket_name).upload(
            path=remote_path,
            file=f,
            file_options={"cache-control": "3600", "upsert": "true"}
        )
    
    # Get public URL
    public_url = supabase.storage.from_(bucket_name).get_public_url(remote_path)
    return public_url

def upload_bytes(bucket_name, file_bytes, remote_path, content_type="application/pdf"):
    """
    Upload bytes directly to a Supabase bucket.
    """
    if not supabase:
        return None

    supabase.storage.from_(bucket_name).upload(
        path=remote_path,
        file=file_bytes,
        file_options={"cache-control": "3600", "upsert": "true", "content-type": content_type}
    )
    
    return supabase.storage.from_(bucket_name).get_public_url(remote_path)
